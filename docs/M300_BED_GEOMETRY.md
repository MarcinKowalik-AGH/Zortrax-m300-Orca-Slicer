# Zortrax M300 Classic — measured physical bed and printer coordinates

## Source measurements (17 November 2026)

| Item | Measurement | Status |
|---|---:|---|
| Whole metal plate | **360 × 360 mm** | operator-measured |
| Left, right perforation margins | **14 mm each** | operator-measured |
| Front perforation margin | **15 mm** | operator-measured |
| Rear perforation margin | **16 mm** | operator-measured |
| Perforated field | **332 × 329 mm** | calculated |
| Four corner gold pads | **60 × 60 mm each** | operator-measured |
| Centre gold pad | **50 × 50 mm** | operator-measured |
| Exact pad locations relative to corners | 30 mm inset, approximately | **estimated from screenshot**, not measured |
| Safe nozzle range in Klipper | X: 0…300, Y: 0…305 mm | user-confirmed |
| Y=315 mm | service/head-cleaning travel, not print placement | out of scope |
| STL physical metal thickness | **3.0 mm** | operator-requested |
| Rear socket centre from plate left edge | approximately **148 mm** | ruler-photo estimate, not caliper |
| Rear socket plastic body width | approximately **8.5 mm** | ruler-photo estimate |
| Rear socket total width including tabs | approximately **12 mm** | ruler-photo estimate |
| Socket front-to-back depth | approximately **7 mm** | ruler-photo estimate |
| Socket rear protrusion | approximately **1.6 mm** | ruler-photo estimate |
| Socket height above plate | approximately **3.2 mm** | provisional; not physically measured |

## Geometry transform

Origin of physical coordinates `(u,v)` is the **front-left edge** of the 360 mm plate; its geometric centre is `(180,180)`. The nozzle printable field is:

- In physical coordinates, **X: u=30…330 mm; Y: v=30…335 mm**.
- In printer coordinates, **X: x=0…300 mm; Y: y=0…305 mm**.
- Conversion: `x = u - 30`, `y = v - 30`.
- Relative to the plate centre, the printable limit is **X −150…+150 mm** and **Y −150…+155 mm**.
- Physical metal limits in printer coordinates: **X −30…330 mm, Y −30…330 mm**.
- Perforated field in printer coordinates: **X −16…316 mm, Y −15…314 mm**.

Orca's custom physical bed STL is positioned by its own **print-volume midpoint** (`150,152.5`). Hence the STL's local bounds are X `−180…180` mm, Y `−182.5…177.5` mm. The 2.5 mm Y offset ensures that the **real plate centre**, not the slightly rear-shifted print rectangle midpoint, remains correctly aligned.

## Rendering model

[View full-scale top-view SVG with the actual 300 × 305 mm boundary](Zortrax_M300_360mm_plate_layout.svg).

The interactive `bed_custom_texture` SVG is clipped by Orca to its real printable area. The exterior metal must therefore be shown by a separate `bed_custom_model` STL rather than by enlarging `printable_area`. The STL uses physical millimetre coordinates and represents the **complete 3 mm-thick plate**. The non-printable outer metal ring has real perforation geometry and frame Allen-bolt seats; beneath the central SVG print texture there is a thin solid STL backing so the preview remains performant. This backing is visual only: the SVG supplies the regular apparent holes inside the printable zone. The two centre screws and all five gold pads remain in the clipped SVG; colour cannot be carried through Orca's monochrome STL visual model.

The native profile installer generates the STL locally using `tools/bed_geometry.py` and copies it beside the SVG. The rear electrical connector has been modelled from operator ruler photos `IMG_9058.jpg`–`IMG_9063.jpg`, with the housing centred at physical X≈148 mm, positioned around rear Y≈355–362 mm. The connector includes a cream-housing-shaped stepped body (STL monochrome), two side solder wings, five top ribs and a small latch. It is modelled roughly 1.6 mm past the rear metal edge; its height (about 3.2 mm above the plate) is **not measured** and remains provisional. Visual details are approximate where not yet measured: exact screw positions, precise perforation diameter and exact pad-corner distances. **They do not affect print coordinates or G-code.**

No Klipper configuration or MCU/host settings are installed by this repository. Existing motion, mesh, purge and service procedures remain unchanged.
