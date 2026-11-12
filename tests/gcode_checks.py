"""Offline Orca 2.5 checks; never send generated test files to a printer."""
import math,re
NUMBER=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)'
WORDS=re.compile(r'([A-Z])('+NUMBER+r')')

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



def inspect(g,ef,p,q,f,pa):
 errors=[];ds=float(p['nozzle_diameter'][0]);h=float(q['layer_height'])
 for k,want in [('nozzle_diameter',ds),('filament_diameter',1.75),('layer_height',h),('filament_flow_ratio',float(f['filament_flow_ratio'][0]))]:
  if not math.isclose(float(scalar(ef.get(k,['nan']))),want,abs_tol=1e-6):errors.append('Effective '+k)
 for k in ['line_width','outer_wall_line_width','inner_wall_line_width','sparse_infill_line_width','top_surface_line_width']:
  if not math.isclose(float(scalar(ef.get(k,['nan']))),float(q[k]),abs_tol=1e-6):errors.append('Effective '+k)
 commands=[l.split(';',1)[0].strip() for l in g.splitlines() if l.split(';',1)[0].strip()]
 expected='START_PRINT EXTRUDER_TEMP=%s BED_TEMP=%s MESH=AUTO'%(f['nozzle_temperature_initial_layer'][0],f['hot_plate_temp_initial_layer'][0])
 starts=[i for i,l in enumerate(commands) if l.startswith('START_PRINT ')]
 if len(starts)!=1 or commands[starts[0]]!=expected:errors.append('START_PRINT temperatures')
 start=starts[0] if starts else -1
 if commands.count('END_PRINT')!=1:errors.append('END_PRINT')
 if any(re.match(r'M(?:104|109|140|190)\b',l) for l in commands[:max(0,start)]):errors.append('Duplicate preheat')
 if any(l.split()[0] in ['M82','G10','G11','M201','M203','M205'] or 'ACCEL_TO_DECEL=' in l for l in commands):errors.append('Unwanted firmware command')
 pas=[]
 for i,l in enumerate(commands):
  if l.startswith('SET_PRESSURE_ADVANCE '):
   m=re.search(r'\bADVANCE=('+NUMBER+')',l)
   if m:pas.append((i,float(m[1])))
 if not any(i<start and v==0 for i,v in pas):errors.append('PA reset before purge')
 if not any(i>start and abs(v-pa)<1e-7 for i,v in pas):errors.append('Filament PA after start')
 feed=None;relative=False;absolute=True;position=[None]*3;layer_z=None
 retracts=[];returns=[];hops=[];positive=0;maxacc=0;area_peak=0;area_fail=[]
 area_limit=4*ds*ds;filament_area=math.pi*1.75**2/4;small_e=ds*area_limit/filament_area
 for raw in g.splitlines():
  if raw.startswith(';Z:'):layer_z=float(raw[3:])
  code=raw.split(';',1)[0].strip()
  if not code:continue
  cmd=code.split()[0]
  if cmd=='M83':relative=True
  if cmd=='M82':relative=False
  if cmd=='G90':absolute=True
  if cmd=='G91':absolute=False
  if cmd=='M204':
   m=re.search(r'\bS('+NUMBER+')',code)
   if m:maxacc=max(maxacc,float(m[1]))
  for m in re.finditer(r'\bACCEL=('+NUMBER+')',code):maxacc=max(maxacc,float(m[1]))
  if cmd not in ['G0','G1','G92']:continue
  words={k:float(v) for k,v in WORDS.findall(code)};old=position[:]
  for idx,axis in enumerate('XYZ'):
   if axis in words:position[idx]=words[axis] if absolute or cmd=='G92' else old[idx]+words[axis] if old[idx] is not None else None
  if cmd=='G92':continue
  if 'F' in words:feed=words['F']/60
  e=words.get('E',0)
  if e and not relative:errors.append('Extrusion without M83')
  if e<0:retracts.append((-e,feed))
  elif e>0 and not any(k in words for k in 'XYZ'):returns.append((e,feed))
  elif e>0:
   positive+=1
   if all(v is not None for v in old[:2]+position[:2]):
    distance=math.hypot(position[0]-old[0],position[1]-old[1])
    if distance>1e-6:
     area=e*filament_area/distance;area_peak=max(area_peak,area)
     if area>area_limit*1.001 and e>small_e*1.001:area_fail.append(raw)
  if 'normal lift Z' in raw and 'Z' in words and layer_z is not None:hops.append(words['Z']-layer_z)
 length=float(override(f,p,'retraction_length'));extra=float(override(f,p,'retract_restart_extra'))
 speed=float(override(f,p,'retraction_speed'));back=float(override(f,p,'deretraction_speed')) or speed
 hop=float(override(f,p,'z_hop'))
 for values,want_length,want_speed,label in [(retracts,length,speed,'retract'),(returns,length+extra,back,'return')]:
  if not values:errors.append('No '+label)
  elif any(abs(l-want_length)>0.001 or v is None or abs(v-want_speed)>0.02 for l,v in values):errors.append('Wrong '+label+' amount/feed')
 if hop>0 and (not hops or any(abs(z-hop)>1e-4 for z in hops)):errors.append('Wrong Z hop')
 if not positive:errors.append('No printed extrusion')
 if not 0<maxacc<=700:errors.append('Acceleration outside host limits')
 if area_fail:errors.append('Nozzle-dependent extrusion cross-section exceeded')
 return dict(errors=sorted(set(errors)),start=expected,nozzle=ds,layer_height=h,pressure_advance_commands=pas,
  retraction_length=length,restart_extra=extra,retract_speed=speed,return_speed=back,retract_count=len(retracts),return_count=len(returns),
  z_hop=hop,hop_count=len(hops),positive_xy_extrusions=positive,max_acceleration=maxacc,
  peak_cross_section=area_peak,default_cross_section_limit=area_limit,cross_section_errors=area_fail[:3])

