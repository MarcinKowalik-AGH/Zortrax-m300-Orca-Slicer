# Zortrax M300 Classic — OrcaSlicer

**Current profiles: R7.4.1 · Target slicer: OrcaSlicer 2.5.0 · Current release only.**

Native system profiles for the **Zortrax M300 Classic with the project's Klipper port**. This community integration uses recovered Z-SUITE data and explicit engineering adaptations; it is not an official Zortrax Orca release, or an OEM-firmware/M300 Plus/M300 Dual/Inventure preset.

**This repository installs slicer profiles on the Mac only. It never updates the Orange Pi, Klipper, MCU, bootloader, UART, OLED or Fluidd.**

**R7.4.1 fixes the perforated-bed PNG display in OrcaSlicer 2.5.** The installer copies the image into Orca's vendor resources **and now sets the actual `bed_custom_texture` in each installed 0.2/0.3/0.4/0.6 mm printer preset** to the absolute image path on that Mac. Earlier R7.4 copied the image but did not populate the `Texture` field in **Printer settings → Printable area → Set… → Bed Shape**. No manual image selection or hard-coded Mac username is needed. This is visual only; no G-code, mesh, temperature, or Klipper changes.

## Install on macOS — first-time installation or update

These commands work on **any Mac with OrcaSlicer 2.5 installed**. The `$HOME` variable automatically points to the current user's home folder, so **no personal username or fixed `/Users/...` path is needed**.

**Before either procedure:** save your projects and fully quit OrcaSlicer with **Cmd+Q**. Use the **local Mac Terminal**, not an SSH session on the printer's Orange Pi. Do **not** use `sudo`.

### A. First installation on a new Mac

If OrcaSlicer is installed but **this repository has not been downloaded on this Mac**, run:

```bash
git clone https://github.com/MarcinKowalik-AGH/Zortrax-m300-Orca-Slicer.git "$HOME/Zortrax-m300-Orca-Slicer" &&
python3 "$HOME/Zortrax-m300-Orca-Slicer/install.py" --apply
```

The first command downloads the current profiles; the second installs them. You only need to clone once on each computer.

### B. Update on a Mac with an existing checkout

If the repository folder **already exists** on this Mac, run:

```bash
git -C "$HOME/Zortrax-m300-Orca-Slicer" pull --ff-only origin main &&
python3 "$HOME/Zortrax-m300-Orca-Slicer/install.py" --apply
```

### C. Enable the printer in OrcaSlicer

Launch OrcaSlicer 2.5, open **Printer → Select/Remove printers (system presets)**, and enable **Zortrax → Zortrax M300 Classic**. Select your **physically installed 0.2, 0.3, 0.4 or 0.6 mm nozzle**. Keep any other printer brands enabled.

### Troubleshooting

- **`fatal: cannot change to ... No such file or directory`**: the repository is missing from that location. Use **A. First installation**, not the `git pull` command.
- **`git clone` says the destination already exists**: do not delete the folder. Check whether it contains the correct repository and use **B. Update** if so.
- **`git pull --ff-only` reports local modifications**: inspect those changes; do not use `git reset --hard`.
- **`git` or `python3` is missing**: install or enable the required command-line tools first.
- Installing new profiles does **not** modify previously generated G-code. Select the filament and **slice again** for subsequent prints.

Only native OrcaSlicer presets are installed. The installer preserves other printers and global Orca settings, creates a backup, and **does not change Klipper, Orange Pi, MCU firmware or printer motion limits**. See the [full installation, connection and rollback guide](docs/INSTALLATION.md).

## One current profile set

| Component | Contents |
|---|---|
| Printer | One Zortrax M300 Classic model |
| Nozzle variants | 0.2 / 0.3 / 0.4 / 0.6 mm |
| Processes | 30 quality presets, matched to nozzle geometry |
| Filaments | 104: 19 Zortrax + 7 Generic names for each nozzle |
| Active files | [profiles/](profiles/) — the only installable preset set |
| Installer | [install.py](install.py) — the only supported installer |
| Correspondence | [Detailed Z-SUITE → Orca mapping](docs/ZSUITE_TO_ORCA.md) and [CSV tables](docs/tables/README.md) |

Classic M300 source records contain **only the 0.4 mm nozzle**. Other variants are project adaptations for mechanically fitted nozzles; M300 Plus/Dual support does not establish Classic support. No Creality motion settings were copied.

## Documentation

| Guide | Purpose |
|---|---|
| [Installation and connection](docs/INSTALLATION.md) | Local Mac setup, other-printer preservation, selection, Moonraker, backups and rollback |
| [Printer/process/filament guide](docs/PROFILES.md) | Nozzle geometry, quality families, material provenance, start/end and PA |
| [Z-SUITE profile tables](docs/ZSUITE_TO_ORCA.md) | Source labels, all 152 M300 combinations, closest processes, temperatures and speed differences |
| [Settings dictionary](docs/SETTINGS_REFERENCE.md) | What transfers, what needs manual review, and unresolved mappings |
| [Validation](docs/VALIDATION.md) | Current software evidence versus limited operator-reported hardware results |

