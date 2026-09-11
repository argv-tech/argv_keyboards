"""Import a reviewed local router session into its prepared board.

Usage: import_case_routes.py prepared.kicad_pcb routes.ses output.kicad_pcb
The switch/diode/connector pads and all net assignments must stay unchanged.
"""
import argparse
import pcbnew as p

p.SwigPyIterator.next = p.SwigPyIterator.__next__


def snapshot(board):
    return sorted((f.GetReference(), pad.GetNumber(), pad.GetNetname(),
                   pad.GetPosition().x, pad.GetPosition().y)
                  for f in board.GetFootprints() if not f.GetReference().startswith("H")
                  for pad in f.Pads())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared")
    parser.add_argument("session")
    parser.add_argument("output")
    args = parser.parse_args()
    board = p.LoadBoard(args.prepared)
    before = snapshot(board)
    assert p.ImportSpecctraSES(board, args.session)
    assert snapshot(board) == before, "Routing must not move or reassign electrical pads"
    # The first routing session predates this 0.5 mm mechanical adjustment.
    for f in board.GetFootprints():
        if f.GetReference() == "H3":
            f.SetPosition(p.VECTOR2I(166000000, -11500000))
    p.SaveBoard(args.output, board)
    print(f"Imported routing into {args.output}")
