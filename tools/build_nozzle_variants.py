#!/usr/bin/env python3
"""Reproducible M300 Classic nozzle variants. No host or MCU modifications.
Z-SUITE supports 0.4 mm for Classic; 0.3/0.6 below are custom Klipper presets,
NOT imported manufacturer profiles. Original 0.4 mm bundle stays byte-identical.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import zipfile
import io

ROOT = Path(__file__).resolve().parents[1]
BASE = 'profiles/Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer'
BASE_SHA = '3b60cd1ec9d324d5c2ed5a2aec7ced13560d13eff56734167bede1655e4333a4'
SPECS = {
    '0.3': {'normal': '0.32', 'inner': '0.34', 'first': '0.38', 'support': '0.3', 'min_layer': '0.09', 'max_layer': '0.24'},
    '0.6': {'normal': '0.63', 'inner': '0.68', 'first': '0.75', 'support': '0.6', 'min_layer': '0.15', 'max_layer': '0.45'},
}
NORMAL_WIDTHS = ('line_width', 'outer_wall_line_width', 'top_surface_line_width', 'internal_solid_infill_line_width')
INNER_WIDTHS = ('inner_wall_line_width', 'sparse_infill_line_width')
SOURCES = [
    {'url': 'https://support.zortrax.com/m-series-specification/', 'finding': 'M300 Classic: nozzle 0.4 mm; layers 0.09-0.29 mm.'},
    {'url': 'https://forum.zortrax.com/t/zortrax-m300-print-with-0-6-mm-nozzle/9671', 'finding': 'Zortrax support correction dated 2020-05-20: 0.6 not available for M300.'},
    {'url': 'https://forum.zortrax.com/t/there-is-no-possibility-to-choose-a-nozzle-except-0-4/12068', 'finding': 'Zortrax support dated 2023-07-04: no 0.6 M300 profiles; Plus/Dual differ.'},
    {'url': 'https://support.zortrax.com/m300-plus-specification/', 'finding': 'M300 Plus lists 0.3/0.4/0.6; not the Classic machine.'},
    {'url': 'https://support.zortrax.com/downloads/software/', 'finding': 'Classic M300 owners directed to Z-SUITE 2.32.0, not latest Z-SUITE 3.x.'},
    {'url': 'https://www.klipper3d.org/Config_Reference.html#extruder', 'finding': 'Host nozzle_diameter must describe installed nozzle; default max_extrude_cross_section=4*d*d.'},
]


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=4)+'\n').encode('utf-8')


def zipped(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    data = stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip():
            raise ValueError('Generated archive CRC failure')
    return data


def parity(old, new):
    assert set(old) == set(new), 'Schema keys changed'
    assert all(type(old[k]) is type(new[k]) for k in old), 'JSON field type changed'


def generate(root=ROOT):
    source = root/BASE
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA, 'Baseline changed: review variants before regenerating'
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        base = {n: json.loads(z.read(n)) for n in z.namelist()}
    manifest = base['bundle_structure.json']
    bp = base[manifest['printer_config'][0]]
    bq = base[manifest['process_config'][0]]
    assert len(bp) == 144 and len(bq) == 334
    outputs = {}
    record = {'revision': 'R4', 'date': '2026-11-11', 'machine': 'M300_CLASSIC',
              'zsuite_classic_nozzles_mm': [0.4], 'custom_klipper_nozzles_mm': [0.3, 0.6],
              'baseline_sha256': BASE_SHA, 'baseline_0p4_unchanged': True,
              'sources': SOURCES, 'variants': [], 'host_updated': False,
              'physical_test': False, 'gui_import_test': False}
    record['variants'].append({'diameter': '0.4', 'status': 'ZSUITE_CLASSIC_DIAMETER_CUSTOM_KLIPPER_PROCESS',
        'bundle': BASE, 'preset_root': 'presets', 'printer': bp['name'], 'process': bq['name'],
        'layer_height': '0.2', 'normal_line_width': '0.42', 'inner_line_width': '0.45',
        'initial_line_width': '0.5', 'support_line_width': '0.4',
        'min_layer_height': '0.09', 'max_layer_height': '0.29', 'materials': 18, 'sha256': BASE_SHA})
    for diameter, spec in SPECS.items():
        tag = diameter.replace('.', 'p')
        printer_name = f'Zortrax M300 {diameter} nozzle - Klipper custom'
        process_name = f'0.20mm Standard @{printer_name}'
        prefix = f'nozzle_presets/{tag}'
        p, q = copy.deepcopy(bp), copy.deepcopy(bq)
        p.update(name=printer_name, printer_settings_id=printer_name,
                 printer_variant=f'{diameter} nozzle', nozzle_diameter=[diameter],
                 min_layer_height=[spec['min_layer']], max_layer_height=[spec['max_layer']],
                 default_print_profile=process_name,
                 default_filament_profile=[f'Z-PLA Pro @Zortrax M300 {diameter}'])
        p['printer_notes'] = (
            f'CUSTOM KLIPPER PROFILE, NOT a Z-SUITE M300 Classic nozzle preset. Nozzle {diameter} mm, layer 0.20 mm. '
            f'Install a mechanically compatible nozzle and set Klipper [extruder] nozzle_diameter: {diameter} while idle. '
            'Importing this preset cannot change the host. Widths and min/max layer bounds are engineering starting settings, not OEM values. '
            'Keep M83, current motion/temperature limits and PA=0 until measured for this nozzle and filament. '
            'Recheck homing/mesh after nozzle replacement. PEEK remains catalog-only, not printable on this hardware.')
        p['file_start_gcode'] = (f'; M300 Classic custom Klipper nozzle {diameter} mm, layer 0.20 mm\n'
            f'; REQUIRED installed nozzle and Klipper [extruder] nozzle_diameter: {diameter}\n'
            '; Custom extension; not an OEM Z-SUITE Classic preset.\n')
        q.update(name=process_name, print_settings_id=process_name,
                 compatible_printers=[printer_name], layer_height='0.2', initial_layer_print_height='0.2',
                 filename_format=f'{{input_filename_base}}_M300_N{tag}_0p20_{{filament_preset[0]}}.gcode')
        for key in NORMAL_WIDTHS: q[key] = spec['normal']
        for key in INNER_WIDTHS: q[key] = spec['inner']
        q['initial_layer_line_width'] = spec['first']
        q['support_line_width'] = spec['support']
        q['notes'] = (f'M300 Classic custom {diameter} mm nozzle. One 0.20 mm process. '
                      'Explicit widths adapted from R3 geometry; no factory Z-SUITE claim. '
                      'Speeds, acceleration, raft layers, wall count, flow multipliers and temperature are unchanged. '
                      'A larger nozzle does not authorize a higher measured hotend flow capacity.')
        parity(bp, p); parity(bq, q)
        printer_path = f'printer/{printer_name}.json'
        process_path = f'process/{process_name}.json'
        bundle_files = {printer_path: encoded(p), process_path: encoded(q)}
        filaments = []
        for original_path in manifest['filament_config']:
            bf = base[original_path]
            f = copy.deepcopy(bf)
            material = bf['name'].split(' @Zortrax M300', 1)[0]
            f['name'] = f'{material} @Zortrax M300 {diameter}'
            f['filament_settings_id'] = [f['name']]
            f['filament_id'] = 'P'+hashlib.sha256(f['name'].encode()).hexdigest()[:8]
            f['compatible_printers'] = [printer_name]
            f['enable_pressure_advance'] = ['1']; f['pressure_advance'] = ['0']
            f['adaptive_pressure_advance'] = ['0']
            f['filament_notes'] = [bf['filament_notes'][0]+f' R4 CUSTOM {diameter} mm: '
                'separate nozzle-specific calibration record; PA/flow/retraction need print qualification. '
                'No automatic temperature offset or MVS increase. Nozzle diameter is not evidence of material compatibility.']
            parity(bf, f)
            path = f"filament/{f['name']}.json"
            bundle_files[path] = encoded(f); filaments.append(path)
        bm = {'bundle_id': f'_M300_KLIPPER_CUSTOM_N{tag}_0p20_R4_20261111',
              'bundle_type': 'printer config bundle', 'filament_config': filaments,
              'printer_config': [printer_path], 'printer_preset_name': printer_name,
              'process_config': [process_path], 'version': '00.00.00.00'}
        bundle_files['bundle_structure.json'] = encoded(bm)
        assert len(bundle_files) == 21 and len(filaments) == 18
        for name, data in bundle_files.items(): outputs[f'{prefix}/{name}'] = data
        bundle_path = f'profiles/Zortrax_M300_Classic_N{tag}_0p20_CUSTOM_R4.orca_printer'
        archive = zipped(bundle_files); outputs[bundle_path] = archive
        record['variants'].append({'diameter': diameter, 'status': 'CUSTOM_KLIPPER_NOT_ZSUITE_CLASSIC',
            'bundle': bundle_path, 'preset_root': prefix, 'printer': printer_name, 'process': process_name,
            'layer_height': '0.2', 'normal_line_width': spec['normal'], 'inner_line_width': spec['inner'],
            'initial_line_width': spec['first'], 'support_line_width': spec['support'],
            'min_layer_height': spec['min_layer'], 'max_layer_height': spec['max_layer'], 'materials': 18,
            'sha256': hashlib.sha256(archive).hexdigest()})
    outputs['NOZZLES.json'] = encoded(record)
    kit = {Path(BASE).name: raw, 'NOZZLES.json': outputs['NOZZLES.json'],
           'NOZZLES_R4_PL.md': (root/'docs/NOZZLES_R4_PL.md').read_bytes()}
    for variant in record['variants'][1:]: kit[Path(variant['bundle']).name] = outputs[variant['bundle']]
    outputs['profiles/M300_Orca_0p3_0p4_0p6_R4.zip'] = zipped(kit)
    # Keep original checksum entries; extend them with the new bundles and kit.
    sums = {}
    for line in (root/'SHA256SUMS').read_text().splitlines():
        if line.strip():
            digest, path = line.split('  ', 1); sums[path] = digest
    for path, data in outputs.items():
        if path.startswith('profiles/'): sums[path] = hashlib.sha256(data).hexdigest()
    outputs['SHA256SUMS'] = ''.join(f'{sums[p]}  {p}\n' for p in sorted(sums)).encode()
    return outputs, record


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true', help='Fail on any missing or stale output; do not write')
    args = ap.parse_args()
    outputs, record = generate()
    stale = []
    for name, data in outputs.items():
        target = ROOT/name
        if args.check:
            if not target.is_file() or target.read_bytes() != data: stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
    if stale: raise SystemExit('Stale generated nozzle files: '+', '.join(stale))
    print(json.dumps({'status': 'PASS', 'mode': 'check' if args.check else 'build',
        'variants': [x['diameter'] for x in record['variants']],
        'printer_count': 3, 'process_count': 3, 'material_entries': 54,
        'original_0p4_unchanged': True, 'generated_files': len(outputs)}))

if __name__ == '__main__': main()
