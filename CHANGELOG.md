# Current release notes

## R7.1 — current-only repository cleanup, 12 November 2026

This is a repository/documentation cleanup, not a new numerical print calibration. All 140 current profile JSON files, identities and settings match the baseline commit `18d68bb161631004e6909a0f7585fe552b15b302` byte-for-byte.

The current tree now contains one `profiles/` directory, one English `install.py`, one validation workflow, current test evidence and English documentation. Old R3–R6 bundles, duplicate native directories, obsolete generators, repair installers, Polish manuals and historical test summaries were removed from the working tree. They remain in Git history; no history rewrite or host-repository modification was performed.

The migration reference is generated from actual source and preset files. It contains 30 process rows, 104 filament/nozzle rows, all 152 recovered Classic M300 combinations and 18 PLA Pro feature-speed comparisons. Source/displayed heights, other-printer origins, missing equivalents, shell-mode limitations and source/current temperatures are explicit.

The safe installer retains its transaction, backup format and preservation of other printers and OrcaSlicer.conf. Only its entry point/source path and messages changed. Installation must happen locally on a Mac with Orca closed; cleanup does not install anything on the user's computer.

The pre-existing 0.4 mm Z-PLA 50°C bed override remains distinguished from its 30°C source. PA remains zero; high-temperature references remain visible but unqualified. Fresh software checks are recorded in [current evidence](evidence/VALIDATION.json), not copied from older pass summaries.

[README](README.md) · [crosswalk](docs/ZSUITE_TO_ORCA.md).