## Additional installation notes

Use **only the root `install.py`**. Old versioned installers, global-config repair tools and R3–R6 ZIPs have been removed from the current tree. Earlier files remain available in [Git history](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Orca-Slicer/tree/18d68bb161631004e6909a0f7585fe552b15b302); history has not been rewritten.

## Quick process correspondence — nozzle 0.4 mm

| Z-SUITE selection | Current Orca starting point | Important distinction |
|---|---|---|
| 0.09 fine detail | 0.08mm SuperDetail | Different height, not an exact replacement |
| 0.14 High | 0.12mm Detail | Thinner approximation |
| 0.14 Normal | 0.16mm Optimal | Slightly thicker approximation |
| 0.19 Normal | 0.20mm Standard | Six speeds match the cited Z-PLA Pro Normal example, not the whole profile |
| 0.19 High | 0.20mm High Quality | Three walls and different speeds, not the OEM High table |
| 0.19 Draft | A user copy of 0.20mm Standard | No supplied 0.20 Draft; compare speeds explicitly |
| 0.29 | 0.28mm SuperDraft | Different height and default 10% infill |

Choose the same material, then copy the old project's actual infill density/pattern, shells, supports and raft choices. **Source displayed layer labels and recovered SliceThickness are shown separately.** The [complete generated table](docs/ZSUITE_TO_ORCA.md) includes every recovered Classic M300 row without inventing missing equivalents.

## R7.3: only raise bed temperatures below their minima

**40°C on the first layer / 35°C on later layers are floors, never caps.** Of the eight materials reviewed, three required an increase (each has four nozzle-specific variants):

| Material | Original first/later bed | R7.3 first/later bed |
|---|---|---|
| Z-SEMIFLEX | 10/10°C | **40/35°C** |
| Z-GLASS | 30/30°C | **40/35°C** |
| Z-PETG | 30/30°C | **40/35°C** |

**Preserved:** Z-PHA 55/55°C; Generic TPU 50/50°C; Z-FLEX 50/50°C; Z-ASA Pro 65/65°C; Z-ULTRAT Plus 100/100°C. All hotend temperatures, other filaments, all process parameters and the R7.2 PLA experiment remain unchanged. The 40/35°C minimum is an unvalidated operator-requested trial, not a manufacturer-certified setting.

## R7.2: increased PLA first-layer temperatures

To test first-layer adhesion, **all 12 Z-PLA, Z-PLA Pro and Generic PLA profiles** (nozzles 0.2 / 0.3 / 0.4 / 0.6 mm) now request **230°C nozzle and 70°C bed on the first layer only**. Every other printing setting, including later-layer temperatures, extrusion, retraction, fan behavior, raft and process speeds, is unchanged.

| Filament | First layer (nozzle / bed) | Later layers (nozzle / bed) |
|---|---|---|
| Z-PLA, 0.4 mm nozzle | **230 / 70°C** | **210 / 50°C** |
| Z-PLA, 0.2/0.3/0.6 mm | **230 / 70°C** | **210 / 30°C** |
| Z-PLA Pro, all four nozzle variants | **230 / 70°C** | **207 / 30°C** |
| Generic PLA, all four nozzle variants | **230 / 70°C** | **210 / 60°C** |

The archived Z-SUITE record for Z-PLA remains 210/30°C; the prior 0.4 mm bed override of 50°C also remains for subsequent layers. **230/70°C is a requested, unvalidated trial**, not a Zortrax or generic PLA manufacturer's recommendation. Verify the spool's maximum nozzle temperature and watch adhesion, extrusion and warping. Save and re-slice existing projects; an already-generated G-code file will not change.

`M83`, `START_PRINT`/`END_PRINT`/`PAUSE`, `MESH=AUTO` and **PA=0 pending calibration** remain unchanged. The separate [Klipper project](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper) owns homing, PC7 contact release, Z range and mesh compensation. No purge lines are relocated.

**PEEK/PEI are visible reference entries, not printable materials on a 305°C target-limit setup.** Their 400/370/360°C requests exceed it. Slicing success is not hardware qualification; Generic and other materials still need physical calibration.

## Current layout

```text
profiles/                 one current native vendor and preset set
install.py                guarded, reversible macOS installer
docs/                     English guides and generated CSV tables
sources/                  extracted numerical evidence and provenance
tests/                    installer, profile, slicing and loader checks
tools/                    catalog, checksums, packaging and validation
evidence/                 current baseline hashes and test results
.github/workflows/        one current validation workflow
```

Source databases are evidence, not old installable versions. No OEM installers, DLLs, fonts or old profile ZIPs are distributed. [Current change notes](CHANGELOG.md) · [validation scope](docs/VALIDATION.md).
