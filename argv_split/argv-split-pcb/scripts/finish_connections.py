from pathlib import Path
# Reuse the symbol/footprint helpers without rerunning the controller placement.
source=Path('scripts/add_controllers.py').read_text().split('pinmap=')[0]
source=source.replace("if any(f.GetReference()=='U1' for f in b.GetFootprints()): raise SystemExit('Controllers already present')",'')
exec(source)
if any(f.GetReference()=='J1' for f in b.GetFootprints()): raise SystemExit('Connectors already present')
for i,(side,x) in enumerate([('L',160),('R',279)],1):
 add('Connector_Generic:Conn_01x04','J'+str(i),'BREAKOUT_4PIN','Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',(365.76,66.04+(i-1)*119.38),(x,51),{'1':side+'_VSYS','2':side+'_GND','3':side+('_TX' if i==1 else '_RX'),'4':side+('_RX' if i==1 else '_TX')})
 # VSYS is powered by the module's internal USB Schottky diode, or the remote module via cable.
 lib=getlib('power:PWR_FLAG'); xsch=330.2; ysch=40.64+(i-1)*119.38;u=uid();ref='#FLG0'+str(i)
 s.append(parse(f'(symbol (lib_id "power:PWR_FLAG") (at {xsch} {ysch} 0) (unit 1) (in_bom no) (on_board yes) (dnp no) (uuid "{u}") (property "Reference" "{ref}" (at {xsch} {ysch} 0) (effects (font (size 1.27 1.27)) (hide yes))) (property "Value" "PWR_FLAG" (at {xsch} {ysch-5.08} 0) (effects (font (size 1.27 1.27)))) (pin "1" (uuid "{uid()}")) (instances (project "keyboard" (path "/{root}" (reference "{ref}") (unit 1)))))'))
 s.append(parse(f'(global_label "{side}_VSYS" (shape input) (at {xsch} {ysch} 0) (effects (font (size 1 1)) (justify left)) (uuid "{uid()}"))'))
# Unused module outputs and AGND require no external connection.
for side in ['L','R']:
 for lab in list(children(s,'global_label')):
  if lab[1] in [side+'_VBUS',side+'_3V3'] or (lab[1]==side+'_GND' and float(one(lab,'at')[1])>300):
   at=one(lab,'at');s.remove(lab);s.append(parse(f'(no_connect (at {at[1]} {at[2]}) (uuid "{uid()}"))'))
for t in children(s,'text'):
 t[1]=t[1].replace('Connector footprint pending identification of purchased part.','J1/J2: provisional 2.54 mm wire/breakout headers; purchased connector footprint to confirm.\\nStraight cable pin 1-1, 2-2, 3-3, 4-4; TX/RX crossover is on the right PCB.')
# Restore the missing stabilizer libraries from the original embedded design.
Path('symbols').mkdir(exist_ok=True);Path('footprints/Mounting_Keyboard_Stabilizer.pretty').mkdir(exist_ok=True)
st=copy.deepcopy(next(x for x in children(libs,'symbol') if x[1]=='Mechanical:SW_stab'));st[1]='SW_stab'
Path('symbols/Mechanical.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor")\n'+dump(st)+'\n)\n')
for f in b.GetFootprints():
 if f.GetReference().startswith('ST'):
  p.PCB_IO_KICAD_SEXPR().FootprintSave(str(Path('footprints/Mounting_Keyboard_Stabilizer.pretty').resolve()),f)
  f.Reference().SetVisible(False)
 # Loaded footprints need a fully qualified library identifier.
 if f.GetReference().startswith('U'): f.SetFPID(p.LIB_ID('Module','RaspberryPi_Pico_Common_THT'))
 if f.GetReference().startswith('J'): f.SetFPID(p.LIB_ID('Connector_PinHeader_2.54mm','PinHeader_1x04_P2.54mm_Vertical'))
Path('sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Mechanical") (type "KiCad") (uri "${KIPRJMOD}/symbols/Mechanical.kicad_sym") (options "") (descr "Original keyboard stabilizer symbol")))\n')
fpt=parse(Path('fp-lib-table').read_text())
for name,uri in [('Mounting_Keyboard_Stabilizer','${KIPRJMOD}/footprints/Mounting_Keyboard_Stabilizer.pretty'),('Module','${KICAD10_FOOTPRINT_DIR}/Module.pretty'),('Connector_PinHeader_2.54mm','${KICAD10_FOOTPRINT_DIR}/Connector_PinHeader_2.54mm.pretty')]:
 fpt.append(parse(f'(lib (name "{name}") (type "KiCad") (uri "{uri}") (options "") (descr ""))'))
Path('fp-lib-table').write_text(dump(fpt)+'\n');Path('keyboard.kicad_sch').write_text(dump(s)+'\n');p.SaveBoard('keyboard.kicad_pcb',b)
