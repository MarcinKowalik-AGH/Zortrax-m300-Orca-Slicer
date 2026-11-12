# Documentation (English)

**Current maintained documentation:**

- [R7 profile guide](PROFILE_GUIDE_R7.md) — model/variant organization, all nozzle sizes, print quality, filament families and limitations.
- [R7 macOS installation and Moonraker connection](INSTALL_R7.md) — safe setup without modifying `OrcaSlicer.conf` or Creality/other printer selections.
- [Z-SUITE → OrcaSlicer R7 crosswalk](ZSUITE_TO_ORCA_R7.md) — complete 30-process matrix, 26-material table for 0.4 mm, exact Z-PLA Pro speed comparisons and parameter dictionary.
- [Evidence: R7 process catalog](../evidence/R7_PROCESS_CATALOG.json) and [R7 validation](../evidence/R7_VALIDATION.json).
- [Historical Z-SUITE Classic and beta-4 source files](../sources/).

The files ending in `_PL.md` and the older R3–R6 documents are **retained historical Polish notes**. They are useful for tracking earlier decisions and migration history, but the English pages above and the root [README](../README.md) are now the authoritative entry points. The installer and native presets retain the historical R7 compatibility requirements.

**Boundary:** this repository changes Orca profiles only. Klipper Z homing, PC7 contact release, mesh application, heater limits, UART, bootloader, OLED and MCU firmware belong to the separate [Zortrax-m300-Klipper](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper) repository.
