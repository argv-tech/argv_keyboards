"""Finish the two-segment thumb-row link and restore the 0.4 mm width rule."""
from pathlib import Path
import pcbnew as p

p.SwigPyIterator.next = p.SwigPyIterator.__next__
ROOT = Path(__file__).resolve().parent.parent
board = p.LoadBoard(str(ROOT / "keyboard.kicad_pcb"))
for track in board.GetTracks():
    if track.GetClass() == "PCB_TRACK":
        track.SetWidth(400000)
points = [(128.845, 113.7996), (137.345, 113.7996), (145.845, 122.2996)]
existing = {(t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetLayer())
            for t in board.GetTracks()}
for start, end in zip(points, points[1:]):
    a = p.VECTOR2I(round(start[0] * 1e6), round(start[1] * 1e6))
    b = p.VECTOR2I(round(end[0] * 1e6), round(end[1] * 1e6))
    if (a.x, a.y, b.x, b.y, p.F_Cu) in existing:
        continue
    track = p.PCB_TRACK(board)
    track.SetStart(a)
    track.SetEnd(b)
    track.SetLayer(p.F_Cu)
    track.SetWidth(400000)
    track.SetNet(board.FindNet("ROW9"))
    board.Add(track)
p.SaveBoard(str(ROOT / "keyboard.kicad_pcb"), board)
