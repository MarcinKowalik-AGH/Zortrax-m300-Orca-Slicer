# Zortrax M300 Classic — OrcaSlicer profiles (R7.1)

Community-maintained **native OrcaSlicer 2.5** system profiles for the **Zortrax M300 Classic running the separate Klipper port**. This repository contains **slicer presets and their audit evidence only**. It does **not** install or update Klipper, the Orange Pi, the printer MCU, its bootloader, or Fluidd.

## Current profile set

| Component | R7 contents |
|---|---|
| Printer family | **One** `Zortrax M300 Classic` model in Orca |
| Printer variants | **Four** selectable nozzle diameters: 0.2 / 0.3 / 0.4 / 0.6 mm |
| Quality/process profiles | **30** presets (5 / 7 / 8 / 10 for those respective nozzle sizes) |
| Filament profiles | **104** presets: 19 Zortrax names + 7 Generic polymer families, each for four nozzle sizes |
| Supports | Regular same-filament support and a 2-layer raft where enabled; no separate Z-SUPPORT soluble material |
| G-code | Klipper flavor, 1.75 mm filament, relative extrusion (`M83`), existing `START_PRINT` / `END_PRINT` host macros |
| Primary profile directory | [`native_r7/`](native_r7/) |

The original **M300 Classic Z-SUITE 0.4 mm nozzle** is the only manufacturer-documented Classic configuration. The 0.2, 0.3 and 0.6 mm nozzle variants and their quality presets are **engineering adaptations for the installed hardware and Klipper**. They are **not** official Z-SUITE Classic nozzle presets or adaptations copied from Creality K2 motion settings.

For a complete explanation of all available settings, start with the [R7 English profile guide](docs/PROFILE_GUIDE_R7.md) and the [Z-SUITE → OrcaSlicer crosswalk](docs/ZSUITE_TO_ORCA_R7.md). In particular, an approximate quality label does **not** mean identical layer height, fill, motion, raft or resulting toolpaths.

## Install on macOS (existing OrcaSlicer)

**Before installing:** save your projects and completely quit OrcaSlicer using **Cmd+Q**. Run the following in the **Mac's local Terminal**, not in SSH to Orange Pi:

```bash
git -C "$HOME/Zortrax-m300-Orca-Slicer" pull --ff-only origin main &&
python3 "$HOME/Zortrax-m300-Orca-Slicer/tools/install_classic_r7.py" --apply
```

This **R7 installer only** copies/updates the Zortrax M300 native system-vendor presets, checks its inputs and creates a rollback backup. **It does not write `OrcaSlicer.conf`**, activate printer subscriptions for you, or modify Creality, Inventure or other printer settings. It refuses to run on Orange Pi/Linux, over SSH, as root, or while OrcaSlicer is running.

Then launch Orca and choose:

1. **Printer → Select/Remove printers (system presets)**.
2. **Zortrax → Zortrax M300 Classic**. Select the physically fitted nozzle variant(s).
3. Keep Creality and other printers selected; do not remove existing ones.
4. Pick the matching printer, **Process**, and **Filament**. The process and filament must match the nozzle variant.

Only **after verifying** the new M300 profiles in Orca, close Orca again to archive the four recognized old offline M300-only bundles:

```bash
python3 "$HOME/Zortrax-m300-Orca-Slicer/tools/install_classic_r7.py" --archive-offline --apply
```

The archive operation is optional and reversible. It checks each old bundle, leaves mixed/unknown bundles untouched, and does not delete personal or other-printer profiles. Do **not** run the legacy `repair_macos_r6.py --apply` installer: it had a different global-config scope.

See [step-by-step installation, verification and rollback](docs/INSTALL_R7.md).

## Use with the M300 Klipper port

The printer preset already supplies start/end G-code:

```gcode
G90
M83
SET_PRESSURE_ADVANCE ADVANCE=0
START_PRINT EXTRUDER_TEMP={first_layer_temperature[0]} BED_TEMP=[bed_temperature_initial_layer_single] MESH=AUTO
```

```gcode
END_PRINT
```

- `START_PRINT` handles heating, homing, loading an existing saved `m300_pads` profile with `MESH=AUTO`, and the host-side purge procedure. **`MESH=AUTO` does not re-probe the bed.**
- `position_min`, `safe_z`, `approach_distance`, the contact probe, PC7 release checks, thermal shutdown limits, UART and OLED belong **only** to the [separate Klipper repository](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper). They must not be rewritten as slicer settings.
- Configure a physical printer in Orca using **Moonraker** on `http://<Orange-Pi-IP>:7125`, and optionally Fluidd at `http://<Orange-Pi-IP>:4480`, for a host with those ports. Upload prints to **`gcodes`**, not `config`. For initial checks choose **Upload**, not **Upload and Print**.
- Filament `pressure_advance = 0` is intentional until measured. Generic polymer settings are uncalibrated starter values. Confirm the installed nozzle in Klipper separately.

### First print-test finding (11 November 2026)

A Classic M300 running the project's Klipper host successfully heated, homed and **started printing** a Benchy sliced with the **0.4 mm** profile. The first host-side attempt failed before purge with `Move out of range: 3.000 10.000 -0.089 [0.000]`, because an active pad mesh compensated a nominal `Z=0.28` purge move to `Z=-0.089`. The M300 operator subsequently configured **`position_min: -0.5`, `safe_z: 5`, `approach_distance: 6.5`** on that *hardware-qualified host*, and reported that printing began. These are **not OrcaSlicer changes**, and physical safety/clearance must be checked for any other machine. Do not move purge lines or disable pad compensation to work around this error.

**R7.1 changes only the native Z-PLA 0.4 mm filament preset**: it now requests **210°C hotend / 50°C bed**, matching the successful-start log. The archived Z-SUITE/R6/R7 source still records **30°C**; the 0.2/0.3/0.6 mm Z-PLA variants and all other material temperatures are unchanged. This is a user-observed field-test adjustment, **not** a universal or manufacturer-certified temperature. Print completion and first-layer quality have **not** been documented as passing.

## Source data, limits and validation

- [Detailed Z-SUITE → Orca profile mapping](docs/ZSUITE_TO_ORCA_R7.md): displayed-vs-source layer heights, Normal/High/Draft speeds, 30 processes, 26 material rows, limitations and terminology.
- [Current R7 preset guide](docs/PROFILE_GUIDE_R7.md) · [installation guide](docs/INSTALL_R7.md).
- [R7 process catalog](evidence/R7_PROCESS_CATALOG.json) · [R7 validation evidence](evidence/R7_VALIDATION.json) · [source database](sources/).
- Baseline R7: **138/138 slicer checks** and **14 installer checks** passed. R7.1 adds a **single 0.4 mm Z-PLA bed-temperature override** and English descriptive metadata; those historical runtime numbers must not be mistaken for a new complete R7.1 test run. A real OrcaSlicer 2.5.0 application in Linux/Xvfb loaded four printer variants, 30 processes, and 104 filaments. These checks **did not** validate the original user's macOS GUI or physical completion of every print.
- The source bundle from R6 and historical R3–R6 files are retained for provenance, **not as the current installation method**.
- Z-PEEK / Z-PEI 1010 / Z-PEI 9085 remain visible reference entries but **cannot be printed** on the present **305°C target-limit** host setup. Selection or successful slicing does not override that constraint.

**Never run an Orca/host update or restart Klipper during an active print.** The historical Polish R3–R6/R7 notes remain as provenance in [`docs/`](docs/); the maintained entry points above are in **English**.
