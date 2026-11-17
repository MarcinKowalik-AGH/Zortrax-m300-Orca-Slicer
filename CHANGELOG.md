# Current release notes

## R7.4 — M300 Classic perforated bed image

The M300 Classic system model now references `model/Zortrax_M300_Classic_bed.png`, a compact top-down visual representation based on the provided perforated plate photos and generated illustration (128×128 indexed PNG). The macOS installer copies this file to `system/Zortrax/model/` and includes it in normal backup/restore. The image is shared by all four nozzle variants.

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
