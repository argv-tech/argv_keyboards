"""Prepare the current left PCB in a separate file for local DSN/SES routing.

Usage: /usr/bin/python3 scripts/prepare_case_pcb.py /tmp/argv-case.kicad_pcb
The source PCB is never overwritten by this preparation command.
"""
import argparse
import math
from pathlib import Path

import pcbnew as p

p.SwigPyIterator.next = p.SwigPyIterator.__next__
ROOT = Path(__file__).resolve().parent.parent
MM = 1_000_000


def xy(x, y):
    return p.VECTOR2I(round(x * MM), round(y * MM))


def prepare(output):
    source = ROOT / "keyboard.kicad_pcb"
    assert output.resolve() != source.resolve(), "Prepare a separate working board"
    board = p.LoadBoard(str(source))
    refs = {f.GetReference(): f for f in board.GetFootprints()}
    assert "U1" in refs and "U2" not in refs, "This revision is the left half only"
    # Pin 1 is the footprint origin. USB front is at local y=-2.67 mm;
    # the new position puts it 0.67 mm beyond the y=-15 mm carrier edge.
    refs["U1"].SetPosition(xy(143, -13))
    refs["U1"].Reference().SetPosition(xy(164, 36))
    # Keep the overhanging connector outline on fabrication drawings only.
    # A project-local library variant records this intended silk difference.
    pico = refs["U1"]
    for item in pico.GraphicalItems():
        if item.GetLayer() == p.F_SilkS and item.GetBoundingBox().GetTop() < -14.85 * MM:
            item.SetLayer(p.F_Fab)
    pico.SetFPID(p.LIB_ID("ARGV", "RaspberryPi_Pico_Case_THT"))
    library = ROOT / "footprints/ARGV.pretty"
    library.mkdir(exist_ok=True)
    p.PCB_IO_KICAD_SEXPR().FootprintSave(str(library), pico)

    holes = sorted(
        (f for f in board.GetFootprints() if f.GetValue() == "MountingHole_2.1mm"),
        key=lambda f: (f.GetPosition().y, f.GetPosition().x),
    )
    assert len(holes) == 8
    for i, hole in enumerate(holes, 1):
        hole.SetReference(f"H{i}")
        if i == 3:
            # Half a millimetre outward separates its courtyard from the Pico.
            hole.SetPosition(xy(166, -11.5))
        hole.SetBoardOnly(True)
        hole.Reference().SetVisible(False)
        hole.Value().SetVisible(False)

    # Reserve screw-head / standoff envelopes on both copper layers. These
    # circles are conservative polygons circumscribing a 5.5 mm diameter.
    for zone in list(board.Zones()):
        if zone.GetZoneName().startswith("CASE_"):
            board.Remove(zone)
    for hole in holes:
        center = hole.GetPosition()
        zone = p.ZONE(board)
        zone.SetZoneName(f"CASE_{hole.GetReference()}_M2_CLEARANCE")
        zone.SetIsRuleArea(True)
        zone.SetLayerSet(p.LSET.AllCuMask(2))
        zone.SetDoNotAllowTracks(True)
        zone.SetDoNotAllowVias(True)
        zone.SetDoNotAllowZoneFills(True)
        zone.SetDoNotAllowPads(False)
        zone.SetDoNotAllowFootprints(False)
        outline = zone.Outline()
        outline.NewOutline()
        radius = 2.75 / math.cos(math.pi / 24)
        for step in range(24):
            angle = 2 * math.pi * step / 24
            outline.Append(center.x + round(radius * MM * math.cos(angle)),
                           center.y + round(radius * MM * math.sin(angle)))
        board.Add(zone)

    for item in list(board.GetDrawings()):
        if item.GetClass() == "PCB_TEXT" and item.GetText() == "5 mm MIN EDGE PADDING":
            # This old blanket claim did not describe the controller or screws.
            board.Remove(item)
    # Preserve switch, diode, interconnect and mounting-hole positions. Route
    # against final width/clearance instead of widening an older narrow route.
    for track in list(board.GetTracks()):
        board.Delete(track)
    p.SaveBoard(str(output), board)
    assert p.ExportSpecctraDSN(board, str(output.with_suffix(".dsn")))
    print(f"Prepared {output} and {output.with_suffix('.dsn')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    prepare(parser.parse_args().output)
