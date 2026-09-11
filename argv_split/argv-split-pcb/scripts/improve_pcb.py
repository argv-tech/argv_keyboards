"""Apply the manufacturing cleanup requested for the split keyboard PCB."""
from pathlib import Path
import pcbnew

pcbnew.SwigPyIterator.next = pcbnew.SwigPyIterator.__next__

ROOT = Path(__file__).resolve().parent.parent
BOARD_FILE = ROOT / "keyboard.kicad_pcb"
board = pcbnew.LoadBoard(str(BOARD_FILE))
drawings = list(board.GetDrawings())

MM = 1_000_000


def point(x, y):
    return pcbnew.VECTOR2I(round(x * MM), round(y * MM))


# Use one fabricator-friendly width for every routed copper segment. The
# existing two-layer routing is preserved so the schematic connectivity and
# proven copper topology remain unchanged.
for item in board.GetTracks():
    if item.Type() == pcbnew.PCB_TRACE_T:
        item.SetWidth(round(0.4 * MM))

# JLCPCB legend guidance calls for 1.0 mm characters with a 0.15 mm stroke.
# Bring the existing connector pin labels up to that minimum as well.
for item in drawings:
    if item.Type() == pcbnew.PCB_TEXT_T and item.GetLayerName() in ("F.SilkS", "F.Silkscreen"):
        size = item.GetTextSize()
        size.x = max(size.x, round(1.0 * MM))
        size.y = max(size.y, round(1.0 * MM))
        item.SetTextSize(size)
        item.SetTextThickness(max(item.GetTextThickness(), round(0.15 * MM)))
# Set the two top edges to leave >=5 mm beyond the 9.525 mm key courtyard,
# and move the left edge 1 mm outward to give the leftmost key the same margin.
# Existing ergonomic lower edges are already more than 5 mm clear.
for drawing in drawings:
    if drawing.GetLayerName() != "Edge.Cuts":
        continue
    start = drawing.GetStart()
    end = drawing.GetEnd()
    changed = False
    for attr, value in (("x", start.x), ("y", start.y)):
        if attr == "x" and abs(value / MM + 14.0) < 0.01:
            start.x = round(-15.0 * MM)
            changed = True
        if attr == "y" and value / MM < -9.5:
            start.y = round(-15.0 * MM)
            changed = True
    for attr, value in (("x", end.x), ("y", end.y)):
        if attr == "x" and abs(value / MM + 14.0) < 0.01:
            end.x = round(-15.0 * MM)
            changed = True
        if attr == "y" and value / MM < -9.5:
            end.y = round(-15.0 * MM)
            changed = True
    if changed:
        drawing.SetStart(start)
        drawing.SetEnd(end)

# Add a fabrication note to each half in an open area below the connector.
# The connector pin labels already identify the cable order and polarity.
for text, x, y in (
    ("5 mm MIN EDGE PADDING", 133.0, 68.5),
    ("CABLE ONLY - NO PCB UART LINK", 307.0, 68.5),
):
    existing = next((item for item in drawings
                     if item.Type() == pcbnew.PCB_TEXT_T and item.GetText() == text), None)
    if existing is not None:
        existing.SetLayer(board.GetLayerID("Dwgs.User"))
        continue
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetLayer(board.GetLayerID("Dwgs.User"))
    item.SetPosition(point(x, y))
    item.SetTextSize(point(1.0, 1.0))
    item.SetTextThickness(round(0.15 * MM))
    board.Add(item)

pcbnew.SaveBoard(str(BOARD_FILE), board)
print("Updated track widths, edge padding, and cable notes")
