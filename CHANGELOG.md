# Current release notes

## R7.10 — gold pads with measured 210 mm inner gap; no rear white strip (17 November 2026)

The operator measured a **210 mm free distance between inner edges** of the four 60 × 60 mm golden corner pads, on both X and Y. The pads are now symmetrically located 15 mm from the physical 360 mm sheet edges: X/Y 15…75 and 285…345 mm. This replaces screenshot-guessed pad offsets from R7.9. The 50 × 50 mm centre pad remains unchanged.

The interactive `bed_custom_texture` is an exact 300 × 305 mm crop of the physical plate, not a scaled 360 mm image. The two **rear gold pads begin at texture `y=0`**. The false light/silver gap between the dark non-printable STL margin and the gold pads is eliminated. The reference full-bed SVG uses the same measured pad coordinates.

No STL model, 16 perimeter Allen screws, 3 mm metal thickness, electrical connector, printing limits, 140 native system JSON profiles, Klipper, G-code or filament/process settings were changed. The request for a 15% lighter external STL area remains subject to the documented stock Orca 2.5 renderer limitation.

## R7.9 — perimeter Allen screws corrected; truthful no-op install (17 November 2026)

Rectified the original Zortrax plate photo and compared it with the operator's screw close-ups. The prior 16 screw head centres were approximately 17 mm from metal edges, incorrectly placing them near the perforations. The physical outer border's screws are now drawn **~6 mm from the flange**, on five approximately equally spaced stations per outer side (16 unique screws total). A 24-facet circular head now has a **recessed, six-sided Allen socket** in the actual generated STL. Locations are photographic estimates, not caliper-measured hole coordinates.

**The requested excluded-zone tint is not implemented in the stock OrcaSlicer GUI:** version 2.5 hardcodes a dark custom-bed STL color (`Bed3D::DEFAULT_MODEL_COLOR`), while the custom SVG texture is cropped to the real 300 × 305 mm bed polygon. The [full-plate diagram](docs/Zortrax_M300_360mm_plate_layout.svg) now includes a **15% darkening overlay as a labelled visual reference only**, not as a claim that the printer preset changed the application renderer. We explicitly do not extend printable geometry to 360 × 360 mm.

The Mac installer now only purges `system/Zortrax.opc` when an actual profile/resource file changes, and prints the detected revision. No-op `--apply` no longer creates an empty backup and false "archived cache" status. No Klipper, 300 × 305 mm limits, homing, G-code, filament/process or other printer data changes.

## R7.8 — 3 mm-thick plate and rear electrical connector (17 November 2026)

Based on six operator photographs of the real M300 Classic bed and a centimetre ruler, the generated visual STL now represents the **entire 360 × 360 mm sheet at 3 mm thickness**. The visible outer surround retains perforations, while the central footprint gains solid backing beneath the separate gold-and-silver perforated SVG. The visual model is aligned below Orca's printable-plane overlay so it does not intentionally obscure the image.

The rear socket is now centred about **148 mm from the plate's left edge**, not near the right rear corner as guessed from the original product photo. It has an approximately **8.5 mm housing**, **12 mm width including metal solder tabs**, **5.4 mm inboard depth** and **1.6 mm rear protrusion**. A low rectangular housing, five top ribs, solder wings and front latch are included in the STL. **Socket height (~3.2 mm) is estimated from perspective only** and has not been measured with a calliper. Model is colourless STL, so the cream colour is not represented.

This release changes only generated visual STL, its Python generator, structural tests, documentation, and metadata. The exact **300 × 305 mm** functional Orca print polygon, Klipper motion limits, Y=315 service-only travel, homing, mesh, temperatures and G-code remain unchanged.

## R7.7 — measured 360 mm bed; true 300 × 305 mm print polygon (17 November 2026)

