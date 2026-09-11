"""Add Pico controllers to the original keyboard. Run once on the original files."""
from pathlib import Path
import uuid,copy,json
from sexpr import *
import pcbnew as p
p.SwigPyIterator.next=p.SwigPyIterator.__next__
def uid(): return str(uuid.uuid4())
s=parse(Path('keyboard.kicad_sch').read_text()); root=one(s,'uuid')[1]
b=p.LoadBoard('keyboard.kicad_pcb')
if any(f.GetReference()=='U1' for f in b.GetFootprints()): raise SystemExit('Controllers already present')
def net(name):
 n=b.FindNet(name)
 if n is None: n=p.NETINFO_ITEM(b,name); b.Add(n)
 return n
libs=one(s,'lib_symbols')
def getlib(name):
 lib,part=name.split(':'); a=parse(Path('/usr/share/kicad/symbols/'+lib+'.kicad_sym').read_text())
 sym=copy.deepcopy(next(x for x in children(a,'symbol') if x[1]==part)); sym[1]=name
 if not any(x[1]==name for x in children(libs,'symbol')): libs.append(sym)
 return sym
def add(name,ref,value,fp,at,boardat,mapping):
 lib=getlib(name); x,y=at; u=uid()
 inst=parse(f'(symbol (lib_id "{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{u}"))')
 for key,val,dy in [('Reference',ref,-7),('Value',value,-4),('Footprint',fp,0)]:
  inst.append(parse(f'(property "{key}" "{val}" (at {x} {y+dy} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if key=='Footprint' else '')+'))'))
 occupied=set()
 for sub in children(lib,'symbol'):
  for pin in children(sub,'pin'):
   num=one(pin,'number')[1]; pa=one(pin,'at'); px=round(x+float(pa[1]),4); py=round(y-float(pa[2]),4)
   inst.append(parse(f'(pin "{num}" (uuid "{uid()}"))'))
   if (px,py) in occupied: continue
   occupied.add((px,py))
   if num in mapping:
    ang={'0':0,'180':180,'90':90,'270':270}[str(pa[3])]
    s.append(parse(f'(global_label "{mapping[num]}" (shape bidirectional) (at {px} {py} {ang}) (effects (font (size 1 1)) (justify {"left" if ang in [0,90] else "right"})) (uuid "{uid()}"))'))
   else: s.append(parse(f'(no_connect (at {px} {py}) (uuid "{uid()}"))'))
 inst.append(parse(f'(instances (project "keyboard" (path "/{root}" (reference "{ref}") (unit 1))))'))
 s.append(inst)
 flib,fn=fp.split(':'); f=p.FootprintLoad('/usr/share/kicad/footprints/'+flib+'.pretty',fn)
 f.SetReference(ref);f.SetValue(value);f.SetUuid(p.KIID(u));f.SetPath(p.KIID_PATH('/'+root+'/'+u));b.Add(f);f.SetPosition(p.VECTOR2I(round(boardat[0]*1e6),round(boardat[1]*1e6)))
 for pad in f.Pads():
  if pad.GetNumber() in mapping: pad.SetNet(net(mapping[pad.GetNumber()]))
 return f
pinmap={0:'1',1:'2',2:'4',3:'5',4:'6',5:'7',6:'9',7:'10',8:'11',9:'12',10:'14',11:'15',12:'16',13:'17',14:'19'}
for i,(side,x,rows,cols) in enumerate([('L',143,[0,1,2,3,9],range(8)),('R',282,[8,7,6,5,4],range(8,16))],1):
 mapping={pinmap[gp]:f'ROW{r}' for gp,r in zip(range(2,7),rows)}
 mapping.update({pinmap[gp]:f'COL{c}' for gp,c in zip(range(7,15),cols)})
 mapping.update({'1':side+'_TX','2':side+'_RX','39':side+'_VSYS','40':side+'_VBUS','36':side+'_3V3'})
 mapping.update({str(k):side+'_GND' for k in [3,8,13,18,23,28,33,38]})
 add('MCU_Module:RaspberryPi_Pico','U'+str(i),'RaspberryPi_Pico','Module:RaspberryPi_Pico_Common_THT',(292.1,66.04+(i-1)*119.38),(x,-5),mapping)
# Keep each physical half electrically separate; the removable cable is documented separately.
s.append(parse(f'(text "Pico 1 / RP2040: GP0 TX, GP1 RX; GP2..6 rows; GP7..14 columns.\\nFour-wire cable: VSYS, GND, left TX to right RX, left RX to right TX.\\nConnector footprint pending identification of purchased part.\\nVSYS is supplied through the Pico onboard VBUS Schottky diode; never join 3V3 outputs." (at 250.19 256.54 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid()}"))'))
Path('keyboard.kicad_sch').write_text(dump(s)+'\n')
# Remove redundant vias drilled directly into D2's plated pad.
d2=next(f for f in b.GetFootprints() if f.GetReference()=='D2')
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA) and any(t.GetPosition()==pad.GetPosition() for pad in d2.Pads()): b.Remove(t)
# Board outlines retain every existing switch location and add an inner controller bay.
polys=[[(-14,-10),(169,-10),(169,130),(141,137),(92,110),(80,71),(-14,71)],[(276,-10),(453,-10),(453,71),(352,71),(348,106),(298,135),(276,120)]]
for poly in polys:
 for a,c in zip(poly,poly[1:]+poly[:1]):
  d=p.PCB_SHAPE();d.SetShape(p.SHAPE_T_SEGMENT);d.SetStart(p.VECTOR2I(int(a[0]*1e6),int(a[1]*1e6)));d.SetEnd(p.VECTOR2I(int(c[0]*1e6),int(c[1]*1e6)));d.SetLayer(p.Edge_Cuts);d.SetWidth(50000);b.Add(d)
p.SaveBoard('keyboard.kicad_pcb',b)
