# Install and connect the Zortrax M300 Classic profiles in OrcaSlicer 2.5 (macOS)

## Before you begin

This installer modifies only the **Zortrax native system profile files** in the local OrcaSlicer configuration. It does not install Klipper, MCU firmware or Orange Pi software, does not change `OrcaSlicer.conf`, and does not disable Creality K2 Plus or Inventure.

Use a local Mac Terminal. Do **not** use SSH to the Orange Pi for Orca profile installation. **Save your projects and quit OrcaSlicer completely with Cmd+Q.** Keep a backup of personally tuned Orca profiles.

## 1. Get the repository

For an existing checkout at the expected path:

```bash
git -C "$HOME/Zortrax-m300-Orca-Slicer" pull --ff-only origin main
```

If the repository is not yet present, clone it once:

```bash
git clone https://github.com/MarcinKowalik-AGH/Zortrax-m300-Orca-Slicer.git "$HOME/Zortrax-m300-Orca-Slicer"
```

A failed pull because of local modifications is a conflict to review, **not** a reason to run `git reset --hard`. The host-side `Zortrax-m300-Klipper` repository is completely separate.

## 2. Install the native R7 profiles

```bash
python3 "$HOME/Zortrax-m300-Orca-Slicer/install.py" --apply
```

The installer validates the target environment and creates a reversible backup. It does **not** rewrite `OrcaSlicer.conf` or activate printer subscriptions behind the user's back. The optional `--archive-offline --apply` mode must not be used until the new profiles have been tested in Orca.

## 3. Enable and select the model

Restart OrcaSlicer 2.5 and open **Printer → Select/Remove printers (system presets)**. Find **Zortrax → Zortrax M300 Classic**, select the nozzle variant matching the physical machine (0.2, 0.3, 0.4 or 0.6 mm), and **leave other manufacturers selected**.

On the Prepare page, verify all three selectors:

| Selector | Example for a stock nozzle |
|---|---|
| Printer | `Zortrax M300 Classic` → `0.4 nozzle` |
| Filament | `Z-PLA @Zortrax M300 0.4` or another compatible 0.4 entry |
| Process | `0.20mm Standard @Zortrax M300 Classic 0.4 nozzle` |

Check your **Build plate** material and exact bed-temperature value in Filament. In the R7.1 native presets, **Z-PLA with a 0.4 mm nozzle requests a 50°C bed** on every listed plate type, based on the user's first-print start (the original R6/R7 source was 30°C). All other Z-PLA nozzle variants retain the original 30°C. This is **not** an OEM-prescribed temperature. The slicer only requests a target; it does not change host heater limits.

## 4. Add Moonraker / Fluidd as the printer host

From the printer connection icon in Orca, select **Host type: Moonraker**. For an Orange Pi configured with the project's normal ports use:

```text
Host URL: http://<Orange-Pi-LAN-IP>:7125
Device UI: http://<Orange-Pi-LAN-IP>:4480
```

Use your actual LAN address and configured Moonraker/Fluidd ports. Only leave the API key blank on a local setup that does not require one. Test the connection and save the physical printer.

Slice a small object and choose **Send/Upload to printer**, storage **`gcodes`** (never `config`). For the first test choose **Upload**, confirm the file is visible in Fluidd, and **start printing only under supervision**.

## 5. Start/mesh/PA behavior

The native profile delegates startup to the Klipper host:

```gcode
START_PRINT EXTRUDER_TEMP={first_layer_temperature[0]} BED_TEMP=[bed_temperature_initial_layer_single] MESH=AUTO
```

The host performs heating, homing, `m300_pads` mesh loading, purge, and heater ownership. `MESH=AUTO` uses a *previously saved mesh* if available; it does **not** command a new 25-point probing cycle. Relative extrusion `M83` is already enabled, and the machine profile ends with `END_PRINT`.

**Do not put these host-only values into Orca**: `position_min`, `safe_z`, `approach_distance`, `z_contact_clearance`, sensor shutdown limits, UART speed, OLED settings or heater configuration. A previous M300 print-start failure at purge Z=-0.089 was resolved in the *Klipper config of that machine*, not by moving purge or disabling mesh.

## 6. Archive old M300 offline bundles (optional, only after success)

Quit OrcaSlicer again:

```bash
python3 "$HOME/Zortrax-m300-Orca-Slicer/install.py" --archive-offline --apply
```

The installer recognizes the old `offline_M300_Classic_0.3_v1`, `0.4_v1`, `0.6_v1` and `0.8_v1` bundles and archives only those that match its safety rules. Mixed or changed bundles are left alone. It preserves other vendors and independently saved presets, and it can restore from its recorded backup.

**Never run** the historical `repair_macos_r6.py --apply` against this R7 installation: the R6 helper had a different configuration scope and could alter unrelated printer visibility.

## Validation limits

R7 was validated by 138 slicer cases, 14 installer cases and the Orca 2.5 Linux/Xvfb native GUI loader. These software checks do not guarantee physical flow, adhesion, Z clearance, or finished print results. High-temperature entries that exceed host target limits are not usable merely because the slicer can generate G-code.

Consult the [profile guide](PROFILES.md), [full migration crosswalk](ZSUITE_TO_ORCA.md), and [separate host project](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper).

## Current tree and rollback

Use the single root `install.py`; versioned installers and old ZIPs have been retired from this tree. The receipt format is preserved. With Orca closed, run `python3 install.py --restore /full/path/to/backup` to restore a recorded backup; the installer refuses to overwrite later edits. See [current validation](VALIDATION.md).
