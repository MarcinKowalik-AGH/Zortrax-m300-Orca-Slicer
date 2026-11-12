# Settings dictionary: Z-SUITE → OrcaSlicer

These are functional correspondences, not proof of identical OEM toolpaths. Copy the source project's actual values and inspect the result; a process name is not the full former Z-SUITE selection.

## Parameter dictionary

| Z-SUITE concept | OrcaSlicer control | Migration rule / limitation |
|---|---|---|
| Printer model | Printer / Variant | M300 Classic → Zortrax M300 Classic; only OEM 0.4 is documented for Classic Z-SUITE. |
| Nozzle diameter | Printer Variant | 0.2/0.3/0.6 are project-specific; match the actual installed nozzle and the Klipper extruder config independently. |
| Material | Filament | Match exact named Z material, e.g. **Z-PLA ≠ Z-PLA Pro**; external materials → relevant Generic family and Save As. |
| Layer height | Process → Layer height | Use section 1 for convenience or type the exact desired height in a custom process. |
| High / Normal / Draft | Process plus Speed | Names alone do not establish matching speeds, wall count or support. |
| Infill density | Strength → Sparse infill density | Copy the source percentage, not default R7 Standard 15%, Strength 40%, or Draft 10%. |
| Infill pattern | Strength → Sparse infill pattern | Rectilinear/Grid/Honeycomb are functional approximations; no confirmed one-to-one octagonal equivalence. |
| Solid | Strength → Infill density | Set 100% and review shells; **not** the R7 `Strength` preset. |
| Mesh (source mode) | Strength → Infill | Source Mesh refers to hollow / no infill, **not** Orca `Grid`; adjust 0% and shells appropriately. |
| Shell | Walls, top/bottom shells, infill | Typically no infill; set top/bottom **both layer count and minimum shell thickness** consistently. |
| Spiral | Special mode → Spiral vase | Only for suitable geometry; not an automatic Shell conversion. |
| Top/bottom surface layers | Strength → Top/Bottom shell layers & thickness | Both constraints interact with layer height. |
| Seam Normal/Random | Quality → Seam position | Aligned/Random are functional translations; actual seam locations may differ. |
| Support Automatic/Editable/Lite | Support | Check generated support in preview; there is no proven exact Lite/Editable mapping. |
| Raft, gap, contact | Support → Raft layers / contact distance | R7 uses 2 raft layers. Source Z-SUITE raft zones RB/R2/RG/RS have no validated one-to-one representation. |
| Cooling AUTO/fixed | Filament → Cooling | AUTO depends on layer time and other rules; do not replace with a single fixed fan percentage. |
| Extruder/bed temperatures | Filament → Temperature | These are requested targets, **not** Klipper safety limits. |
| Retraction, Z-lift | Filament override / Printer | Source mm/min ÷ 60 for speeds; `nil` inherits; `R_Forward-R_Back` may be restart extra when semantics match. |
| Flow/feed source fields | Filament → Flow ratio / MVS | No direct 1:1 mapping; requires flow and volumetric calibration. |
| Pressure advance | Filament → Pressure advance | R7 uses PA=0 until tuning. |
| Output format | Export/Send G-code | Klipper receives `.gcode` through Moonraker storage `gcodes`; this is not an OEM `.zcode` conversion. |


## Host versus slicer

`position_min`, `safe_z`, `approach_distance`, PC7 release, mesh measurement, thermal protection and homing are **host configuration**, not slicer settings. Relative extrusion, temperature requests and the `START_PRINT` call are slicer integration points. Source `...Feed` fields cannot be copied as flow ratio or MVS without a validated conversion.

[Full crosswalk](ZSUITE_TO_ORCA.md) · [Profile guide](PROFILES.md).
