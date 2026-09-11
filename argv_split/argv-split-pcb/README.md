# Split keyboard — one fabrication file, two cable-connected halves

Open `keyboard.kicad_pro` in KiCad 10. The PCB is one fabrication file containing two separately cuttable halves, so both halves can be sent in one order. U1 is the left Pico and U2 is the right Pico. Existing switch positions are preserved. Use standard, non-wireless Raspberry Pi Pico 1 modules with two 20-pin, 2.54 mm headers/sockets. USB connectors face the top edge. The modules supply their own regulation and USB circuitry.

All routed copper segments are 0.4 mm. The top and left edges were moved to leave at least 5 mm between the board edge and the switch courtyard; the other edges already meet that margin. The two halves have no PCB copper link: the four-wire cable is the only connection between them.

The project rules use a JLCPCB-friendly 2-layer baseline: 0.2 mm copper clearance, 0.4 mm minimum track width, 0.6/0.3 mm vias, 0.15 mm minimum via annular width, 0.09 mm soldermask expansion clearance, and 1.0 mm / 0.15 mm silkscreen text height and stroke. The 0.2 mm clearance is deliberately stricter than JLCPCB's published 0.10 mm capability so the board has process margin. See [JLCPCB's PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities). Run the final DRC and JLCDFM check on the exported Gerbers before ordering.

The widened 0.4 mm tracks are applied to the existing compact routing. With the stricter 0.2 mm clearance rule, the current DRC report flags 75 clearance violations. Treat this revision as a routing review checkpoint and do not order until those routes are respaced or the JLCPCB DFM result confirms the actual geometry.

**Connector fit is not yet confirmed.** J1/J2 are standard 1×4, 2.54 mm through-hole headers for wiring to a separate connector PCB. They are not a verified footprint for the purchased four-pin part. Confirm its model, pitch, pin order, mounting, and cable continuity before fabrication. The board outlines are proposed outlines; check them against the intended plate/case.

## Four-wire interconnect

Use 3.3 V logic, full-duplex UART. GP0 is TX and GP1 is RX on both Picos. The right connector swaps the signal assignments, so a pin-for-pin cable crosses TX to RX:

| Cable pin | J1 / left | J2 / right |
| --- | --- | --- |
| 1 | U1 pin 39, VSYS | U2 pin 39, VSYS |
| 2 | Ground | Ground |
| 3 | U1 pin 1, GP0 / TX | U2 pin 2, GP1 / RX |
| 4 | U1 pin 2, GP1 / RX | U2 pin 1, GP0 / TX |

Cable connections: 1–1, 2–2, 3–3, 4–4. Do not add a second TX/RX crossover in the cable. Connect USB to one Pico; its onboard VBUS-to-VSYS Schottky diode supplies both halves through the VSYS wire. Do not connect the Pico 3V3 regulator outputs together. The schematic uses separate left/right net names because the cable is external, not a copper trace between boards.

Connect or disconnect the interconnect with USB power removed, especially if the purchased connector is TRRS: its contacts can short during insertion. This interface is not designed for live insertion.

## Matrix mapping

Diode cathodes connect to rows: firmware diode direction is `COL2ROW`. Each half has a logical 5×8 matrix with unused positions. GPIO names below refer to RP2040 GPIO numbers, not physical Pico pin numbers.

| GPIO | Pico pin | Left net | Right net |
| --- | --- | --- | --- |
| GP2 | 4 | ROW0 | ROW8 |
| GP3 | 5 | ROW1 | ROW7 |
| GP4 | 6 | ROW2 | ROW6 |
| GP5 | 7 | ROW3 | ROW5 |
| GP6 | 9 | ROW9 | ROW4 |
| GP7 | 10 | COL0 | COL8 |
| GP8 | 11 | COL1 | COL9 |
| GP9 | 12 | COL2 | COL10 |
| GP10 | 14 | COL3 | COL11 |
| GP11 | 15 | COL4 | COL12 |
| GP12 | 16 | COL5 | COL13 |
| GP13 | 17 | COL6 | COL14 |
| GP14 | 19 | COL7 | COL15 |

For split firmware, the global schematic ROW/COL numbers need translating to each half's local five rows and eight columns using this table. Firmware is not included or tested in this hardware project.

## Cable transport

Only the Pico-to-connector traces are on the PCBs. The inter-half TX/RX connection runs through the cable, and the cable can be rewired when a board is used on the opposite side. The right-hand connector swaps pins 3 and 4 so a straight pin-for-pin cable works with the two halves.

The UART baud rate is programmable; start at a conservative rate and verify the actual cable and firmware before increasing it. Scan rate, debounce and USB scheduling also affect keyboard latency.

QMK supports RP2040 full-duplex serial transport. Follow its driver configuration for GP0/GP1 and the selected driver; a complete keymap and handedness configuration are still required.

Sources: [RP2040 datasheet, UART §4.2 and I²C §4.3](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf), [QMK serial drivers](https://docs.qmk.fm/drivers/serial), [QMK RP2040 support](https://docs.qmk.fm/platformdev_rp2040), [Pico board datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf).

## Verification and previews

- `reports/erc.json`: schematic electrical checks.
- `reports/drc.json`: PCB design rules, unconnected items, and schematic parity.
- `reports/pcb-preview.png`: latest saved PCB preview.
- `reports/schematic/keyboard.svg`: schematic preview.
- `scripts/validate_design.py`: independent checks of connector and matrix pin mapping, and trace confinement to the two outlines.

If an already-open PCB editor shows long traces across the gap or below the boards, close that older in-memory view without saving and reopen the current project from disk. Avoid overwriting the updated file with the older view.

The scripts used for one-time construction are retained for traceability. Do not rerun `add_controllers.py`, `finish_connections.py`, `sync_board.py`, `finish_presentation.py`, or `clarify_schematic.py` on the finished design: some are one-time migrations and `sync_board.py` intentionally removes routing before autorouting. Edit the KiCad files normally for subsequent changes.
