#!/usr/bin/env python3
"""Offline, real OrcaSlicer 2.3.2 audit. Never submit test files to a printer.
The GUI export knows preset types from its manifest. CLI scratch copies need
metadata type and from=system for standalone flat presets (2.3.2 CLI compares
empty user inherits instead of the printer's actual name). No slicing values
or compatibility names are altered by this adapter. Extracted reusable checks; this module does not repair or rewrite profiles.
"""
import argparse, hashlib, json, math, os, re, subprocess, zipfile
from pathlib import Path

NUMBER=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)'
WORD=re.compile(r'([A-Z])('+NUMBER+r')')


def test_stl(path):
    triangles=[]
    for x in (140,160):
        v=[(x,140,0),(x+6,140,0),(x+6,146,0),(x,146,0),
           (x,140,5),(x+6,140,5),(x+6,146,5),(x,146,5)]
        for face in [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
                     (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]:
            triangles.append('facet normal 0 0 0\n outer loop\n'+''.join(
                '  vertex %s %s %s\n'%v[i] for i in face)+' endloop\nendfacet\n')
    path.write_text('solid m300\n'+''.join(triangles)+'endsolid m300\n')


def scalar(v):return v[0] if isinstance(v,list) else v

def override(f,p,key):
    v=scalar(f.get('filament_'+key,['nil']))
    return scalar(p[key]) if v=='nil' else v


def inspect_gcode(g, f, p, effective):
    errors=[];lines=g.splitlines();commands=[];retracts=[];unretracts=[];hops=[]
    feed=None;relative=False;layer_z=None;positive_xy_e=0;max_acc=0;old_accel=False
    for line in lines:
        if line.startswith(';Z:'):layer_z=float(line[3:])
        code=line.split(';',1)[0].strip()
        if not code:continue
        command=code.split()[0];commands.append(code)
        if command=='M83':relative=True
        if command=='M82':relative=False;errors.append('Unexpected absolute E mode')
        if command in ('G0','G1'):
            words={k:float(v) for k,v in WORD.findall(code)}
            if 'F' in words:feed=words['F']/60.
            e=words.get('E',0.)
            if e and not relative:errors.append('E motion without M83')
            if e<0:retracts.append({'mm':-e,'speed_mm_s':feed,'line':line})
            elif e>0 and not any(k in words for k in ('X','Y','Z')):
                unretracts.append({'mm':e,'speed_mm_s':feed,'line':line})
            elif e>0:positive_xy_e+=1
            if 'normal lift Z' in line and 'Z' in words and layer_z is not None:
                hops.append(words['Z']-layer_z)
        for match in re.finditer(r'\bACCEL=('+NUMBER+')',code):max_acc=max(max_acc,float(match[1]))
        if command=='M204':
            m=re.search(r'\bS('+NUMBER+')',code)
            if m:max_acc=max(max_acc,float(m[1]))
        if 'ACCEL_TO_DECEL=' in code:old_accel=True
    starts=[l for l in commands if l.startswith('START_PRINT ')]
    ends=[l for l in commands if l=='END_PRINT']
    start=starts[0] if len(starts)==1 else ''
    expected='START_PRINT EXTRUDER_TEMP=%s BED_TEMP=%s MESH=AUTO'%(f['nozzle_temperature_initial_layer'][0],f['hot_plate_temp_initial_layer'][0])
    if start!=expected:errors.append('Wrong start temperatures: '+repr(starts)+' expected '+expected)
    if len(ends)!=1:errors.append('END_PRINT missing or duplicated')
    if not positive_xy_e:errors.append('No extrusion along XY path')
    length=float(override(f,p,'retraction_length'));speed=float(override(f,p,'retraction_speed'))
    despeed=float(override(f,p,'deretraction_speed')) or speed
    hop=float(override(f,p,'z_hop'))
    if not retracts or not unretracts:errors.append('Missing retract/unretract')
    for vals,target_l,target_f,label in [(retracts,length,speed,'retract'),(unretracts,length,despeed,'unretract')]:
        if any(abs(v['mm']-target_l)>1e-4 or v['speed_mm_s'] is None or abs(v['speed_mm_s']-target_f)>1e-4 for v in vals):
            errors.append('Wrong '+label+' length/speed')
    if not hops or any(abs(z-hop)>1e-4 for z in hops):errors.append('Incorrect Z-hop')
    if max_acc>700 or not max_acc:errors.append('Acceleration outside profile envelope')
    if old_accel:errors.append('Removed Klipper ACCEL_TO_DECEL parameter present')
    forbidden={'G10','G11','M201','M203','M205','M82'}
    if forbidden.intersection(l.split()[0] for l in commands):errors.append('Unsupported/unwanted command emitted')
    flow=float(f['filament_flow_ratio'][0])
    if float(scalar(effective.get('filament_flow_ratio',['nan'])))!=flow:errors.append('Flow ratio not loaded')
    if float(scalar(effective.get('filament_diameter',['nan'])))!=1.75:errors.append('Filament diameter wrong')
    if float(scalar(effective.get('nozzle_diameter',['nan'])))!=.4:errors.append('Nozzle diameter wrong')
    before=commands[:commands.index(start)] if start in commands else commands
    if any(re.match(r'M(?:104|109|140|190)\b',l) for l in before):errors.append('Duplicate heating before START_PRINT')
    temperatures=[l for l in commands if re.match(r'M(?:104|109|140|190)\b',l)]
    normal_bed=float(f['hot_plate_temp'][0]);first_bed=float(f['hot_plate_temp_initial_layer'][0])
    if normal_bed!=first_bed and not any(re.fullmatch(r'M140 S'+re.escape(str(int(normal_bed))),l) for l in temperatures):
        errors.append('Normal-layer bed temperature not emitted')
    return dict(errors=errors,start=start,end=ends,retraction_mm=length,retraction_speed_mm_s=speed,
        deretraction_speed_mm_s=despeed,retractions=len(retracts),unretractions=len(unretracts),
        retract_examples=[x['line'] for x in retracts[:2]],unretract_examples=[x['line'] for x in unretracts[:2]],
        z_hop_mm=hop,verified_hops=len(hops),positive_xy_extrusions=positive_xy_e,
        flow_ratio=flow,max_volumetric_speed=float(f['filament_max_volumetric_speed'][0]),
        max_emitted_acceleration=max_acc,old_accel_to_decel=old_accel,
        temperature_commands=temperatures,pre_start_commands=before,
        command_names=sorted(set(l.split()[0] for l in commands)))