The operator measured **physical plate 360 × 360 mm**, perforation margins **14/14 mm X**, **15 mm front**, **16 mm rear**, gold corner contacts **60 × 60 mm**, centre **50 × 50 mm**. The resulting perforated field is **332 × 329 mm**. The initial "200 mm backward" description was corrected to **155 mm behind the plate centre**, so safe placement spans **X ±150 mm**, **Y −150…+155 mm**.

Previously the four Orca JSON machine presets used Y=300. These four `printable_area` top corners now use **Y=305**, matching the operator-confirmed Klipper safe Y limit, with X=300 unchanged. No mesh, heaters, motion or G-code edits, and no use of Y=315 for printing. The real plate extends 30 mm beyond printable X on either side, 30 mm beyond printable Y at the front, and 25 mm beyond at the rear.

New SVG is a 300 × 305 mm precisely scaled **crop** of the larger physical plate, with mathematically regular circular perforations including the golden pads. A separate non-printable 360 × 360 mm **STL frame and exterior perforations** is generated on the user's Mac by the installer from `tools/bed_geometry.py` (Python standard library). All four installed nozzle variants point at absolute local SVG and STL paths. A full physical bed layout and printable boundary reference is in [docs/Zortrax_M300_360mm_plate_layout.svg](docs/Zortrax_M300_360mm_plate_layout.svg). Gold pad dimensions are measured; corner pad placement is visually approximated pending positional measurements.

The boundary is functional `printable_area`, **not merely a red line drawn over an illegally enlarged printable surface**. The STL is purely visual. Existing non-M300 printers and `OrcaSlicer.conf` remain preserved; Mac installer backup/restore includes both visual assets. Native slicer and macOS appearance should be visually checked on the user's machine.

## R7.6 — flat perforated gold pads, proper Allen screws (17 November 2026)

Corrected the screenshot-confirmed faults in R7.5. The gold pads previously covered the circular perforations; bolts were drawn like cross-head screws; the inner perforated region had a misleading recessed edge; the image had transparent side margins. The new SVG has an **opaque full-bleed image**, **12,100 mathematically circular holes on a 110×110 grid at pitch 9.6**, **five flush perforated golden pads**, **18 Allen bolts**, and **two solid non-perforated screw collars** in the middle. The SVG is reproducibly generated by `tools/generate_bed_texture.js`.

Orca's dark grid outside the 300×300 mm printable square is drawn by the slicer and cannot be overwritten by the texture. Hide gridlines through **View → Show Gridlines** if desired; keep functional `printable_area` unchanged. No hotend, heater, fan, filament, G-code, motion, Orange Pi or Klipper values were changed. SVG visual rendering (Inkscape) and structural geometry checks passed; final visual acceptance on macOS Orca 2.5 is pending.

## R7.5 — genuine vector Zortrax M300 Classic platform

Replaced the blurry 128×128-pixel platform PNG with a native **SVG vector design** matching the preferred silver-and-gold artwork. All **11,556 perforations are exact circles on a 9.6-unit square lattice**, rather than warped or irregular dots. The artwork retains the five golden contact pads, symmetrical metal frame and machined fasteners.

The installer deploys the SVG file into Orca's vendor resource directory and writes the absolute SVG file path into `bed_custom_texture` for each installed M300 printer variant. The 300×300 mm print area, all physical machine properties, all print/filament/process data and Klipper are unchanged. The previous tiny PNG remains only in the Git history.


## R7.4.1 — fix Bed Shape “Texture: None” on macOS

Previous R7.4 installed `model/Zortrax_M300_Classic_bed.png` as a vendor asset and referenced it in the common printer-model metadata; however, the **per-nozzle `bed_custom_texture` fields were empty**. OrcaSlicer 2.5 uses those fields for the **Bed Shape → Texture** selection, so the image was not indicated in the UI.

The installer now substitutes the **absolute pathname in the active Mac's OrcaSlicer configuration directory** for all four installed nozzle variants, while the source profiles remain portable. No usernames, manual file selection, global `OrcaSlicer.conf` changes or host edits. Regression and CI GUI-loader checks assert that the installed PNG exists at those paths. Print settings remain identical to R7.4.


