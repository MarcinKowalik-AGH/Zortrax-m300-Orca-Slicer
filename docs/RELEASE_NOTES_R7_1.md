# R7.1 maintenance update — English documentation and first-print Z-PLA correction

**Date:** 12 November 2026  
**Scope:** OrcaSlicer M300 Classic profiles only; no Orange Pi, MCU, bootloader, UART, OLED or Klipper host update.

## Verified repository changes

- Main project README and maintained R7 user, installation, and migration documentation are now in **English**. Historical Polish notes remain as a clearly marked source archive; no numerical source evidence was overwritten.
- The [Z-SUITE → OrcaSlicer crosswalk](ZSUITE_TO_ORCA_R7.md) includes every one of the **30 quality processes**, the **26 filament entries** for a 0.4 mm nozzle, the displayed `SliceThickness` distinctions, the complete Z-PLA Pro Normal/High/Draft speed comparison and a parameter dictionary.
- Four native M300 printer variants have clearer **English printer notes**; machine geometry, layer limits, `START_PRINT`/`END_PRINT`, `MESH=AUTO`, pressure-advance behavior and printer-motion parameters have **not** been changed in this update.
- The native vendor index description was clarified and its version changed from `02.05.00.07` to **`02.05.00.08`**.
- The **only changed numeric print setting** is the **Z-PLA filament for 0.4 mm nozzle**: the requested bed temperature for all 12 plate-selector fields (initial and later layers) is now **50°C**, instead of the archived **30°C** baseline. **Nozzle temperature remains 210°C**, and Z-PLA presets for 0.2/0.3/0.6 remain at 30°C. Other filaments remain untouched.
- The `tools/build_classic_r7.py` generator includes this explicit exception so future regeneration will not silently undo the change. The R7 process catalog documents the original and modified targets and the observed first-print test.

## Why the override is limited to this variant

The user's **11 November 2026** host log recorded `hotend=210°C` and `bed=50°C` while trying to print a Benchy with the **0.4 mm** nozzle. Heating and center-contact homing succeeded. The first attempt stopped on a Klipper-side compensated purge Z move (`X3 Y10 Z-0.089` while `position_min=0`). After the qualified machine's Klipper config was adjusted to `position_min: -0.5`, `safe_z: 5` and `approach_distance: 6.5`, the user confirmed that the print began.

This is **evidence of a start**, not a validated finished print, ideal adhesion, or a manufacturer's recommended Z-PLA platform temperature. The historical Z-SUITE/R6 temperature **30°C** is kept in the source files and migration table. Do not automatically propagate the 50°C exception to other printer/nozzle combinations.

## Validation and deployment

The original R7 software baseline has historical evidence of **138/138 slicing** and **14 installer** tests, plus the Orca 2.5 Linux/Xvfb native-loader check. Those historical results predate this R7.1 override and **must not be relabeled as new R7.1 runtime validation**.

The generator, native vendor index, and profile JSONs are updated together; check them with `python3 tools/build_classic_r7.py --check` and the existing repository tests and workflow before treating R7.1 as a new software test pass. The user must install updated slicer presets on the **local Mac while Orca is closed**; GitHub changes do not automatically change the running Mac app. Never run an installer, firmware flashing, or Klipper restart during a print.

**Keep the host/slicer boundary:** negative Z compensation, PC7 release, 5 mm homing clearance, safe M07 travel, bed-mesh measurement and firmware limits belong to the **separate Klipper M300 repository**. Orca does not set them.

[README](../README.md) · [R7 profile guide](PROFILE_GUIDE_R7.md) · [Z-SUITE crosswalk](ZSUITE_TO_ORCA_R7.md) · [install guide](INSTALL_R7.md).
