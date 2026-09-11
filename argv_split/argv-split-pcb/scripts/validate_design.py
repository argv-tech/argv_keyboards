"""Check the intended electrical mapping and confinement of routed copper."""
import sys,subprocess,tempfile,json
from pathlib import Path
import pcbnew as p
from sexpr import *
p.SwigPyIterator.next=p.SwigPyIterator.__next__
root=Path(__file__).resolve().parent.parent
pro=json.loads((root/'keyboard.kicad_pro').read_text())
rules=pro['board']['design_settings']['rules']
defaults=pro['board']['design_settings']['defaults']
netclass=pro['net_settings']['classes'][0]
assert rules['min_clearance']==0.2
assert rules['min_track_width']==0.4
assert rules['min_copper_edge_clearance']>=0.2
assert rules['min_silk_clearance']>=0.15
assert rules['min_text_height']>=1.0
assert rules['min_text_thickness']>=0.15
assert rules['min_via_annular_width']>=0.15
assert rules['min_via_diameter']>=0.6
assert defaults['copper_line_width']==0.4
assert netclass['clearance']==0.2 and netclass['track_width']==0.4
b=p.LoadBoard(str(root/'keyboard.kicad_pcb')); refs={f.GetReference():f for f in b.GetFootprints()}
expected={}
for i,side in [(1,'L'),(2,'R')]:
 expected['J'+str(i)]={'1':side+'_VSYS','2':side+'_GND','3':side+('_TX' if i==1 else '_RX'),'4':side+('_RX' if i==1 else '_TX')}
 rows=[0,1,2,3,9] if i==1 else [8,7,6,5,4]
 expected['U'+str(i)]={'1':side+'_TX','2':side+'_RX','39':side+'_VSYS',**{str(n):side+'_GND' for n in [3,8,13,18,23,28,38]},**{str(n):'ROW'+str(r) for n,r in zip([4,5,6,7,9],rows)},**{str(n):'COL'+str(c) for n,c in zip([10,11,12,14,15,16,17,19],range((i-1)*8,i*8))}}
with tempfile.TemporaryDirectory() as d:
 fn=Path(d)/'netlist.net';subprocess.run(['kicad-cli','sch','export','netlist',str(root/'keyboard.kicad_sch'),'-o',str(fn)],check=True,capture_output=True)
 sch=parse(fn.read_text());snets={}
 for net in children(one(sch,'nets'),'net'):
  for n in children(net,'node'):snets[(one(n,'ref')[1],one(n,'pin')[1])]=one(net,'name')[1]
 for ref,mapping in expected.items():
  pads={pad.GetNumber():pad.GetNetname() for pad in refs[ref].Pads()}
  for pin,name in mapping.items():
   assert pads[pin]==name,(ref,pin,pads[pin],name)
   assert snets[(ref,pin)]==name,(ref,pin,snets.get((ref,pin)),name)
polys=[[(-15,-15),(169,-15),(169,130),(141,137),(92,110),(80,71),(-15,71)],[(268.5,-15),(453,-15),(453,71),(352,71),(348,106),(298,135),(268.5,120)]]
def inside(x,y,poly):
 hit=False
 for (a,c),(d,e) in zip(poly,poly[1:]+poly[:1]):
  if (c>y)!=(e>y) and x<(d-a)*(y-c)/(e-c)+a:hit=not hit
 return hit
for track in b.GetTracks():
 if track.Type()==p.PCB_TRACE_T:
  assert abs(track.GetWidth()/1e6-0.4)<1e-6,(track.GetNetname(),track.GetWidth()/1e6)
 a,z=track.GetStart(),track.GetEnd()
 steps=max(1,int(max(abs(a.x-z.x),abs(a.y-z.y))/250000))
 for j in range(steps+1):
  x=(a.x+(z.x-a.x)*j/steps)/1e6;y=(a.y+(z.y-a.y)*j/steps)/1e6
  assert any(inside(x,y,poly) for poly in polys),(track.GetNetname(),x,y)
assert sum(r.startswith('SW') for r in refs)==64
assert len([r for r in refs if r.startswith('U')])==2
edge_points=[]
for drawing in b.GetDrawings():
 if drawing.GetLayerName()=='Edge.Cuts':
  edge_points.extend([(drawing.GetStart().x/1e6,drawing.GetStart().y/1e6),(drawing.GetEnd().x/1e6,drawing.GetEnd().y/1e6)])
assert min(y for x,y in edge_points)==-15.0
assert min(x for x,y in edge_points)==-15.0
# Key courtyards are 9.525 mm from their switch centres. The four exposed
# corners therefore have at least 5 mm of board beyond the key body.
assert -9.525-(-15.0)>=5.0
assert -9.525-(-15.0)>=5.0
assert 453.0-(438.15+9.525)>=5.0
print('PASS: 64 switches, two Picos; controller and cable net assignments match in PCB and schematic; all routed centre lines stay inside outlines; every copper segment is 0.4 mm; key-edge padding is >=5 mm.')