## R7.4 — M300 Classic perforated bed image

The M300 Classic system model now references `model/Zortrax_M300_Classic_bed.png`, a compact top-down visual representation based on the provided perforated plate photos and generated illustration (128×128 indexed PNG). The macOS installer copies this file to `vendor/Zortrax/model/` and includes it in normal backup/restore. The image is shared by all four nozzle variants.

**Only the visual bed texture and vendor release metadata changed.** No heater, motion, filament, G-code, support, raft or Klipper settings were changed. After updating on the Mac, restart OrcaSlicer to see the bed.


## R7.3 — bed-temperature floors, 17 November 2026

Only Z-SEMIFLEX, Z-GLASS and Z-PETG were below the requested minima. For all four nozzle variants, first-layer bed temperature is now **40°C** and later layers **35°C**, for a total of 12 affected profiles. This is strictly an *increase-only* correction.

Five other reviewed materials remain at their higher values: Z-PHA 55/55°C, Generic TPU 50/50°C, Z-FLEX 50/50°C, Z-ASA Pro 65/65°C, Z-ULTRAT Plus 100/100°C. No nozzle temperatures, speeds, filament properties, pressure advance, motion/raft settings, other presets or Klipper components were changed. Previous R7.2 PLA first-layer settings remain in force.

These new floors are experimental and require physical print verification; they are not official Zortrax material prescriptions.


## R7.2 — PLA first-layer adhesion trial, 17 November 2026

Only the first-layer hotend and bed settings have changed in 12 native PLA-family filament presets: **Z-PLA**, **Z-PLA Pro**, and **Generic PLA** for all four supported nozzle sizes (0.2/0.3/0.4/0.6 mm). The first layer requests **230°C / 70°C**. All later-layer temperatures, IDs, printer/process geometry, cooling, speeds, retractions, flow/PA and Klipper start/end macros are unchanged.

This is an operator-requested test, **not verified finished-print quality or a manufacturer-certified calibration**. Original Z-SUITE source values are preserved. The 0.4 mm Z-PLA later-layer temperature remains 210°C / 50°C; all other nozzle/material later-layer temperatures retain their R7.1 values. The vendor index version is updated to **02.05.00.09**. The 12 affected filament JSONs and index are the only modified profile files; 127 others are byte-identical.

After installing R7.2 in Orca on the Mac, select the appropriate PLA filament and **re-slice** before uploading a new G-code file. Do not update the Orange Pi, Klipper or MCU as part of this profile change.

## R7.1 — current-only repository cleanup, 12 November 2026

This is a repository/documentation cleanup, not a new numerical print calibration. All 140 current profile JSON files, identities and settings match the baseline commit `18d68bb161631004e6909a0f7585fe552b15b302` byte-for-byte.

The current tree now contains one `profiles/` directory, one English `install.py`, one validation workflow, current test evidence and English documentation. Old R3–R6 bundles, duplicate native directories, obsolete generators, repair installers, Polish manuals and historical test summaries were removed from the working tree. They remain in Git history; no history rewrite or host-repository modification was performed.

The migration reference is generated from actual source and preset files. It contains 30 process rows, 104 filament/nozzle rows, all 152 recovered Classic M300 combinations and 18 PLA Pro feature-speed comparisons. Source/displayed heights, other-printer origins, missing equivalents, shell-mode limitations and source/current temperatures are explicit.

The safe installer retains its transaction, backup format and preservation of other printers and OrcaSlicer.conf. Only its entry point/source path and messages changed. Installation must happen locally on a Mac with Orca closed; cleanup does not install anything on the user's computer.

The pre-existing 0.4 mm Z-PLA 50°C bed override remains distinguished from its 30°C source. PA remains zero; high-temperature references remain visible but unqualified. Fresh software checks are recorded in [current evidence](evidence/VALIDATION.json), not copied from older pass summaries.

[README](README.md) · [crosswalk](docs/ZSUITE_TO_ORCA.md).
