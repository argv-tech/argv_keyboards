"""Export a dimensioned case drawing and CAD datums from the saved PCB."""
import json
from pathlib import Path
import pcbnew as p

p.SwigPyIterator.next = p.SwigPyIterator.__next__
ROOT = Path(__file__).resolve().parent.parent


def pos(point):
    return [round(point.x / 1e6, 6), round(point.y / 1e6, 6)]


def export():
    board = p.LoadBoard(str(ROOT / "keyboard.kicad_pcb"))
    footprints = {f.GetReference(): f for f in board.GetFootprints()}
    edges = [(pos(d.GetStart()), pos(d.GetEnd())) for d in board.GetDrawings()
             if d.GetLayer() == p.Edge_Cuts]
    holes = [{"reference": ref, "center_mm": pos(f.GetPosition()), "drill_mm": 2.1,
              "max_hardware_diameter_mm": 5.0, "copper_keepout_diameter_mm": 5.5}
             for ref, f in sorted(footprints.items()) if ref.startswith("H")]
    pico = pos(footprints["U1"].GetPosition())
    usb_x = round(pico[0] + 8.89, 3)
    usb_front = round(pico[1] - 2.67, 3)
    data = {
        "units": "mm", "view": "top", "axes": "KiCad: X right, Y down",
        "board": "left only", "pcb_thickness_mm": board.GetDesignSettings().GetBoardThickness() / 1e6,
        "edge_segments_mm": edges, "mounting_holes": holes,
        "case_xy_gap_mm": 0.5, "suggested_wall_thickness_mm": 2.0,
        "minimum_clearance_below_pcb_mm": 5.0,
        "pico_pin1_mm": pico,
        "pico_body_bounds_mm": [pico[0] - 1.61, pico[1] - 1.37, pico[0] + 19.39, pico[1] + 49.63],
        "usb": {"center_x_mm": usb_x, "front_y_mm": usb_front,
                "board_edge_y_mm": -15.0, "overhang_mm": round(-15 - usb_front, 3),
                "case_opening_width_mm": 16.0, "case_opening_height_mm": 10.0,
                "opening_z": "Centre on actual assembled USB socket; socket/header height is not fixed",
                "external_plug_access_depth_mm": 25.0},
        "interconnect": {"reference": "J1", "pin1_mm": pos(footprints["J1"].GetPosition()),
                         "pitch_mm": 2.54, "pins": ["VSYS", "GND", "TX", "RX"],
                         "case_exit": "Use a separate panel connector and internal wires; J1 is vertical"},
    }
    out = ROOT / "mechanical"
    out.mkdir(exist_ok=True)
    (out / "case-interface.json").write_text(json.dumps(data, indent=2) + "\n")

    # Minimal millimetre DXF: only actual carrier outline and mounting bores.
    # DXF uses Y up, so negate KiCad Y consistently for lines and circles.
    dxf = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4",
           "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for a, b in edges:
        dxf += ["0", "LINE", "8", "PCB_OUTLINE", "10", str(a[0]), "20", str(-a[1]),
                "11", str(b[0]), "21", str(-b[1])]
    for hole in holes:
        x, y = hole["center_mm"]
        dxf += ["0", "CIRCLE", "8", "M2_DRILL", "10", str(x), "20", str(-y), "40", "1.05"]
    dxf += ["0", "ENDSEC", "0", "EOF"]
    (out / "pcb-outline-mounts.dxf").write_text("\n".join(dxf) + "\n")

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="330mm" height="195mm" viewBox="0 0 330 195">',
           '<rect width="330" height="195" fill="#fafaf7"/>',
           '<g font-family="sans-serif" fill="#172a36">',
           '<text x="10" y="9" font-size="4.5">ARGV LEFT · CUSTOM CASE INTERFACE</text>',
           '<g transform="translate(25 42)">']
    for a, b in edges:
        svg.append(f'<path d="M {a[0]} {a[1]} L {b[0]} {b[1]}" stroke="#172a36" stroke-width="0.4"/>')
    for hole in holes:
        x, y = hole["center_mm"]
        svg += [f'<circle cx="{x}" cy="{y}" r="2.75" fill="none" stroke="#a46018" stroke-width="0.2" stroke-dasharray="0.8 0.6"/>',
                f'<circle cx="{x}" cy="{y}" r="1.05" fill="none" stroke="#172a36" stroke-width="0.3"/>',
                f'<text x="{x+3.3}" y="{y+1}" font-size="2.8">{hole["reference"]}</text>']
    x1, y1, x2, y2 = data["pico_body_bounds_mm"]
    svg += [f'<rect x="{x1}" y="{y1}" width="21" height="51" fill="#4e977f" fill-opacity="0.15" stroke="#2a715c" stroke-width="0.3"/>',
            f'<rect x="{usb_x-4}" y="{usb_front}" width="8" height="5.6" fill="#8a9ba5"/>',
            f'<rect x="{usb_x-8}" y="-36" width="16" height="21" fill="#599cac" fill-opacity="0.15" stroke="#397c8c" stroke-width="0.2" stroke-dasharray="1 0.7"/>',
            f'<text x="{usb_x}" y="-38" font-size="3" text-anchor="middle">16 mm USB opening</text>',
            f'<path d="M {usb_x} -36 V 40" stroke="#397c8c" stroke-width="0.2" stroke-dasharray="2 1"/>',
            f'<text x="{usb_x}" y="15" text-anchor="middle" font-size="3">PICO</text>']
    jx, jy = data["interconnect"]["pin1_mm"]
    svg += [f'<rect x="{jx-1.3}" y="{jy-1.3}" width="2.6" height="10.22" fill="none" stroke="#172a36" stroke-width="0.3"/>',
            f'<text x="{jx-3}" y="{jy+4}" text-anchor="end" font-size="3">J1 → panel connector</text>',
            '<text x="20" y="35" font-size="4">184 × 152 mm carrier envelope</text>',
            '<text x="20" y="41" font-size="3">PCB origin and switch locations retained</text>',
            '</g>']
    notes = ["TOP VIEW · ALL DIMENSIONS IN mm", "M2 holes: Ø2.1; hardware: Ø5 max",
             "Dashed rings: Ø5.5 copper keepouts", "Case XY clearance: 0.5 per side",
             "Suggested wall: 2.0", "Clear space below PCB: ≥5.0",
             f"USB centre X: {usb_x:.2f}", f"USB front Y: {usb_front:.2f}",
             "USB opening: 16 W × 10 H", "Centre height on assembled socket",
             "Keep 25 mm outside clear for plug", "Leave BOOTSEL and Pico removable",
             "J1: internal wires to panel connector", "Fit check with actual USB cable",
             "", "MOUNTING DATUMS (KiCad X, Y)"]
    notes += [f'{h["reference"]}: {h["center_mm"][0]:.2f}, {h["center_mm"][1]:.2f}' for h in holes]
    for i, note in enumerate(notes):
        svg.append(f'<text x="207" y="{22+i*6}" font-size="3">{note}</text>')
    svg += ['<text x="10" y="189" font-size="3">DXF: Y up (KiCad Y negated). JSON: original KiCad axes. Drawing scale 1:1 when printed at 100%.</text>', '</g></svg>']
    (out / "case-interface.svg").write_text("\n".join(svg) + "\n")
    print("Exported mechanical/case-interface.{json,svg} and pcb-outline-mounts.dxf")


if __name__ == "__main__":
    export()
