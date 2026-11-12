# Zortrax M300 Classic — OrcaSlicer

**Current profiles: R7.1 · Target slicer: OrcaSlicer 2.5.0 · Current release only.**

Native system profiles for the **Zortrax M300 Classic with the project's Klipper port**. This community integration uses recovered Z-SUITE data and explicit engineering adaptations; it is not an official Zortrax Orca release, or an OEM-firmware/M300 Plus/M300 Dual/Inventure preset.

**This repository installs slicer profiles on the Mac only. It never updates the Orange Pi, Klipper, MCU, bootloader, UART, OLED or Fluidd.**

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

## Update on the Mac

Save your projects and **quit OrcaSlicer using Cmd+Q**. Run in the **Mac's local Terminal**, not SSH to the Orange Pi:

```bash
git -C "$HOME/Zortrax-m300-Orca-Slicer" pull --ff-only origin main &&
python3 "$HOME/Zortrax-m300-Orca-Slicer/install.py" --apply
```

For a first checkout, use the installation guide. No sudo is needed. The installer preserves `OrcaSlicer.conf`, independent user presets and other printer brands. Enable **Zortrax → Zortrax M300 Classic** in Orca's own **Select/Remove printers** dialog and leave Creality/Inventure selected. Backups and the optional old-offline-bundle archive operation are reversible.

**Use root `install.py` only.** Old versioned installers, global-config repair tools and R3–R6 ZIPs have been removed from the current tree. Earlier files remain recoverable in [Git history](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Orca-Slicer/tree/18d68bb161631004e6909a0f7585fe552b15b302); history has not been rewritten.

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

## No print-setting changes in this cleanup

All **140 current profile JSON files are preserved byte-for-byte**, including names, IDs and numerical settings. The existing R7.1 Z-PLA **0.4 mm** preset requests **210°C nozzle / 50°C bed**, whereas the recovered source bed value is 30°C. This remains a user-reported start-test override, not a new cleanup change or OEM recommendation. Other Z-PLA nozzle variants retain 30°C.

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
