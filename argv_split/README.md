# argv_split

`argv_split` is a custom split ergonomic keyboard based on the ErgoDox. It keeps
the familiar two-half layout and thumb clusters while adapting the electronics
and key arrangement for this project.

## Features

- Split, column-oriented ergonomic layout
- 80 keys with dedicated thumb clusters
- Kailh hot-swap sockets for MX-compatible switches
- One diode per key for matrix isolation
- A Raspberry Pi Pico controller on each half
- Four-pin connectors for communication and power between the halves

## Project files

The KiCad project is located in [`argv_split_kicad/`](argv_split_kicad/):

- `argv_split_kicad.kicad_sch` — circuit schematic
- `argv_split_kicad.kicad_pcb` — PCB layout
- `argv_split_kicad.kicad_pro` — KiCad project settings
- `keyboard-layout.json` — physical layout data for Keyboard Layout Editor

Open `argv_split_kicad.kicad_pro` in KiCad to inspect or modify the design.

## Layout

The keyboard uses an 80-key split layout. It includes a full function row,
alphanumeric columns with a 0.25u vertical stagger, dedicated arrow keys, inner
symbol keys, and angled thumb clusters for Space, Backspace, Return, Control,
Linux/Meta, and Alt.

To view or edit the layout, open Keyboard Layout Editor, choose **Raw data**, and
paste in the contents of `keyboard-layout.json`. The labels in this file describe
the intended physical layout; the active key behavior still depends on the
keyboard firmware and keymap.

## Status

This is a custom hardware project and may still be a work in progress. Review
the schematic, PCB layout, footprints, clearances, and connector pinout before
ordering boards or assembling the keyboard.

## Attribution

This design is inspired by and derived from the ErgoDox keyboard layout, with
modifications made for the ARGV split keyboard project.
