# Validation and evidence boundaries

The most recent check can be found in the repository's [GitHub Actions](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Orca-Slicer/actions/workflows/validate.yml). The checked-in [evidence/VALIDATION.json](../evidence/VALIDATION.json) is a dated snapshot and must not be mistaken for R7.2 until its tested commit actually matches the R7.2 source. The CI workflow generates fresh, source-identified evidence, rather than relabeling old passes.

| Check | Establishes | Does not establish |
|---|---|---|
| 140 current preset hashes | R7.2 reviewed profiles and only the intended 12 PLA first-layer overrides | Physical quality |
| Index/field validation | One model, four variants, 30 processes, 104 filaments | Compatibility with untested future slicers |
| Source/table audit | All 152 source combinations retained and current values read from files | Full execution of the OEM slicing pipeline |
| Installer regression tests | Scoped writes, other-printer/global-config preservation, idempotence and rollback in temporary directories | Already-installed state on the user's Mac |
| OrcaSlicer 2.5.0 runtime | 30 process + 104 filament + four PA checks = 138 jobs | 138 physical prints or permission to print PEEK/PEI |
| Linux/Xvfb native GUI loader | Processes/filaments loaded and four variants visible | User's macOS GUI tested |

The workflow never connects to a printer or executes generated G-code. It uses a checksum-pinned Orca 2.5.0 binary. Current unit tests include 14 installer and 15 source/profile contracts. High-temperature reference filaments are sliced only for software inspection.

## Operator evidence — 11 November 2026

The user reported a Benchy starting after a Klipper-side correction. The preceding failure was `Move out of range: 3.000 10.000 -0.089 [0.000]` during purge with an active `m300_pads` mesh. Nominal purge Z=0.28 mm plus a local correction near -0.369 mm was rejected by the former zero lower axis bound.

The operator's final **host** configuration was:

```ini
[stepper_z]
position_min: -0.5

[m300_calibration]
safe_z: 5
approach_distance: 6.5
probe_search_margin: 1
```

These are not Orca settings and are not installed here. They preserve center-contact homing, purge placement and active mesh. A test on one machine does not qualify the mechanical range on all M300 printers. PC7-release clearance is separate.

The recorded print target was Z-PLA / nozzle 0.4 / 210°C nozzle / 50°C bed; the recovered source bed was 30°C. CANCEL_PRINT parked the head and Ready/IDLE was observed. A later successful start was reported. **Print completion and first-layer quality have not been confirmed here.**

## R7.3 selective bed-temperature floors — pending physical confirmation

The change raises only lower existing bed targets (to 40°C initial and 35°C subsequent) in 12 Z-SEMIFLEX, Z-GLASS and Z-PETG nozzle-specific profiles. The five other reviewed materials retain all previous, higher bed values. Other profile parameters, all nozzle temperatures and Klipper are unchanged. CI checks the effective slicing result and later-layer bed-temperature transition. No physical print result is claimed.

## R7.2 first-layer temperature change — pending physical confirmation

For 12 PLA-family filament profiles the requested first-layer target is **230°C nozzle / 70°C bed**. Subsequent-layer temperatures and all other slicer settings remain unchanged from R7.1. This is an adhesion experiment requested after an unsatisfactory first layer, not a proven correction or official manufacturer setting. The active Mac installation is independent of the GitHub repository: update and re-slice locally after the CI pass. If Orca displays a filament temperature range warning at 230°C, check spool documentation before printing.

Historical test results remain in Git history. Current evidence is generated only after the cleaned tree passes static, unit, slicing and loader checks. [Profiles](PROFILES.md) · [crosswalk](ZSUITE_TO_ORCA.md) · [source checksums](../sources/MANIFEST.json).
