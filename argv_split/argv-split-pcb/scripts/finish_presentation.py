from pathlib import Path
import uuid
from sexpr import *
import pcbnew as p
p.SwigPyIterator.next=p.SwigPyIterator.__next__
s=parse(Path('keyboard.kicad_sch').read_text())
for lab in children(s,'global_label'):
 at=one(lab,'at')
 if str(lab[1]).startswith(('L_','R_')) and float(at[1])<330 and str(at[3]) in ['0','180']:
  at[3]=Atom('180' if str(at[3])=='0' else '0')
  one(one(lab,'effects'),'justify')[1]=Atom('right' if str(at[3])=='180' else 'left')
 if str(lab[1]).startswith(('L_','R_')) and float(at[1])>350:
  at[3]=Atom('180');one(one(lab,'effects'),'justify')[1]=Atom('right')
for inst in children(s,'symbol'):
 ref=next((x[2] for x in children(inst,'property') if x[1]=='Reference'),'')
 if ref in ['U1','U2']:
  x,y=map(float,one(inst,'at')[1:3])
  for prop in children(inst,'property'):
   if prop[1] in ['Reference','Value']:
    one(prop,'at')[2]=Atom(str(y-48.26+(3.81 if prop[1]=='Value' else 0)))
for t in children(s,'text'):
 t[1]='PICO 1 / RP2040 — FOUR-WIRE UART\nJ1/J2 pin 1: VSYS; pin 2: GND\nPin 3: left TX / right RX\nPin 4: left RX / right TX\nCable connects 1–1, 2–2, 3–3, 4–4.\nGP0 = TX; GP1 = RX (3.3 V logic).\nPower uses each Pico onboard USB diode.\nDo not connect the two 3V3 outputs.\nJ1/J2 are provisional 2.54 mm headers.\nConfirm purchased breakout dimensions.'
 one(t,'at')[1:3]=[Atom('335.28'),Atom('109.22')]
 one(one(one(t,'effects'),'font'),'size')[1:]=[Atom('1'),Atom('1')]
Path('keyboard.kicad_sch').write_text(dump(s)+'\n')
b=p.LoadBoard('keyboard.kicad_pcb')
def text(value,x,y,size=1):
 t=p.PCB_TEXT(b);t.SetText(value);t.SetPosition(p.VECTOR2I(int(x*1e6),int(y*1e6)));t.SetTextSize(p.VECTOR2I(int(size*1e6),int(size*1e6)));t.SetTextThickness(150000);t.SetLayer(p.F_SilkS);b.Add(t)
text('LEFT / PICO 1',148,65);text('RIGHT / PICO 1',291,65)
for x,side in [(160,'L'),(279,'R')]:
 for idx,label in enumerate(['1 VSYS','2 GND','3 TX' if side=='L' else '3 RX','4 RX' if side=='L' else '4 TX']):
  text(label,x+( -6 if side=='L' else 6),51+2.54*idx,.8)
p.SaveBoard('keyboard.kicad_pcb',b)
