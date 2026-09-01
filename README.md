# ARGV Keyboards

Keyboard Layout Editor definitions and printable keycap models for building and experimenting with custom keyboards.

The repository contains two keyboard layouts plus four ScottoCaps profiles. Ready-to-print meshes, editable CAD files, and original Shapr3D sources are included where available.

## Quick start

Choose a layout:

- [`keyboard-layout.json`](keyboard-layout.json) — split 80-key layout.
- [`keyboard-layout-no-split.json`](keyboard-layout-no-split.json) — non-split 106-key layout.

Then:

1. To view or edit the layout, open [Keyboard Layout Editor](https://www.keyboard-layout-editor.com/), select **Raw data**, and paste in the contents of the JSON file.
2. Choose a keycap profile and confirm that it supports your switch type and printing process.
3. Open a `.3mf` or `.stl` file in your slicer. Use the matching `.step` or `.shapr` file if you need to modify the geometry.
4. Print a single `1.00u` keycap first and test the stem fit before printing a full set.

## Keycap profiles

| Profile | Switches | Process | Contents | Documentation |
| --- | --- | --- | --- | --- |
| Flat | Cherry MX | FDM | Low-profile blanks and legends | [Printing notes](ScottoCaps/Flat/Readme.md) |
| Glass | Cherry MX and Choc | MSLA resin | Low-profile blanks from 1.00u to 10.00u, depending on switch type | [Safety and printing notes](ScottoCaps/Glass/README.md) |
| Scooped | Cherry MX and Choc | FDM | Concave, convex, homing, and multi-size caps; extensive legend collection | [Dimensions and printing notes](ScottoCaps/Scooped/Readme.md) |
| Sculpted | Cherry MX | FDM | R1–R5 blank keycaps in multiple sizes | [Dimensions and printing notes](ScottoCaps/Sculpted/Readme.md) |

### File formats

| Extension | Use |
| --- | --- |
| `.3mf` | Preferred slicer-ready model, including legend objects where applicable |
| `.stl` | Widely supported printable mesh |
| `.step` | Editable solid model for CAD applications |
| `.shapr` | Original Shapr3D project |
| `.json` | Keyboard Layout Editor raw data |

## Printing notes

- **Check compatibility first.** MX and Choc stems are different; use the directory for your switch type.
- **Test the stem fit.** The FDM stems use an approximately 0.15 mm tolerance, so the result depends on printer calibration and material. Never force a tight cap onto a switch.
- **Use dual extrusion for legends.** The Scooped legend variants are designed for a dual-extruder or multi-material printer.
- **Use biocompatible resin for Glass caps.** These caps are handled continuously and must be printed with an appropriate biocompatible resin. Read the [Glass safety notes](ScottoCaps/Glass/README.md) before printing.
- **Expect to tune the model or slicer.** Stem fit, rotation, and surface finish vary between printers. Each profile's documentation contains its recommended orientation and adjustments.

## Repository structure

```text
.
├── keyboard-layout.json
├── keyboard-layout-no-split.json
└── ScottoCaps/
    ├── Flat/
    │   ├── Blanks/
    │   └── Legends/
    ├── Glass/
    │   ├── Choc/
    │   └── MX/
    ├── Scooped/
    │   ├── Choc/
    │   └── MX/
    └── Sculpted/
        └── Blanks/
```

File names encode the key width in keyboard units (`u`). Scooped Choc models also include their physical footprint (`16x16`, `18x17`, or `18x18`), while Sculpted files include the row (`R1`–`R5`).

## Contributing

When adding or changing an asset:

- Keep the existing profile, switch, size, and variant naming conventions.
- Include an editable `.step` model alongside printable meshes when possible.
- Update the relevant profile README with any new dimensions, materials, or slicer requirements.
- Confirm that edited layout files still load in Keyboard Layout Editor.

## Credits

Special thanks to [ScottoKeebs](https://scottokeebs.com/) for the keycap models and printing guidance. The original designs and source files are available in the [ScottoKeebs GitHub repository](https://github.com/joe-scotto/scottokeebs/).
