from pathlib import Path
import uuid
from sexpr import *
s=parse(Path('keyboard.kicad_sch').read_text())
def uid():return str(uuid.uuid4())
# Connector ground is a physical connection, unlike unused module AGND.
for side,y in [('L',66.04),('R',185.42)]:
 x=360.68
 for nc in list(children(s,'no_connect')):
  at=one(nc,'at')
  if abs(float(at[1])-x)<.001 and abs(float(at[2])-y)<.001:s.remove(nc)
 s.append(parse(f'(global_label "{side}_GND" (shape bidirectional) (at {x} {y} 180) (effects (font (size 1 1)) (justify right)) (uuid "{uid()}"))'))
for lab in children(s,'global_label'):
 at=one(lab,'at');x,y=float(at[1]),float(at[2]); nx,ny=x,y
 if abs(x-269.24)<.001 or abs(x-360.68)<.001:
  nx=x-5.08;angle=180;justify='right'
 elif str(lab[1]) in ['L_VSYS','R_VSYS'] and abs(x-287.02)<.001:
  ny=y-7.62;angle=90;justify='left'
 elif str(lab[1]) in ['L_GND','R_GND'] and abs(x-292.1)<.001:
  ny=y+5.08;angle=270;justify='right'
 else:continue
 at[1:]=[Atom(str(round(nx,4))),Atom(str(round(ny,4))),Atom(str(angle))]
 one(one(lab,'effects'),'justify')[1]=Atom(justify)
 s.append(parse(f'(wire (pts (xy {x} {y}) (xy {round(nx,4)} {round(ny,4)})) (stroke (width 0) (type default)) (uuid "{uid()}"))'))
Path('keyboard.kicad_sch').write_text(dump(s)+'\n')
