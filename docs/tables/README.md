# Current machine-readable tables

Generated directly from current `profiles/` and `sources/` by `tools/catalog.py`. These are UTF-8 comma-delimited CSV files; decimal values use a dot. GitHub displays them as tables and Excel can import them. They are not extra installable profile versions.

| File | Rows | Purpose |
|---|---:|---|
| [processes.csv](processes.csv) | 30 | All processes: geometry, speeds, accelerations, shell/support/raft values |
| [filaments.csv](filaments.csv) | 104 | All filament/nozzle combinations: source/current temperatures and effective tuning values |
| [zsuite_m300_correspondence.csv](zsuite_m300_correspondence.csv) | 152 | Every recovered M300 selection with an explicitly approximate counterpart |
| [pla_pro_speed_comparison.csv](pla_pro_speed_comparison.csv) | 18 | Six feature speeds for Normal, High and Draft |

[Human-readable comparison](../ZSUITE_TO_ORCA.md). No table asserts identical OEM toolpaths or physical material qualification.
