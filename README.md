# Zortrax M300 Classic — OrcaSlicer

**Current profiles: R7.9 · Target slicer: OrcaSlicer 2.5.0 · Current release only.**

Native system profiles for the **Zortrax M300 Classic with the project's Klipper port**. This community integration uses recovered Z-SUITE data and explicit engineering adaptations; it is not an official Zortrax Orca release, or an OEM-firmware/M300 Plus/M300 Dual/Inventure preset.

**This repository installs slicer profiles on the Mac only. It never updates the Orange Pi, Klipper, MCU, bootloader, UART, OLED or Fluidd.**

**R7.9: corrected perimeter screw geometry and honest cache reporting.** The measured 360 mm plate model now places **16 hex-socket screws** on the outer flange, ~6 mm from the edges, on five approximately evenly spaced positions along each side (four corner screws counted only once). This replaces the R7.8 screws incorrectly positioned ~17 mm in from the actual edges. Heads now contain visibly recessed **hexagonal** sockets. The installer **does not delete Orca's compiled `system/Zortrax.opc` cache on an unchanged reinstall**, and logs the actual profile revision.

**Requested 15% darker excluded border — stock OrcaSlicer limitation:** Orca 2.5 hardcodes the color of custom bed STL models (`Bed3D::DEFAULT_MODEL_COLOR`) and clips `bed_custom_texture` SVG to the 300 × 305 mm printable polygon. Therefore **the installer cannot make the outer 360 mm metal margin precisely 15% darker in the stock Orca app** without changing Orca's C++ renderer. The [full-plate layout](docs/Zortrax_M300_360mm_plate_layout.svg) now demonstrates the target 15% shading as a **design reference only**; it is not claimed as a change to Orca's rendered STL. Never increase the printable area for cosmetic reasons.

**R7.8: 3 mm physical plate and photo-scaled rear electrical connector.** The STL model now has a 3.0 mm-thick metal sheet across the entire 360 × 360 mm footprint. The rear electrical socket sits approximately 148 mm from the left edge and extends about 1.6 mm beyond the back edge, with two mounting tabs, five small ribs and a visible latch. Width and position are estimated from ruler photographs; socket height is provisional. This affects *only the local visual bed model*; no profile motion, printable area, Klipper, process, filament, or G-code changes from R7.7.

**R7.7 — measured Zortrax M300 physical bed, safe print area unchanged in Klipper.** The actual build plate is **360 × 360 mm**, with a **332 × 329 mm** perforated region (14 mm margins left/right; 15 mm front and 16 mm rear). The gold contact pads measure **60 × 60 mm** in the corners and **50 × 50 mm** in the centre. Their *positions* are estimated from the provided photograph, while their sizes and the bed margins are measured.

**Orca print placement is precisely X=0…300 mm and Y=0…305 mm.** Relative to the centre of the real plate, X spans −150…+150 mm and Y spans **−150…+155 mm**. The 360 mm plate therefore extends 30 mm past the print area on each X side, 30 mm in front and 25 mm behind. The separate STL makes the physical surround visible outside the print polygon, including regular perforations in the surround and hex-socket frame screws. A cropped, precisely regular SVG supplies gold pads, perforations and two central screw collars *inside* the printable region. Orca's *Model* and *Texture* settings are separate; the Mac installer creates both assets and assigns their absolute paths for each nozzle variant.

[**View the measured 360 mm plate with the true 300 × 305 mm limit**](docs/Zortrax_M300_360mm_plate_layout.svg) · [Dimensions and coordinate transform](docs/M300_BED_GEOMETRY.md)

**No Klipper/Orange Pi/MCU or firmware changes.** The printer's service travel towards Y=315 is deliberately outside Orca's 305 mm printable limit. All printing, temperature, start/end G-code, mesh and process settings are preserved. The one slicer-geometry correction is the Y printable bound, previously entered as 300 mm in the four Orca nozzle JSON files, now 305 mm.

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
