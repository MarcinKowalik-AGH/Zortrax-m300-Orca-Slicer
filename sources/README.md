# Numerical source evidence

These files are the evidence needed to audit the current profiles, not old installable releases.

| File | Contents |
|---|---|
| [zsuite_classic.json](zsuite_classic.json) | 448 recovered records, including 152 Classic M300 selections |
| [zsuite_beta4.json](zsuite_beta4.json) | 214 recovered records from named other Zortrax models |
| [filament_provenance.json](filament_provenance.json) | Exact selected source metadata/mapping for the 76 current named Zortrax filament presets |
| [MANIFEST.json](MANIFEST.json) | Original binary/installer checksums and retained numerical-file hashes |

Record source, model, material, nozzle, displayed layer, quality and infill labels are preserved. Missing fields are not silently invented. The original extraction code remains accessible through the manifest's pinned Git-history link. No vendor installer, DLL, font or image asset is distributed.

The only retained numerical-source override is explicitly marked: Z-PLA / nozzle 0.4 has current bed 50°C rather than source 30°C, based on a reported print start. No source data were edited to disguise that difference. Other-model data do not prove Classic compatibility. [Generated correspondence](../docs/ZSUITE_TO_ORCA.md).
