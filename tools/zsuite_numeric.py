#!/usr/bin/env python3
"""Restricted IL data interpreter, not an application runner.
Reads only configuration constructors and a string-pool decoder. No proprietary
assembly execution, GUI/font export, network access, printer access or flashing.
Requires dnfile 0.18.0 and dncil 1.0.2. Inputs must match the pinned vendor DLLs.
"""
import argparse, collections, hashlib, json, struct
from pathlib import Path
import dnfile
from dncil.cil.body.reader import read_method_body_from_bytes

VERSIONS={
 'classic':dict(sha='54a01c41318b1d30fc7822f6c974409ca8a9c90ec467b42e6c657131da4bf40a',
  decoder=0x58a3,owner='majjwkrHrdo1JAFjv5p',pool='cb1azttdr7G',decode_name='gjoazyZf1pX',
  ctor_fields=['H6OazdS3Eqj','zhFazkURGh7'],cipher='HKnazrXs2PQ',mix='EKdazpUxPpj',
  true='DpJOBV7JD6Te6LX73j',false='uaMP9Xqy4udZx3BwfE',
  loaders=[(0xce3,None)],skip=['DUouAs5wUrnvP','EMRazwNcEVC','cjtD3lhVXu478FRUu4']),
 'beta4':dict(sha='2b42e567aaee3c7370f8339aebafad0625d27726859231bf40ffaa93d0bdf0b2',
  decoder=0x46d3,owner='hfnNJx2et0MZ5gGlyo0',pool='pot07uiFxhh',decode_name='wqC07UtBuCK',
  ctor_fields=['KOi07OjXBPl','kPV07alMEhG'],cipher='rqO07CagraM',mix='vMD078Qqo2b',
  true='EbQ4xjPDUMmBuenlVg',false='SYYp1wDwgMwsHFwN69',
  loaders=[(0xf5b,'M200Plus'),(0xfc9,'M300Plus'),(0xf93,'M300Dual'),(0xf34,'Inventure'),(0xf12,'Endureal')],
  skip=['TtrVK7SlOXnPj'])}
WRAPPERS={'gB7R5pTqc6wfvdchVe':'Type.GetTypeFromHandle','Ukmg3HJu7AufamYNcC':'IntrospectionExtensions.GetTypeInfo',
 'yNlvWGMdRdZS2guydL':'Assembly.GetManifestResourceStream','nw9elJeBCNYPm64W8t':'get_BaseStream',
 'whTXOGaD0a0tt6SNDV':'set_Position','srGsKEKW7o5kewPNBM':'get_Length','Eywc57ktBK1EAtGXY8':'ReadBytes',
 'qBQrryYKiVMZovXR9d':'Dispose','fa1cO6ug7YyeclDPnD':'BitConverter.ToInt32','SoaRWo22CQ8q3SPBlX':'System.Array.Copy',
 'rbiISsm9P3rjg2L8fH':'get_Unicode','RlyH9CCJ5yM95mKqiD':'Encoding.GetString'}

def i32(v):
 v=int(v)&0xffffffff
 return v-0x100000000 if v&0x80000000 else v

def compressed(data,pos):
 a=data[pos];pos+=1
 if a&0x80==0:return a,pos
 if a&0xc0==0x80:return ((a&0x3f)<<8)|data[pos],pos+1
 return ((a&0x1f)<<24)|int.from_bytes(data[pos:pos+3],'big'),pos+3

