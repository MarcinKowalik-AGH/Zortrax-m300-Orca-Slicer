# Z-SUITE → OrcaSlicer R7: Zortrax M300 Classic profile crosswalk

> **Scope and provenance (11 November 2026).** Migrated from the project's recovered Z-SUITE 2.32 / beta-4 data and the 11 November R7 snapshot. This is an **engineering crosswalk, not a manufacturer-certified one-to-one conversion**. It distinguishes displayed Z-SUITE layer labels, the recovered `SliceThickness` field, and actual values in OrcaSlicer. Numeric tables are historical R7 source values, **not new thermal, motion or hardware recommendations**. The linked repository keeps the underlying [Classic source](../sources/ZSUITE_classic.json), [beta-4 source](../sources/ZSUITE_beta4.json) and [R7 process catalog](../evidence/R7_PROCESS_CATALOG.json).

## 1. Z-SUITE layer/quality → R7 process (stock 0.4 mm nozzle)

The original Classic M300 offers a **0.4 mm nozzle** in Z-SUITE. Our 0.2/0.3/0.6 mm variants are community adaptations for a mechanically fitted nozzle and Klipper; do not present them as official Classic OEM modes.

| Z-SUITE label / mode | Z-SUITE displayed height (mm) | Recovered `SliceThickness` (mm) | Closest ready-to-use Orca R7 process (0.4 mm) | Orca height (mm) | Qualification |
|---|---:|---:|---|---:|---|
| 0.09 High / Normal | 0.09 | 0.10 | 0.08mm SuperDetail | 0.08 | Similar fine-detail category only; create a custom 0.09 or 0.10 preset for numeric equivalence. |
| 0.14 High | 0.14 | 0.15 | 0.12mm Detail | 0.12 | Thinner approximation; not the recovered High preset. |
| 0.14 Normal | 0.14 | 0.15 | 0.16mm Optimal (or 0.12 Detail) | 0.16 / 0.12 | Nearest practical quality selection, **not** exact layer height. |
| 0.19 Normal | 0.19 | 0.20 | 0.20mm Standard | 0.20 | Strongest starting point; some Z-PLA Pro Normal speeds match exactly. |
| 0.19 High | 0.19 | 0.20 | 0.20mm High Quality | 0.20 | Functionally similar but different walls/speeds. |
| 0.19 Draft | 0.19 | 0.20 | 0.20mm Standard | 0.20 | No dedicated 0.20mm Draft; modify a local copy after checking source speeds. |
| 0.29 Normal / Draft | 0.29 | 0.30 | 0.28mm SuperDraft | 0.28 | Coarse-layer approximation; R7 sets 10% infill, not automatically equal to Z-SUITE. |
| 0.39 ABS-based external record | 0.39 | 0.39 | None for 0.4 mm | — | Only two external ABS-family records; not a universal Classic M300 print setting. |

**Important:** 0.09, 0.14, 0.19 and 0.29 are Z-SUITE displayed labels. They must not be silently rewritten as 0.10, 0.15, 0.20 or 0.30. For strict height matching, **Save As** a custom Orca process and set the desired value explicitly; the rest of the process still needs independent comparison.

## 2. All 30 delivered R7 processes

Speeds are nominal settings in mm/s, not measured machine speeds. Infill, accelerations, cooling, volumetric-flow limits and geometry can reduce effective motion. All presets retain a 2-layer raft; the gap to the model varies with layer height.

| Nozzle (mm) | Process | Layer (mm) | Walls | Infill | Outer speed (mm/s) | Top speed (mm/s) | First layer (mm) | Raft gap (mm) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 0.2 | Fine | 0.06 | 2 | 15% | 12.833 | 46.667 | 0.06 | 0.06 |
| 0.2 | SuperDetail | 0.08 | 2 | 15% | 12.833 | 46.667 | 0.08 | 0.08 |
| 0.2 | Standard | 0.1 | 2 | 15% | 18.333 | 66.667 | 0.1 | 0.1 |
| 0.2 | Detail | 0.12 | 2 | 15% | 15.583 | 56.667 | 0.12 | 0.12 |
| 0.2 | Optimal | 0.16 | 2 | 15% | 16.5 | 60 | 0.12 | 0.15 |
| 0.3 | SuperDetail | 0.08 | 2 | 15% | 16.333 | 28 | 0.08 | 0.08 |
| 0.3 | Detail | 0.12 | 2 | 15% | 19.833 | 34 | 0.12 | 0.12 |
| 0.3 | Optimal | 0.16 | 2 | 15% | 21 | 36 | 0.16 | 0.15 |
| 0.3 | High Quality | 0.2 | 3 | 15% | 17.5 | 20 | 0.18 | 0.15 |
| 0.3 | Standard | 0.2 | 2 | 15% | 23.333 | 40 | 0.18 | 0.15 |
| 0.3 | Strength | 0.2 | 4 | 40% | 23.333 | 40 | 0.18 | 0.15 |
| 0.3 | Draft | 0.24 | 2 | 10% | 23.333 | 40 | 0.18 | 0.15 |
| 0.4 | SuperDetail | 0.08 | 2 | 15% | 16.333 | 28 | 0.08 | 0.08 |
| 0.4 | Detail | 0.12 | 2 | 15% | 19.833 | 34 | 0.12 | 0.12 |
| 0.4 | Optimal | 0.16 | 2 | 15% | 21 | 36 | 0.16 | 0.15 |
| 0.4 | High Quality | 0.2 | 3 | 15% | 17.5 | 20 | 0.2 | 0.15 |
| 0.4 | Standard | 0.2 | 2 | 15% | 23.333 | 40 | 0.2 | 0.15 |
| 0.4 | Strength | 0.2 | 4 | 40% | 23.333 | 40 | 0.2 | 0.15 |
| 0.4 | Draft | 0.24 | 2 | 10% | 23.333 | 40 | 0.2 | 0.15 |
| 0.4 | SuperDraft | 0.28 | 2 | 10% | 23.333 | 40 | 0.2 | 0.15 |
| 0.6 | Detail | 0.12 | 2 | 15% | 19.833 | 34 | 0.12 | 0.12 |
| 0.6 | Optimal | 0.16 | 2 | 15% | 21 | 36 | 0.16 | 0.15 |
| 0.6 | High Quality | 0.2 | 3 | 15% | 17.5 | 20 | 0.2 | 0.15 |
| 0.6 | Standard | 0.2 | 2 | 15% | 23.333 | 40 | 0.2 | 0.15 |
| 0.6 | Strength | 0.2 | 4 | 40% | 23.333 | 40 | 0.2 | 0.15 |
| 0.6 | Draft | 0.24 | 2 | 10% | 23.333 | 40 | 0.2 | 0.15 |
| 0.6 | SuperDraft | 0.28 | 2 | 10% | 23.333 | 40 | 0.2 | 0.15 |
| 0.6 | Coarse | 0.32 | 2 | 10% | 23.333 | 40 | 0.2 | 0.15 |
| 0.6 | Draft | 0.36 | 2 | 10% | 23.333 | 40 | 0.2 | 0.15 |
| 0.6 | SuperDraft | 0.42 | 2 | 10% | 23.333 | 40 | 0.2 | 0.15 |

Process breakdown: 0.2 mm nozzle = 5; 0.3 = 7; 0.4 = 8; 0.6 = 10. The 0.2 mm nozzle has no 0.20 mm process because this project's quality limits cap its layer height at 0.16 mm.

## 3. Exact speed comparison: Z-PLA Pro, Classic 0.4 mm, Z-SUITE 0.19 label / 0.20 recovered SliceThickness

The source speeds were recovered in **mm/min** and divided by 60. Compare the same six motion categories, not just the names `High` / `Normal` / `Draft`.

| Z-SUITE mode | Proposed Orca R7 process | Feature | Z-SUITE (mm/min) | Z-SUITE (mm/s) | R7 (mm/s) |
|---|---|---|---:|---:|---:|
| Normal | 0.20mm Standard | Outer wall | 1400 | 23.333 | 23.333 |
| Normal | 0.20mm Standard | Inner wall | 3000 | 50 | 50 |
| Normal | 0.20mm Standard | Sparse infill | 3000 | 50 | 50 |
| Normal | 0.20mm Standard | Top surface | 2400 | 40 | 40 |
| Normal | 0.20mm Standard | Bridge | 4000 | 66.667 | 66.667 |
| Normal | 0.20mm Standard | Travel | 7200 | 120 | 120 |
| High | 0.20mm High Quality | Outer wall | 1200 | 20 | 17.5 |
| High | 0.20mm High Quality | Inner wall | 2400 | 40 | 50 |
| High | 0.20mm High Quality | Sparse infill | 2400 | 40 | 50 |
| High | 0.20mm High Quality | Top surface | 1800 | 30 | 20 |
| High | 0.20mm High Quality | Bridge | 2000 | 33.333 | 66.667 |
| High | 0.20mm High Quality | Travel | 4800 | 80 | 120 |
| Draft | 0.20mm Standard | Outer wall | 1500 | 25 | 23.333 |
| Draft | 0.20mm Standard | Inner wall | 3200 | 53.333 | 50 |
| Draft | 0.20mm Standard | Sparse infill | 3200 | 53.333 | 50 |
| Draft | 0.20mm Standard | Top surface | 4000 | 66.667 | 40 |
| Draft | 0.20mm Standard | Bridge | 4000 | 66.667 | 66.667 |
| Draft | 0.20mm Standard | Travel | 9000 | 150 | 120 |

For **Normal**, all six listed speed settings match `0.20mm Standard` in this particular Z-PLA Pro example. This does **not** establish full G-code, raft, wall, or support equivalence. `High Quality` is a community 3-wall quality adaptation, not a copy of the Z-SUITE High speed table; `Strength` (40% gyroid / four walls) is not Z-SUITE Solid.

## 4. 0.4 mm material baseline crosswalk (26 filament entries)

These are the original R7 recorded **filament settings** for the 0.4 mm nozzle, not a new recommendation. The Z-SUITE-derived source may be from M200, M300 Plus, Inventure or Endureal as indicated. Materials with another machine provenance are *not* implied to be officially supported on the M300 Classic. Filament profiles exist separately for all four nozzle variants.

| Material / Orca filament | Nozzle °C | Bed °C | Retract mm | Retract mm/s | Restart extra mm | Z-hop mm | Origin / limit |
|---|---:|---:|---:|---:|---:|---:|---|
| Generic ABS | 250 | 100 | 1 | 35 | 0 | 0.2 | Generic starter |
| Generic ASA | 255 | 100 | 1 | 35 | 0 | 0.2 | Generic starter |
| Generic PA | 260 | 90 | 1 | 35 | 0 | 0.3 | Generic starter |
| Generic PC | 280 | 105 | 1 | 35 | 0 | 0.2 | Generic starter |
| Generic PETG | 240 | 80 | 1 | 35 | 0 | 0.2 | Generic starter |
| Generic PLA | 210 | 60 | 1 | 35 | 0 | 0.5 | Generic starter |
| Generic TPU | 225 | 50 | 0.8 | 20 | 0 | 0.2 | Generic starter |
| Z-ABS 2 | 275 | 80 | 0.8 | 37 | 0 | 0.2 | Classic / M200 |
| Z-ABS | 275 | 80 | 0.8 | 37 | 0 | 0.2 | Classic / M200 |
| Z-ASA Pro | 255 | 65 | 0.8 | 37 | 0.01 | 0.2 | Classic / M300 |
| Z-ESD | 280 | 70 | 1 | 33 | 0 | 0.6 | Classic / M300 |
| Z-FLEX | 230 | 50 | 2.5 | 20 | 0 | 0.2 | Beta 4 / M300 Plus |
| Z-GLASS | 254 | 30 | 1.5 | 30 | 0.1 | 0.2 | Classic / M300 |
| Z-HIPS | 255 | 80 | 0.5 | 30 | 0 | 0.2 | Classic / M300 |
| Z-NYLON | 250 | 90 | 2.5 | 45 | 0 | 0.3 | Beta 4 / M300 Plus |
| Z-PCABS | 290 | 85 | 0.8 | 37 | 0.0075 | 0.2 | Classic / M200 |
| Z-PEEK | 400 | 105 | 2 | 33 | 0 | 0.6 | Beta 4 / Endureal; INCOMPATIBLE >305 °C |
| Z-PEI 1010 | 370 | 105 | 2 | 17 | 0 | 0.6 | Beta 4 / Endureal; INCOMPATIBLE >305 °C |
| Z-PEI 9085 | 360 | 105 | 0.5 | 33 | 0.1 | 0.6 | Beta 4 / Endureal; INCOMPATIBLE >305 °C |
| Z-PETG | 254 | 30 | 1.5 | 45 | 0.005 | 0.2 | Classic / M300 |
| Z-PHA | 205 | 55 | nil | nil | nil | nil | Project R3 fallback |
| Z-PLA | 210 | 30 | 2 | 21 | 0.035 | 0.6 | Classic / Inventure |
| Z-PLA Pro | 207 | 30 | 1.2 | 37 | 0.03 | 0.5 | Classic / M300 |
| Z-SEMIFLEX | 215 | 10 | 4.5 | 30 | 0 | 1.5 | Classic / Inventure |
| Z-ULTRAT | 253 | 80 | 0.9 | 28 | 0 | 0.2 | Classic / M300 |
| Z-ULTRAT Plus | 225 | 100 | 1 | 30 | 0.01 | 0.6 | Classic / Inventure |

`nil` means inherit a setting from the Printer preset. All entries retain `pressure_advance = 0` until physically tuned. Material feed fields in the source **must not** be copied as Orca flow ratio or MVS. Different polymers, nozzle sizes, and actual filament brands require independent tuning.

**Print-test update:** During the 11 November 2026 Klipper/Orca test, the M300 host log recorded **nozzle 210°C / bed 50°C** for Z-PLA; the printer homed and began printing after the Klipper-side Z-range/mesh fix. The original R7 Z-PLA source bed value shown above is **30°C**, and that distinction must be retained. **Active R7.1 change:** the native Orca Z-PLA **0.4 mm** filament preset now uses **50°C for every plate temperature field**, for both first and subsequent layers; the historical baseline value **30°C remains in the table above**. The other three nozzle-size Z-PLA profiles and every other material retain their previous temperatures. The test does not establish a universal manufacturer recommendation, finished print quality, or safety on other machines. The Klipper-side Z-limit fix is *not* an Orca profile setting.

**Thermal limitations:** Z-PEEK 400°C, Z-PEI 1010 370°C and Z-PEI 9085 360°C are inventory/reference presets only. They exceed the project's 305°C **target** hotend limit and must not be used to print on that configuration. Other listed materials still need nozzle, heater, bed, ventilation, and physical qualification.

## 5. Parameter dictionary: Z-SUITE → OrcaSlicer

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

## 6. Worked conversion

**Source project:** Z-SUITE Classic M300, stock 0.4 nozzle, Z-PLA Pro, displayed layer 0.19 mm, Normal, 20% rectilinear infill.

**Orca 2.5/R7:** Printer **Zortrax M300 Classic**, Variant **0.4**, Filament **Z-PLA Pro @Zortrax M300 0.4**, Process **0.20mm Standard @Zortrax M300 Classic 0.4 nozzle**. Change `Sparse infill density` from the default 15% to **20%**, keep a rectilinear pattern, and compare support/raft/shell values separately. Save the custom process without replacing the system preset. A successful slice is not a physically validated match.

## 7. Sources and validation boundaries

- [Recovered Classic Z-SUITE database](../sources/ZSUITE_classic.json): 448 total entries, 152 `printer=M300` records with 0.4 mm nozzle according to the 11 November extraction; source includes 14 material names (7 Z products + 7 external families). This is not a complete executable OEM toolpath.
- [Recovered beta-4 source](../sources/ZSUITE_beta4.json) and [R6 numerical catalog](../evidence/R6_CATALOG.json): some extra material entries were imported from other printer families and retained for provenance.
- [R7 process catalog](../evidence/R7_PROCESS_CATALOG.json), [R7 validation](../evidence/R7_VALIDATION.json), [R7 builder](../tools/build_classic_r7.py). Historical R7: 138/138 slicing checks, 14 installer tests, Orca 2.5/Linux GUI loader verified 30 processes/104 filaments/four nozzle variants; **no historical validation on user's Mac**.
- [Zortrax Classic specification](https://support.zortrax.com/m-series-specification/) and [Zortrax forum clarification](https://forum.zortrax.com/t/zortrax-m300-print-with-0-6-mm-nozzle/9671): do not treat M300 Plus or Dual nozzle support as Classic support.
- [OrcaSlicer layer-height reference](https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_layer_height).

**Scope rule:** All `position_min`, `safe_z`, `approach_distance`, homing release, and pad-mesh measurement settings are **Klipper host configuration**, not OrcaSlicer printer/filament/process settings. Orca's start code should call `START_PRINT ... MESH=AUTO` and the host must handle the saved mesh.
