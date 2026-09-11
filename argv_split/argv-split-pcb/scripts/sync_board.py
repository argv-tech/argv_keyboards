"""Apply exported schematic net names to board pads before routing."""
import pcbnew as p
from sexpr import *
p.SwigPyIterator.next=p.SwigPyIterator.__next__
b=p.LoadBoard('keyboard.kicad_pcb'); s=parse(open('/tmp/keyboard.net').read()); refs={f.GetReference():f for f in b.GetFootprints()}
for n in children(one(s,'nets'),'net'):
 name=one(n,'name')[1]; bn=b.FindNet(name)
 if bn is None:bn=p.NETINFO_ITEM(b,name);b.Add(bn)
 for node in children(n,'node'):
  f=refs.get(one(node,'ref')[1]);num=one(node,'pin')[1]
  if f:
   for pad in f.Pads():
    if pad.GetNumber()==num: pad.SetNet(bn)
# Move two diodes away from switch holes, matching the positions in the other rows.
for ref,xy in [('D60',(423.25,5.66)),('D61',(447.0625,5.66))]:refs[ref].SetPosition(p.VECTOR2I(int(xy[0]*1e6),int(xy[1]*1e6)))
# Reroute from clean connectivity after relocating diodes and adding controllers.
for t in b.GetTracks():b.Remove(t)
p.SaveBoard('keyboard.kicad_pcb',b)
print('export',p.ExportSpecctraDSN(b,'/tmp/keyboard.dsn'))
