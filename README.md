<h1 align="center"> Water Rights Nightly Updates </h1>

### Requirements: ArcGIS Pro 3.4+ | Python 3.11 | Enterprise 11.3+

## Overview
This modern implementation replaces 43 legacy ArcGIS  ModelBuilder workflows and seven python scripts with a unified, maintable solution for updating our Water Rights data. The script automates data synchronization between, Test, Prodcution, and CSA Enterprise Geodatabases while ensuring data integrity and performance.

### ✨ Key Features

### 🏗️ Architecture
```
WaterRights/
├──README.md                        # configuration guide
├──pyproject.toml                   # deps, Python version, tooling
├──pre-commit-config.yaml           # ruff/black/mypy
├──.vscode/
|   ├──settings.json
|   └──launch.json                  # debug "Run Water Rights"
├──docs/
|   ├──overview.md                  # what it does, simple diagram
|   ├──system_overview.md           # machines, schedules, owners
|   ├──runbook.md                   # smoke checks, common failures, rollback
|   ├──data_contracts.md            # field lists, domains, keys, watermarks
|   ├──WR_sum_PT_2025.dbf
|   ├──WR_NightlyScripts_FilesStructure.txt
|   ├──Permit_Summary.xlsx
|   ├──WR_sum_P_by_Purpose_GWSW.xlsx
|   ├──WR_sum_PT_Active.xlsx
|   └──sops/
|       ├──Monthly Updates for SDE Layers.docx
|       ├──Updating the Water Rights Maps.docx
|       ├──Updating the Web Summary Statistics.docx
|       └──WaterRights_MonthlyUpdatesSDELayers.docx
├──config/
|   ├──settings.example.json        # non-secret config template
|   ├──.env.example                 # env var sample (PORTAL_URL, SDE_CONN, etc.)
|   ├──settings.json
|   └──launch.json                  # debug "Run Water Rights"
├──src/
|   └──water_rights/
|       ├──__init__.py
|       ├──cli.py                   # Typer/Click entrypoint
|       ├──cfg.py                   # pydantic-settings
|       ├──watermark.py             # last-run timestamp storage
|       ├──ingest.py                # CDC pulls
|       ├──transform.py             # domain mapping, label building
|       ├──validate.py              # rules (status sets, geometry-in-OK, etc.)
|       ├──sde_apply.py             # arcpy versioned upserts + reconcile/post
|       ├──fs_apply.py              # ArcGIS API append(upsert=True)
|       └──log.py                   # structured JSON logs
├──scripts/
|   ├──WR_Updates.py                # thin wrapper calling `water_rights.cli:main`
|   └──py2.6Scripts/
|       ├──SAB_Update_106.py
|       ├──WR_Copy_Logfiles_to_SAB_folder.py
|       ├──WR_LT_Update_106_32logging.py
|       ├──WR_LT_Update_106_64logging.py
|       ├──WR_LT_Update_CSA_32logging.py
|       ├──WR_Permit_Notice_Map_Update_logging.py
|       └──WR_PT_Update_CSA_32logging.py
├──tests/
|   ├──conftest.py
|   ├──test_validate.py
|   └──data/
|       ├──sample_input.csv
|       └──expected_output.geojson  # "golden" results for quick regression checks
├──modelbuilder/
|   ├──Z_LT_Water_Rights102.tbx
|   ├──Z_SDE_Layers_Update108.tbx
|   ├──ZUpdateSettlementAreaBasins.tbx
|   ├──ZWRDailyUpdates.tbx
|   ├──ZWRPermitProprosals.tbx
|   └──diagrams/
|       └──model_overview.png
├──metadata/
|   ├──domains.json                 # code→label maps
|   └──schema/
|       └──sde_layer.yaml           # layer names, fields, types, indices
├──logs/
|   └──.gitkeep                     # keep folder; don't commit log files!
├──.github/
|   └──workflows/
|       └──ci.yml                   # lint/typecheck/tests on push/PR
```

### 🚀 Quick Start

**Prerequisites**
- ArcGIS Pro 3.4 (Enterprise 11.3+ compatibility)
- Professional/Professional Plus license (for editing operations)
- Python 3.11 (included with ArcGIS Pro)
- Required Python packages: