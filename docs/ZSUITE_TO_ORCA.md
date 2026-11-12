# Z-SUITE → OrcaSlicer: M300 Classic migration tables

**Current profile set: R7.1 · OrcaSlicer target: 2.5.0.** Values below are generated from committed source records and current preset files, not remembered defaults. Source terminology is preserved: **material, displayed layer, quality and infill mode**. An original Z-SUITE selection is split between **Printer/Variant**, **Filament** and **Process** in Orca.

**There is no complete 1:1 conversion.** A recovered source field, a matching numerical value and a recommended functional process are three different claims. Neither field recovery nor an individual match proves identical toolpaths or print quality. Process suggestions are explicitly project judgments.

## 1. Practical process crosswalk — physically installed 0.4 mm nozzle

The recovered Classic M300 records contain only a **0.4 mm nozzle**. Other Orca variants are project adaptations; M300 Plus/Dual support is not evidence of Classic support.

| Z-SUITE selection | Displayed mm | Recovered SliceThickness mm | Suggested Orca process | Orca mm | Difference / action |
| --- | --- | --- | --- | --- | --- |
| 0.09 High/Normal | 0.09 | 0.1 | 0.08mm SuperDetail | 0.08 | Thinner functional approximation; no supplied 0.09/0.10 process for nozzle 0.4. |
| 0.14 High | 0.14 | 0.15 | 0.12mm Detail | 0.12 | Thinner approximation, not the recovered High mode. |
| 0.14 Normal/Default | 0.14 | 0.15 | 0.16mm Optimal | 0.16 | Slightly thicker; use a custom 0.14/0.15 process for the chosen numerical target. |
| 0.19 Normal/Default | 0.19 | 0.2 | 0.20mm Standard | 0.2 | Best starting point; six speed fields match only the cited PLA Pro Normal example. |
| 0.19 High | 0.19 | 0.2 | 0.20mm High Quality | 0.2 | Functional equivalent only; three walls and different speeds. |
| 0.19 Draft | 0.19 | 0.2 | 0.20mm Standard | 0.2 | No 0.20 Draft preset; save a copy and compare material-specific speeds. |
| 0.29 Normal/Draft | 0.29 | 0.3 | 0.28mm SuperDraft | 0.28 | Coarse approximation; default infill is 10%, not the Z-SUITE project percentage. |
| 0.39 external ABS-family records | 0.39 | 0.39 | None for nozzle 0.4 | — | Only two source records; do not silently change the physical nozzle. |

The **SliceThickness column is a recovered configuration field**, not a measurement or proof that the UI label was wrong. Keep 0.09/0.14/0.19/0.29 labels separate from 0.10/0.15/0.20/0.30 fields. To preserve one numeric height, save a user copy and set it explicitly; still review first-layer height, raft gap, shells and speeds.

## 2. Which source material selections exist for Classic M300?

The Classic extraction has **152 M300 records** covering **seven named Z materials and seven external families**. Counts include Standard/Shell modes and multiple qualities; they are not 152 independent polymers. Generic is a starting template, not a copied external-material calibration.

| Z-SUITE material/family | Displayed layers mm | Source qualities | Records | Orca filament / action |
| --- | --- | --- | --- | --- |
| ABS-based filament | 0.09, 0.14, 0.19, 0.29, 0.39 | Default | 10 | Generic ABS @Zortrax M300 0.4 |
| ESD v2-based filament | 0.09, 0.14, 0.19 | Default | 6 | No direct Generic; create a separately qualified custom filament |
| GLASS-type filament | 0.14, 0.19, 0.29 | Default | 5 | No direct Generic; create a separately qualified custom filament |
| HIPS-based filament | 0.09, 0.14, 0.19, 0.29 | Default | 7 | No direct Generic; create a separately qualified custom filament |
| PCABS-based filament | 0.14, 0.19, 0.29 | Default | 6 | No direct Generic; create a separately qualified custom filament |
| PETG-based filament | 0.14, 0.19 | Default | 4 | Generic PETG @Zortrax M300 0.4 |
| PLA-based filament | 0.09, 0.14, 0.19, 0.29 | Default | 8 | Generic PLA @Zortrax M300 0.4 |
| Z-ASA Pro | 0.09, 0.14, 0.19, 0.29 | High, Normal | 16 | Z-ASA Pro @Zortrax M300 0.4 |
| Z-ESD | 0.09, 0.14, 0.19 | Draft, High, Normal | 10 | Z-ESD @Zortrax M300 0.4 |
| Z-GLASS | 0.14, 0.19, 0.29 | Draft, High, Normal | 15 | Z-GLASS @Zortrax M300 0.4 |
| Z-HIPS | 0.09, 0.14, 0.19, 0.29 | Draft, High, Normal | 21 | Z-HIPS @Zortrax M300 0.4 |
| Z-PETG | 0.14, 0.19 | Draft, High, Normal | 12 | Z-PETG @Zortrax M300 0.4 |
| Z-PLA Pro | 0.09, 0.14, 0.19, 0.29 | Draft, High, Normal | 18 | Z-PLA Pro @Zortrax M300 0.4 |
| Z-ULTRAT | 0.09, 0.14, 0.19, 0.29 | High, Normal | 14 | Z-ULTRAT @Zortrax M300 0.4 |

Do not silently relabel GLASS-type, ESD v2-based or PCABS-based as Generic PETG, Generic PLA or Generic PC. No exact supplied Generic counterpart is claimed. **Z-PLA and Z-PLA Pro are separate materials.**

## 3. All 30 current processes

Full names append `@Zortrax M300 Classic <diameter> nozzle`. Speeds are nominal stored mm/s, not observed motion. Process geometry, walls, fill, speeds, accelerations, raft and supports depend on nozzle, not only layer height. A 0.16 mm layer exists for all four nozzle sizes; a 0.20 mm process is not supplied for a 0.2 mm nozzle.

| Nozzle mm | Process | Layer mm | Walls | Infill | Outer mm/s | Top mm/s | Raft gap mm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.2 | 0.06mm Fine | 0.06 | 2 | 15% rectilinear | 12.833333 | 46.666667 | 0.06 |
| 0.2 | 0.08mm SuperDetail | 0.08 | 2 | 15% rectilinear | 12.833333 | 46.666667 | 0.08 |
| 0.2 | 0.10mm Standard | 0.1 | 2 | 15% rectilinear | 18.333333 | 66.666667 | 0.1 |
| 0.2 | 0.12mm Detail | 0.12 | 2 | 15% rectilinear | 15.583333 | 56.666667 | 0.12 |
| 0.2 | 0.16mm Optimal | 0.16 | 2 | 15% rectilinear | 16.5 | 60 | 0.15 |
| 0.3 | 0.08mm SuperDetail | 0.08 | 2 | 15% rectilinear | 16.333333 | 28 | 0.08 |
| 0.3 | 0.12mm Detail | 0.12 | 2 | 15% rectilinear | 19.833333 | 34 | 0.12 |
| 0.3 | 0.16mm Optimal | 0.16 | 2 | 15% rectilinear | 21 | 36 | 0.15 |
| 0.3 | 0.20mm High Quality | 0.2 | 3 | 15% rectilinear | 17.5 | 20 | 0.15 |
| 0.3 | 0.20mm Standard | 0.2 | 2 | 15% rectilinear | 23.333333 | 40 | 0.15 |
| 0.3 | 0.20mm Strength | 0.2 | 4 | 40% gyroid | 23.333333 | 40 | 0.15 |
| 0.3 | 0.24mm Draft | 0.24 | 2 | 10% rectilinear | 23.333333 | 40 | 0.15 |
| 0.4 | 0.08mm SuperDetail | 0.08 | 2 | 15% rectilinear | 16.333333 | 28 | 0.08 |
| 0.4 | 0.12mm Detail | 0.12 | 2 | 15% rectilinear | 19.833333 | 34 | 0.12 |
| 0.4 | 0.16mm Optimal | 0.16 | 2 | 15% rectilinear | 21 | 36 | 0.15 |
| 0.4 | 0.20mm High Quality | 0.2 | 3 | 15% rectilinear | 17.5 | 20 | 0.15 |
| 0.4 | 0.20mm Standard | 0.2 | 2 | 15% rectilinear | 23.333333 | 40 | 0.15 |
| 0.4 | 0.20mm Strength | 0.2 | 4 | 40% gyroid | 23.333333 | 40 | 0.15 |
| 0.4 | 0.24mm Draft | 0.24 | 2 | 10% rectilinear | 23.333333 | 40 | 0.15 |
| 0.4 | 0.28mm SuperDraft | 0.28 | 2 | 10% rectilinear | 23.333333 | 40 | 0.15 |
| 0.6 | 0.12mm Detail | 0.12 | 2 | 15% rectilinear | 19.833333 | 34 | 0.12 |
| 0.6 | 0.16mm Optimal | 0.16 | 2 | 15% rectilinear | 21 | 36 | 0.15 |
| 0.6 | 0.20mm High Quality | 0.2 | 3 | 15% rectilinear | 17.5 | 20 | 0.15 |
| 0.6 | 0.20mm Standard | 0.2 | 2 | 15% rectilinear | 23.333333 | 40 | 0.15 |
| 0.6 | 0.20mm Strength | 0.2 | 4 | 40% gyroid | 23.333333 | 40 | 0.15 |
| 0.6 | 0.24mm Draft | 0.24 | 2 | 10% rectilinear | 23.333333 | 40 | 0.15 |
| 0.6 | 0.28mm SuperDraft | 0.28 | 2 | 10% rectilinear | 23.333333 | 40 | 0.15 |
| 0.6 | 0.32mm Coarse | 0.32 | 2 | 10% rectilinear | 23.333333 | 40 | 0.15 |
| 0.6 | 0.36mm Draft | 0.36 | 2 | 10% rectilinear | 23.333333 | 40 | 0.15 |
| 0.6 | 0.42mm SuperDraft | 0.42 | 2 | 10% rectilinear | 23.333333 | 40 | 0.15 |

The [complete process CSV](tables/processes.csv) also contains widths, six speed categories, accelerations, shell counts/thicknesses, support type and first-layer height. High Quality is not the source High table; Strength is 40% gyroid/four walls, not Solid/100%; Draft also changes layer and shell/fill values.

## 4. Speed comparison: Z-PLA Pro, nozzle 0.4, displayed layer 0.19

Recovered `SliceThickness` is approximately 0.20 mm. This example uses **Standard infill mode**. Source mm/min values are divided by 60 and rounded here for readability.

| Source quality | Orca process | Feature | Source mm/min | Source mm/s | Orca mm/s | Difference mm/s |
| --- | --- | --- | --- | --- | --- | --- |
| Normal | 0.20mm Standard | Outer wall | 1400 | 23.333333 | 23.333333 | -0 |
| Normal | 0.20mm Standard | Inner wall | 3000 | 50 | 50 | 0 |
| Normal | 0.20mm Standard | Sparse infill | 3000 | 50 | 50 | 0 |
| Normal | 0.20mm Standard | Top surface | 2400 | 40 | 40 | 0 |
| Normal | 0.20mm Standard | Bridge | 4000 | 66.666667 | 66.666667 | 0 |
| Normal | 0.20mm Standard | Travel | 7200 | 120 | 120 | 0 |
| High | 0.20mm High Quality | Outer wall | 1200 | 20 | 17.5 | -2.5 |
| High | 0.20mm High Quality | Inner wall | 2400 | 40 | 50 | 10 |
| High | 0.20mm High Quality | Sparse infill | 2400 | 40 | 50 | 10 |
| High | 0.20mm High Quality | Top surface | 1800 | 30 | 20 | -10 |
| High | 0.20mm High Quality | Bridge | 2000 | 33.333333 | 66.666667 | 33.333334 |
| High | 0.20mm High Quality | Travel | 4800 | 80 | 120 | 40 |
| Draft | 0.20mm Standard | Outer wall | 1500 | 25 | 23.333333 | -1.666667 |
| Draft | 0.20mm Standard | Inner wall | 3200 | 53.333333 | 50 | -3.333333 |
| Draft | 0.20mm Standard | Sparse infill | 3200 | 53.333333 | 50 | -3.333333 |
| Draft | 0.20mm Standard | Top surface | 4000 | 66.666667 | 40 | -26.666667 |
| Draft | 0.20mm Standard | Bridge | 4000 | 66.666667 | 66.666667 | 0 |
| Draft | 0.20mm Standard | Travel | 9000 | 150 | 120 | -30 |

All six listed **Normal** speeds match the Standard process in this example only. High Quality and Draft do not. Other source materials have different speed tables. Selecting a different Filament does **not** automatically replace the shared Process speeds. The shared quality family cannot simultaneously reproduce every source material's modes.

## 5. Zortrax filament table — exact selected source versus current values

This table is for **nozzle 0.4 mm**. Source temperatures come from the exact selected record identified by the retained provenance, not generic manufacturer guidance. Other-model origins (M200, Inventure, M300Plus, Endureal) are labeled rather than claimed as Classic OEM settings. Missing data mean not recovered, not zero.

| Material | Actual source | Source nozzle °C | Source bed °C | Current nozzle °C | Current bed °C | Qualification |
| --- | --- | --- | --- | --- | --- | --- |
| Z-ABS 2 | classic / M200 | 275 | 80 | 275 | 80 | Not physically qualified |
| Z-ABS | classic / M200 | 275 | 80 | 275 | 80 | Not physically qualified |
| Z-ASA Pro | classic / M300 | 255 | 65 | 255 | 65 | Not physically qualified |
| Z-ESD | classic / M300 | 280 | 70 | 280 | 70 | Not physically qualified |
| Z-FLEX | beta4 / M300Plus | 230 | 50 | 230 | 50 | Not physically qualified |
| Z-GLASS | classic / M300 | 254 | 30 | 254 | 30 | Not physically qualified |
| Z-HIPS | classic / M300 | 255 | 80 | 255 | 80 | Not physically qualified |
| Z-NYLON | beta4 / M300Plus | 250 | 90 | 250 | 90 | Not physically qualified |
| Z-PCABS | classic / M200 | 290 | 85 | 290 | 85 | Not physically qualified |
| Z-PEEK | beta4 / Endureal | 400 | 120 | 400 | 105 | REFERENCE ONLY >305C |
| Z-PEI 1010 | beta4 / Endureal | 370 | 200 | 370 | 105 | REFERENCE ONLY >305C |
| Z-PEI 9085 | beta4 / Endureal | 360 | 200 | 360 | 105 | REFERENCE ONLY >305C |
| Z-PETG | classic / M300 | 254 | 30 | 254 | 30 | Not physically qualified |
| Z-PHA | Project fallback / no named source table recovered | not recovered | not recovered | 205 | 55 | Not physically qualified |
| Z-PLA | classic / Inventure | 210 | 30 | 210 | 50 | Not physically qualified |
| Z-PLA Pro | classic / M300 | 207 | 30 | 207 | 30 | Not physically qualified |
| Z-SEMIFLEX | classic / Inventure | 215 | 10 | 215 | 10 | Not physically qualified |
| Z-ULTRAT | classic / M300 | 253 | 80 | 253 | 80 | Not physically qualified |
| Z-ULTRAT Plus | classic / Inventure | 225 | 100 | 225 | 100 | Not physically qualified |

**Z-PLA 0.4 exception:** 50°C bed replaces the 30°C source baseline based on one user-reported print start at 210/50°C. The other three Z-PLA nozzle presets retain 30°C. This is not a completed-print test or universal manufacturer recommendation. Cleanup changes none of these values.

**PEEK/PEI references:** 400/370/360°C exceed the stated 305°C hotend target limit, and source bed/chamber requirements may also exceed the setup. A capped 105°C profile bed setting does not qualify the material. Do not send these reference-only presets to this host.

## 6. Filament tuning values — all 26 names for nozzle 0.4

`nil` overrides are resolved from the corresponding Printer preset in this table. Flow ratio, MVS and PA are project values, not direct conversions of source `...Feed` fields. Distances are mm; speed is mm/s; MVS is mm³/s.

| Material | Flow | MVS | PA | Retract mm | Retract mm/s | Return mm/s | Extra return mm | Z-hop mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Generic ABS | 1 | 8 | 0 | 1 | 35 | 35 | 0 | 0.2 |
| Generic ASA | 1 | 8 | 0 | 1 | 35 | 35 | 0 | 0.2 |
| Generic PA | 1 | 6 | 0 | 1 | 35 | 35 | 0 | 0.3 |
| Generic PC | 1 | 6 | 0 | 1 | 35 | 35 | 0 | 0.2 |
| Generic PETG | 1 | 6 | 0 | 1 | 35 | 35 | 0 | 0.2 |
| Generic PLA | 1 | 8 | 0 | 1 | 35 | 35 | 0 | 0.5 |
| Generic TPU | 1 | 3 | 0 | 0.8 | 20 | 20 | 0 | 0.2 |
| Z-ABS 2 | 0.926 | 8 | 0 | 0.8 | 37 | 37 | 0 | 0.2 |
| Z-ABS | 0.926 | 8 | 0 | 0.8 | 37 | 37 | 0 | 0.2 |
| Z-ASA Pro | 0.95 | 8 | 0 | 0.8 | 37 | 37 | 0.01 | 0.2 |
| Z-ESD | 0.97 | 8 | 0 | 1 | 33 | 33 | 0 | 0.6 |
| Z-FLEX | 1 | 4 | 0 | 2.5 | 20 | 20 | 0 | 0.2 |
| Z-GLASS | 0.97 | 8 | 0 | 1.5 | 30 | 30 | 0.1 | 0.2 |
| Z-HIPS | 0.95 | 8 | 0 | 0.5 | 30 | 30 | 0 | 0.2 |
| Z-NYLON | 0.95 | 8 | 0 | 2.5 | 45 | 45 | 0 | 0.3 |
| Z-PCABS | 0.94 | 8 | 0 | 0.8 | 37 | 37 | 0.0075 | 0.2 |
| Z-PEEK | 0.95 | 1 | 0 | 2 | 33 | 33 | 0 | 0.6 |
| Z-PEI 1010 | 0.95 | 1 | 0 | 2 | 17 | 17 | 0 | 0.6 |
| Z-PEI 9085 | 0.95 | 1 | 0 | 0.5 | 33 | 33 | 0.1 | 0.6 |
| Z-PETG | 0.97 | 8 | 0 | 1.5 | 45 | 45 | 0.005 | 0.2 |
| Z-PHA | 0.98 | 8 | 0 | 1.0 | 35 | 35 | 0 | 0.4 |
| Z-PLA | 0.98 | 8 | 0 | 2 | 21 | 20 | 0.035 | 0.6 |
| Z-PLA Pro | 0.98 | 8 | 0 | 1.2 | 37 | 37 | 0.03 | 0.5 |
| Z-SEMIFLEX | 1 | 2 | 0 | 4.5 | 30 | 20 | 0 | 1.5 |
| Z-ULTRAT | 0.926 | 8 | 0 | 0.9 | 28 | 28 | 0 | 0.2 |
| Z-ULTRAT Plus | 0.926 | 8 | 0 | 1 | 30 | 30 | 0.01 | 0.6 |

The [104-row filament CSV](tables/filaments.csv) covers every nozzle size and complete name. The Generic families are PLA/PETG/ABS/ASA/TPU/PA/PC, not brand calibrations. Use Save As for SUNLU or another brand, preserve printer compatibility, and tune the actual spool/nozzle. No dedicated Z-SUPPORT preset is supplied; ordinary same-material support geometry remains available.

## 7. All 152 source combinations, record by record

The [correspondence CSV](tables/zsuite_m300_correspondence.csv) preserves each source array index, material, nozzle, displayed height, `SliceThickness`, quality and infill mode. Each row pairs a suggested current process/filament (or an explicit no-match) with source/current temperatures and six source/current speed categories. Shell rows require manual shell/fill choices; the suggestion is not a completed Shell conversion.

**Example:** Classic M300 / 0.4 / Z-PLA Pro / displayed 0.19 / Normal / 20% rectilinear → `Z-PLA Pro @Zortrax M300 0.4` and `0.20mm Standard @Zortrax M300 Classic 0.4 nozzle`, with infill explicitly changed **15% → 20%** and actual shells/supports/raft reviewed. The 20% is a project example, not recovered from the Standard label.

## 8. Evidence and unresolved mappings

Sources: [Classic records](../sources/zsuite_classic.json), [beta-4 records](../sources/zsuite_beta4.json), [current filament provenance](../sources/filament_provenance.json), [checksums](../sources/MANIFEST.json), [current profiles](../profiles/). Raw evidence can mention other printers or support materials; it does not add installable presets.

The extraction did not execute the full OEM slicing pipeline. Records alone cannot prove identical raft zones, feed semantics, shells, seams or firmware behavior. Missing mappings are not invented. See the [settings dictionary](SETTINGS_REFERENCE.md), [profile guide](PROFILES.md) and [validation scope](VALIDATION.md). Regenerate tables with `python3 tools/catalog.py`; use `--check` to verify without writing.
