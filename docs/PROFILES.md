# Zortrax M300 Classic — native OrcaSlicer R7 profiles

## Preset organization

OrcaSlicer 2.5 shows **one printer model** named **Zortrax M300 Classic**, and a **nozzle Variant** selector of **0.2 / 0.3 / 0.4 / 0.6 mm**. Four internal `machine` JSON files describe the four physically interchangeable nozzle configurations, not four unrelated printer models. Do not change the selected diameter unless the installed nozzle and the host's `[extruder] nozzle_diameter` actually match it.

The original M300 **Classic** Z-SUITE supports the stock 0.4 mm nozzle. The additional variants are community-engineered for Klipper, not official Classic presets. This is distinct from M300 Plus and M300 Dual.

## Print quality matrix

| Nozzle | Delivered processes | Count |
|---|---|---:|
| 0.2 mm | 0.06 Fine · 0.08 SuperDetail · 0.10 Standard · 0.12 Detail · 0.16 Optimal | 5 |
| 0.3 mm | 0.08 SuperDetail · 0.12 Detail · 0.16 Optimal · 0.20 High Quality / Standard / Strength · 0.24 Draft | 7 |
| 0.4 mm | 0.08 SuperDetail · 0.12 Detail · 0.16 Optimal · 0.20 High Quality / Standard / Strength · 0.24 Draft · 0.28 SuperDraft | 8 |
| 0.6 mm | 0.12 Detail · 0.16 Optimal · 0.20 High Quality / Standard / Strength · 0.24 Draft · 0.28 SuperDraft · 0.32 Coarse · 0.36 Draft · 0.42 SuperDraft | 10 |

A `0.20mm High Quality` or `0.20mm Strength` preset is not simply a different layer height. High Quality has **3 walls** and slower outer/top surfaces; Standard has **2 walls and 15% infill**; Strength has **4 walls and 40% gyroid infill**. Draft/SuperDraft use **10% infill** in the project defaults. Do not automatically map the Z-SUITE Solid setting to Strength.

The standard 0.4 mm process contains **0.20 mm layers**, line widths **0.44 mm outer / 0.48 mm inner**, first-layer width **0.50 mm**, a **2-layer raft**, and source-derived nominal speeds. Process-first-layer and raft-contact gaps are adjusted for small nozzle/layer variants rather than copying a 0.15 mm gap into all very thin layers. Raft removability and first-layer quality require physical checks.

See the [full 30-row process matrix and source-speed comparison](ZSUITE_TO_ORCA.md).

## Filament matrix and material provenance

There are **26 material names per nozzle**: 19 Zortrax-name materials carried from R6 and 7 Generic materials (PLA, PETG, ABS, ASA, TPU, PA and PC). Total: **104 native filament profiles**. Profiles are filtered to the selected nozzle. All Z-SUITE-derived filament temperature/retraction fields have identifiable source provenance; some high-temperature/reference records come from different Zortrax product families.

- **Z-PLA** and **Z-PLA Pro** are separate products and presets. Do not combine them by name.
- **Generic** presets are *uncalibrated starting points*; for a named third-party spool use **Save As** and tune temperature, flow ratio, volumetric flow, retraction and pressure advance.
- Pressure advance is **zero by default** until calibrated on the physical nozzle/filament.
- **Z-SUPPORT** is intentionally absent. A single-extruder Classic M300 may generate same-material supports in Orca, but cannot print model and soluble support in two simultaneous materials.
- **Z-PEEK (400°C)** and the **Z-PEI 1010 / 9085** entries exceed the current 305°C Klipper hotend *target* limit. Their presence in the menu and software slicing results **do not qualify them for printing**.
- Retraction, cooling, flow ratio and MVS are not exact inverse transformations of Z-SUITE feed fields; calibrate them separately.

### Recorded first print test and hot-bed target

During the 11 November 2026 trial, the host reported a Z-PLA **210°C nozzle / 50°C bed** print request. In the archived source profile Z-PLA was **210°C / 30°C**. The historical value must remain visible in the migration document. **The current R7.1 native Z-PLA 0.4 mm filament preset requests 50°C on all plate selectors** (first and subsequent layers), matching the user-confirmed start. The archived R6/R7 source remains 30°C. The Z-PLA presets for the three other nozzle variants remain unchanged at 30°C, as do all other materials. This override is **not an OEM Z-SUITE default**; verify surface adhesion and print completion before broad use.

If the bed is already warmer than a low requested target, the M300 host's temperature-stability gate may wait until both heater measurements fall within approximately ±2°C. Do not override heater ownership while `START_PRINT` is in progress.

## Klipper integration is deliberately separate

The machine's existing start G-code includes:

```gcode
G90
M83
SET_PRESSURE_ADVANCE ADVANCE=0
START_PRINT EXTRUDER_TEMP={first_layer_temperature[0]} BED_TEMP=[bed_temperature_initial_layer_single] MESH=AUTO
```

This invokes **host-managed heating, center contact homing, saved mesh selection and a four-line purge**. `MESH=AUTO` loads saved `m300_pads` if available, but does **not** perform an automatic mesh survey.

The 11 November test confirmed that a negative mesh correction could reject a purge motion with `Move out of range: X3 Y10 Z-0.089` when Klipper `position_min` was `0`. The host-side tested values were `position_min: -0.5`, `safe_z: 5`, `approach_distance: 6.5`. These values belong to the **Klipper config on the qualified printer**, not to the Orca preset. Mechanical clearance, probe endstops, automatic homing and the saved mesh remain host responsibilities.

Do not turn off mesh compensation, move purge lines or globally add Z offsets to disguise range errors. Do not edit or reboot the Orange Pi during an active print.

## Source compatibility and application verification

- The native Orca system vendor must be loaded from `profiles/`. An empty `inherits: ""` metadata key in a complete flat preset makes the Orca 2.5 **GUI native-loader** reject that preset even if CLI slicing appears to work. R7 correctly **omits** the empty key.
- The **R7 installer on macOS** does not edit `OrcaSlicer.conf` or remove Creality; enable M300 through Orca's own printer selector after installation.
- Baseline software evidence: 138/138 sliced test jobs, 14 macOS installer tests, and a real Orca 2.5.0 Linux/Xvfb GUI loader test confirming 30 processes and 104 filaments. It does not prove a complete print or the user's own Mac GUI was tested.
- Previous releases are retained only in Git history. This tree contains one current profile set and installer.

See [Installation](INSTALLATION.md) · [full Z-SUITE crosswalk](ZSUITE_TO_ORCA.md) · [source JSON catalog](tables/processes.csv).

## Current validation and cleanup

All 140 profile files are preserved byte-for-byte. The older test figures above describe historical R7; current checks are recorded separately in [validation evidence](VALIDATION.md). Repository cleanup does not perform a new physical test or change the operator's host.
