# argv_split

`argv_split` is a custom split ergonomic keyboard based on the ErgoDox. It keeps
the familiar two-half layout and thumb clusters while adapting the electronics
and key arrangement for this project.

## Features

- Split ergonomic layout with separated left and right key groups
- 76 keys with dedicated thumb clusters
- Kailh hot-swap sockets for MX-compatible switches
- One diode per key for matrix isolation
- A Raspberry Pi Pico controller on each half
- Four-pin connectors for communication and power between the halves

## Project files

The design files are located in this directory:

- [`argv_split_kicad/argv_split_kicad.kicad_sch`](argv_split_kicad/argv_split_kicad.kicad_sch) — circuit schematic
- [`argv_split_kicad/argv_split_kicad.kicad_pcb`](argv_split_kicad/argv_split_kicad.kicad_pcb) — PCB layout
- [`argv_split_kicad/argv_split_kicad.kicad_pro`](argv_split_kicad/argv_split_kicad.kicad_pro) — KiCad project settings
- [`keyboard-layout.json`](keyboard-layout.json) — physical layout data for Keyboard Layout Editor
- [`keyboard_layout.dxf`](keyboard_layout.dxf) — exported layout geometry

Open `argv_split_kicad/argv_split_kicad.kicad_pro` in KiCad to inspect or
modify the design.

## Layout

The keyboard uses a 76-key split layout:

- 12 function keys (`F1`–`F12`), with six on each half
- 56 keys in four horizontal main rows, with seven keys per half in each row
- 8 thumb keys in two clusters rotated 30 degrees toward the center

The outer keys in the main block are 1.5u wide. The inner columns contain
parenthesis, brace, bracket, and quote keys. The left thumb cluster contains a
2u `Space` key above three 2u-tall keys labeled `Crtl`, `Linux`, and `Alt`. The
right cluster mirrors it with a 2u `backspace` key above `Return`, `Linux`, and
`Crtl`. These names and spellings match the current layout data.

To view or edit the layout, open Keyboard Layout Editor, choose **Raw data**, and
paste in the contents of [`keyboard-layout.json`](keyboard-layout.json). The
labels in this file describe the intended physical layout; the active key
behavior still depends on the keyboard firmware and keymap.

## Status

This is a custom hardware project and may still be a work in progress. Review
the schematic, PCB layout, footprints, clearances, and connector pinout before
ordering boards or assembling the keyboard.

## Attribution

This design is inspired by and derived from the ErgoDox keyboard layout, with
modifications made for the ARGV split keyboard project.