class Reader:
 def __init__(self,path,version):
  self.c=VERSIONS[version];self.version=version
  raw=Path(path).read_bytes();self.sha=hashlib.sha256(raw).hexdigest()
  if self.sha!=self.c['sha']:raise ValueError('Unreviewed vendor DLL SHA256')
  self.p=dnfile.dnPE(data=raw,fast_load=True);self.p.parse_data_directories(directories=[14])
  self.owner={m.row_index:str(t.TypeNamespace)+'.'+str(t.TypeName) for t in self.p.net.mdtables.TypeDef for m in t.MethodList}
  self.methods={str(m.Name):i for i,m in enumerate(self.p.net.mdtables.MethodDef.rows,1) if self.owner[i].endswith(self.c['owner'])}
  self.cache={};self.fields={self.c['pool']:b''};self.singleton={'Elements':[]}
  self.resources={};base=self.p.get_offset_from_rva(self.p.net.struct.ResourcesRva)
  for r in self.p.net.mdtables.ManifestResource:
   name=str(r.Name)
   if name in ['4D4XNQrTNBbypsWj19.6FMF0ge0qtKX1HJZiA','3pP86bPjqPEg0KrANH.wBigCp1p5Bm43r0ZoC']:
    off=base+r.Offset;n=struct.unpack_from('<I',raw,off)[0];self.resources[name]=raw[off+4:off+4+n]
  self.vm(self.c['decoder'],[0]);data=self.fields[self.c['pool']];at=0;self.strings={}
  while at<len(data):
   n=struct.unpack_from('<I',data,at)[0]
   if n%2 or at+4+n>len(data):raise ValueError('Malformed string table')
   self.strings[at]=data[at+4:at+4+n].decode('utf-16-le');at+=4+n
 def body(self,n):
  if n not in self.cache:self.cache[n]=read_method_body_from_bytes(self.p.get_data(self.p.net.mdtables.MethodDef.rows[n-1].Rva,2000000)).instructions
  return self.cache[n]
 def resolve(self,token):
  v=token.value;tab=v>>24;row=v&0xffffff
  if tab==6:return self.owner[row]+'.'+str(self.p.net.mdtables.MethodDef.rows[row-1].Name)
  if tab==4:return str(self.p.net.mdtables.Field.rows[row-1].Name)
  if tab==10:
   r=self.p.net.mdtables.MemberRef.rows[row-1];o=r.Class.row
   return str(getattr(o,'TypeNamespace',''))+'.'+str(getattr(o,'TypeName',''))+'.'+str(r.Name)
  return str(token)
 def signature(self,tok):
  tab=tok>>24;row=tok&0xffffff
  if tab==43:
   m=self.p.net.mdtables.MethodSpec.rows[row-1].Method
   return self.signature((6 if m.table.name=='MethodDef' else 10)<<24|m.row_index)
  r=(self.p.net.mdtables.MethodDef if tab==6 else self.p.net.mdtables.MemberRef).rows[row-1]
  sig=r.Signature.value;pos=1
  if sig[0]&0x10:_,pos=compressed(sig,pos)
  n,pos=compressed(sig,pos)
  return str(r.Name),n,bool(sig[0]&0x20),sig[pos]!=1,tab,row
 def vm(self,n,args,data_mode=False):
  ins=self.body(n);positions={i.offset:j for j,i in enumerate(ins)};s=[];loc=[None if data_mode else 0]*80;pc=0;steps=0
  while pc<len(ins):
   i=ins[pc];pc+=1;steps+=1;op=i.opcode.name;a=i.operand
   if steps>30000000:raise RuntimeError('IL step bound')
   def idx():return int(op.rsplit('.',1)[-1]) if op.rsplit('.',1)[-1].isdigit() else a.index
   if op in ['nop','volatile.','readonly.']:pass
   elif op.startswith('ldc.i4'):s.append(int(a) if op in ('ldc.i4','ldc.i4.s') else (-1 if op.endswith('m1') else int(op[-1])))
   elif op in ['ldc.r4','ldc.r8','ldc.i8']:s.append(a)
   elif op.startswith('ldarg'):s.append(args[idx()])
   elif op.startswith('ldloc'):s.append(loc[idx()])
   elif op.startswith('stloc'):loc[idx()]=s.pop()
   elif op=='ldnull':s.append(None)
   elif op=='ldstr':s.append(self.p.net.user_strings.get(a.value&0xffffff).value)
   elif op=='ldtoken':s.append(a)
   elif op=='ldsfld':s.append(self.fields.get(self.resolve(a),0))
   elif op=='stsfld':self.fields[self.resolve(a)]=s.pop()
   elif op=='ldfld':s.append(s.pop()[self.resolve(a)])
   elif op=='stfld':v=s.pop();s.pop()[self.resolve(a)]=v
   elif op=='ldlen':s.append(len(s.pop()))
   elif op=='newarr':s.append(bytearray(s.pop()))
   elif op.startswith('stelem'):v=s.pop();j=s.pop();arr=s.pop();arr[j]=v&255 if op.endswith('i1') else v
   elif op.startswith('ldelem'):j=s.pop();s.append(s.pop()[j])
   elif op=='dup':s.append(s[-1])
   elif op=='pop':s.pop()
   elif op in ['add','sub','mul','div','div.un','rem','rem.un','and','or','xor','shl','shr','shr.un']:
    b=s.pop();v=s.pop()
    if op=='add':v+=b
    elif op=='sub':v-=b
    elif op=='mul':v*=b
    elif op in ('div','rem'):v=int(v/b) if op=='div' else v-int(v/b)*b
    elif op in ('div.un','rem.un'):v=(v&0xffffffff)//(b&0xffffffff) if op=='div.un' else (v&0xffffffff)%(b&0xffffffff)
    elif op=='and':v&=b
    elif op=='or':v|=b
    elif op=='xor':v^=b
    elif op=='shl':v<<=(b&31)
    elif op=='shr':v>>=(b&31)
    else:v=(v&0xffffffff)>>(b&31)
    s.append(v if data_mode else i32(v))
   elif op in ('not','neg'):s.append(i32(~s.pop() if op=='not' else -s.pop()))
   elif op.startswith('conv.'):
    if not data_mode:v=s.pop();s.append(v&255 if op=='conv.u1' else i32(v))
   elif op in ('ceq','cgt','cgt.un','clt','clt.un'):
    b=s.pop();v=s.pop();s.append(int(v==b) if op=='ceq' else int(v>b) if 'cgt' in op else int(v<b))
   elif op=='switch':
    k=s.pop()
    if 0<=k<len(a):pc=positions[a[k]]
   elif op.startswith(('br','beq','bne','bge','bgt','ble','blt','leave')):
    go=True
    if op.startswith('brtrue'):go=bool(s.pop())
    elif op.startswith('brfalse'):go=not s.pop()
    elif op.startswith(('beq','bne','bge','bgt','ble','blt')):
     b=s.pop();v=s.pop()
     if '.un' in op and isinstance(v,int) and isinstance(b,int):v&=0xffffffff;b&=0xffffffff
     go=v==b if op.startswith('beq') else v!=b if op.startswith('bne') else v>=b if op.startswith('bge') else v>b if op.startswith('bgt') else v<=b if op.startswith('ble') else v<b
    if go:pc=positions[a]
   elif op=='ret':return s.pop() if s else None
   elif op in ('call','callvirt','newobj'):
    full=self.resolve(a);short=full.rsplit('.',1)[-1]
    if data_mode:
     nm,argc,instance,returns,table,row=self.signature(a.value)
     actual=s[-argc:] if argc else []
     if argc:del s[-argc:]
     this=s.pop() if instance and op!='newobj' else None;result=None
     if nm==self.c['decode_name']:result=self.strings[actual[0]]
     elif nm in self.c['skip']:pass
     elif op=='newobj':
      if full=='...ctor' and argc==1:result=actual[0]
      else:
       result={'_type':full.rsplit('..ctor',1)[0],'_args':actual}
       if any(t in full for t in ['Printer.','PrintingProfile.','NozzleDiameter.','LayerThickness.','Quality.','Infill.']):result['Elements']=[]
     elif nm=='get_Instance':result=self.singleton
     elif nm.startswith('get_'):
      key=nm[4:]
      if key not in this:this[key]=[] if key=='Elements' else {}
      result=this[key]
     elif nm.startswith('set_'):this[nm[4:]]=actual[0]
     elif nm=='Add':this.append(actual[0])
     elif table==6:result=self.vm(row,([this] if instance else [])+actual,True)
     else:raise RuntimeError('Unsupported data call '+full)
     if returns or op=='newobj':s.append(result)
    else:
     nm=WRAPPERS.get(short,full)
     if short==self.c['true']:s.append(True)
     elif short==self.c['false']:s.append(False)
     elif short in self.c['skip']:pass
     elif nm.endswith(('Type.GetTypeFromHandle','IntrospectionExtensions.GetTypeInfo','get_Assembly')):pass
     elif nm.endswith('Assembly.GetManifestResourceStream'):name=s.pop();s.pop();s.append(self.resources[name])
     elif nm=='System.IO.BinaryReader..ctor' or nm.endswith('get_BaseStream'):pass
     elif nm.endswith('get_Length'):s.append(len(s.pop()))
     elif nm.endswith('set_Position'):s.pop();s.pop()
     elif nm.endswith('ReadBytes'):count=s.pop();s.append(s.pop()[:count])
     elif nm.endswith('Dispose'):s.pop()
     elif nm.endswith('BitConverter.ToInt32'):j=s.pop();s.append(struct.unpack_from('<i',s.pop(),j)[0])
     elif nm.endswith('System.Array.Copy'):length=s.pop();j=s.pop();dst=s.pop();k=s.pop();src=s.pop();dst[j:j+length]=src[k:k+length]
     elif nm.endswith('get_Unicode'):s.append('utf-16-le')
     elif nm.endswith('Encoding.GetString'):length=s.pop();j=s.pop();arr=s.pop();encoding=s.pop();s.append(bytes(arr[j:j+length]).decode(encoding))
     elif op=='newobj' and nm.endswith(self.c['owner']+'..ctor'):
      iv=s.pop();key=s.pop();s.append(dict(zip(self.c['ctor_fields'],[key,iv])))
     elif short==self.c['cipher']:value=s.pop();obj=s.pop();s.append(self.vm(self.methods[short],[obj,value]))
     elif short==self.c['mix']:value=s.pop();obj=s.pop();s.append(self.vm(self.methods[short],[obj,value]))
     else:raise RuntimeError('Unsupported decoder call '+nm)
   else:raise RuntimeError('Unsupported IL '+op+' in '+hex(n))
 def records(self):
  for mid,name in self.c['loaders']:
   if name is None:self.vm(mid,[],True)
   else:
    obj={'_args':[name],'Elements':[]};self.vm(mid,[obj],True);self.singleton['Elements'].append(obj)
  rows=[]
  def flatten(obj,prefix=''):
   out={}
   for k,v in obj.items():
    if k.startswith('_') or k=='Elements':continue
    key=prefix+k
    if isinstance(v,dict):out.update(flatten(v,key+'.'))
    elif isinstance(v,(int,float,bool)):out[key]=v
   return out
  for p in self.singleton['Elements']:
   for m in p['Elements']:
    for n in m['Elements']:
     for l in n['Elements']:
      common=dict(source=self.version,printer=p['_args'][0],material=m['_args'][1],material_id=m['_args'][0],
       nozzle=float(n['_args'][1].split()[0].replace(',','.')),layer=float(l['_args'][1].split()[0].replace(',','.')))
      if self.version=='classic':
       for q in l['Elements']:
        for infill in q['Elements']:
         rows.append(dict(common,quality=q['_args'][1],infill=infill['_args'][1],values=flatten(infill['_args'][3])))
      else:rows.append(dict(common,quality='Default',infill='Standard',values=flatten(l['_args'][-1])))
  return rows

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--dll',required=True);ap.add_argument('--version',choices=VERSIONS,required=True);ap.add_argument('--out',required=True)
 a=ap.parse_args();reader=Reader(a.dll,a.version);rows=reader.records();p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(dict(source=a.version,dll_sha256=reader.sha,extraction='static restricted IL interpretation; no application execution',records=rows),indent=2)+'\n')
 print(json.dumps({'source':a.version,'records':len(rows),'M300_records':sum(r['printer']=='M300' for r in rows)}))
