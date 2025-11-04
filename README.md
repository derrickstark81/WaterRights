<h1 align="center"> Water Rights Nightly Update System (WR_Updates)</h1>

# Viewing this Document
This file is written in **Markdown (.md)** format. Markdown is a lightweight markup language used for documentation. If you see raw symbols like `**bold**`, `| tables | like this |`, or code blocks starting with ```bash, you're viewing the *raw source*.

### How to View Properly
- In **Visual Studio Code**, click the **Preview** button (the small icon that looks like a split window in the upper-right corner, or press `Ctrl + Shift + V).
- In **GitHub**, Markdown renders automatically.
- In **Microsoft Word**, Markdown isn't natively supported, but you can:
  - Use the **Markdown Editor Add-in for Word** (available in Microsoft AppSource) to open and render `.md` files with formatting.
  - Or, open the file in Word as plain text and convert via **File -> Open -> Browse -> All Files -> Select file**, then **File -> Save As -> Word Document (.docx)**.
  - Alternatively, you can use a converter like **Pandoc** to convert Markdown to Wor ( `pandoc README_WR_Nightly.md -o README_WR_Nightly.docx`).
- In **Notepad++** or a plain text editor, you'll only see the raw markdown syntax.

If you must view it as plain text, bold text is show as `**text**`, headers start with `#`, and tables are represented using vertical bars ( | ).

# Purpose

The Water Rights Nightly Update system automates the complete refresh of Water Rights data each night, replacing legacy ArcGIS ModelBuilder workflows and batch file chains with a unified Python framework.

It synchronizes datasets between **Arapaho**, **OWRP**, **OWRT**, and **CSA**, then exports maps, metadata, and summary deliverables for publication on the legacy **WebFinal** share(until fully transitioned to Open Data).

This process ensures that all public-facing layers, dashboards, and analytical tables are current and consistent across the agency.

---

# 1. Overview
### Key Benefits
- Single Python-based process (repalcing multiple scheduled scripts).
- Consistent synchronization of Water Rights data across internal and external systems.
- Automated metadata imports, Excel table generation, and static map exports.
- Clear logging, configuration, and error handling for transparency and recovery.
- Fully modular structure for maintainability.

### Main Components

| **Script**        | **Descsription**                                                                      |
| :---------------  | :-----------------------------------------------------------------------------------  |
| `wr_updates.py`   | The entrypoint. Orchestrates all submodules in sequence (runs nightly).               |
| `wr_config.py`    | Loads and validates configuration from `settings.json`.                               |
| `wr_logging.py`   | Handles logging (text + JSON) for all modules.                                        |
| `wr_sde.py`       | Performs truncate-append data refreshes between geodatabases.                         |
| `wr_metadata.py`  | Updates metadata XML for datasets.                                                    |
| `wr_proposals.py` | Processes new proposal CSVs into geodatabase tables and publishes to CSA.             |
| `wr_excel.py`     | Generates Excel summaries and embeds data overlays into maps.                         |
| `wr_maps.py`      | Exports ArcGIS Pro layouts (PDF/PNG) using `arcpy.mp`.                                |
| `wr_packaging.py` | Packages output and copies to `\\172.30.73.39\WebFinal`.                              |
| `wr_watermark.py` | Writes the `watermark.json` file with the UTC timestamp of the last successful run.   |
| `settings.json`   | Configuration file defining all paths, connections, and datasets.                     |
| `__init__.py`     | Initializes the WR module structure (used for imports).                               |

---

# 2. System Architecture
The Water Rights Nightly Update System is an automated pipeline that synchronizes authoritative **Water Rights (WR)** data from the State of Oklahoma's Oracle-based transactional system into the GIS environments managed by **OMES** and **OU/CSA**, producing map-ready data, summary tables, and packaged public deliverables.

The system architecture consists of three connected environments:

## OMES Environment (State Network Zone)

**Primary Role**: Authoritative data storage, nightly automation, and internal GIS processing.
| **Component**     | **Hostname/Path**       | **Role**                       |
| :---------------- | :---------------------- | :----------------------------  |
| **Batch Server**  | `app-bat01-835.agency.ok.local` <br />(E: drive)  | Runs Task Scheduler jobs that execute `wr_updates.py` <br />nightly from `E:\Updates\ArcUpdateScripts\`. Host all <br />update scripts, logs, and temporary exports.  |
| **Authoritative Oracle Database** <br />(Water Rights Source) | `dat-orc01-835/owrp.owrb.thinkbig` <br />(Cheyenne) | Live transactional Oracle 11gR2 database where Water <br />Rights staff edit permit data (`OWRP` schema). The source for <br />GIS synchronization. |
| **Production Oracle SDE** | `OWRPGIS` | Spatial Database Engine on OMES's Oracle 11gR2 server. <br />Holds production WR feature classes and tables <br />for enterprise use and dashboard connections.   |
| **Test Oracle SDE**       | `OWRTGIS` | Parallel SDE environment used for testing and validation <br />prior to production promotion. |
| **Arapaho Server**    | `\\Arapaho\MasterCovs\z_GDBs\Water_Rights.gdb`    | File GDB staging environment used for intermediate <br />groprocessing and summary layers.  |
| **Scissortail Server**    | `\\Scissortail\MasterCovs\`   | Historical or reference GDB storage for QA/QC or transition from legacy ModelBuilder tools.   |
| **OWRBGIS Server**    | `\\OWRBGIS\GeoDat\`   | Hosts ArcGIS project files and FGDBs supporting <br />visualization, map packages, and historical data archiving. |
| **WebFinal Share**    | `\\172.30.73.39\WebFinal` | Temporary publish destination for packages datasets before <br />migration to Open Data portal. Output includes shapefiles, <br />map packages, and Excel summaries.  |

## CSA Environment (University of Oklahoma Zone)

**Primary Role**: External data serving and public distribution.
| **Component** | **Hostname/Path** | **Role**  |
| :------------ | :---------------- | :-------- |
| **PostgreSQL Database**   | `owrp_csa.sde`    | Nightly copy of WR GIS layers hosted on CSA's PostgreSQL <br /> server, synchronized from OMES production SDE.
| **ArcGIS Enterprise Portal** <br />(CSA)  | `https://owrb-csa.ou.edu/portal`  | Hosts published WR feature layers and dashboards. Feeds <br />the public-facing Open Data site and internal web maps.   |
| **Firewall/Connectivity** | Secured by OU-OMES <br /> interagency VPN | Allows scheduled data syncs and API-based publishing from <br />OMES's batch processess to CSA's Enterprise infrastructure.   |

## Public Access Layer (External Zone)

**Primary Role**: Distribution to the public and external partners.
| **Component** | **Example**   | **Role**  |
| :------------ | :------------ | :-------- |
| **OWRB Open Data Portal** | `https://home-owrb.opendata.arcgis.com/`  | Future home for public Water Rights datasets, replacing <br />WebFinal packaging. |
| **Downloadable Packages** | `WebFinal` (legacy)   | Users can still access WR shapefiles and summary statistics <br />while the Open Data migration is finalized.   |

## Data Flow Summary
The nightly data refresh follows this end-to-end path:
1. **Trigger**:
   - Windows Task Scheduler on `app-bat01-835` starts `wr_updates.py`
   - Script references configuration from `settings.json` located in `E:\Updates\ArcUpdateScripts\WR_Updates\`.
2. **Source Extraction**:
   - Connects to the **OWRP (Cheyenne)** Oracle DB to read the latest transactional permit data.
   - Syncs relevant records to the **OWRPGIS** SDE (production) and optionally **OWRTGIS** (test).
3. **Tranformation & Export**:
   - Derived summary layers and Excel statistics are generated.
   - Intermediate processing occurs in File GDBs on **Arapaho**, **Sissortail**, or **OWRBGIS**.
4. **Publishing**:
   - Packaged datasets are copied to `\\172.30.73.39\WebFinal`.
   - Synced WR layers are published to CSA's PostgreSQL and ArcGIS Enterprise.
5. **Validation**:
   - Logs and metadata are updated.
   - The process watermark file (`wr_watermark.json`) is refreshed with UTC timestamps.

## Visual Overview

The following diagram represents the complete system topology and nightly data movement across OMES, CSA, and public layers:

Diagram: Environments and nightly data movement across OMES (authoritative Oracle + SDE + batch), CSA (PostgreSQL + ArcGIS Enterprise), and Public distribution (WebFinal now, Open Data future).
```mermaid
flowchart LR
  %% ========= LAYOUT & STYLES =========
  classDef omes fill:#e6f0ff,stroke:#3563d9,stroke-width:1px;
  classDef csa  fill:#e7f7ed,stroke:#1f8a4c,stroke-width:1px;
  classDef pub  fill:#fff7da,stroke:#c6a420,stroke-width:1px;
  classDef db   fill:#fff,stroke:#666,stroke-width:1px,stroke-dasharray: 3 2;
  classDef host fill:#fff,stroke:#666,stroke-width:1px;

  %% ========= OMES ZONE =========
  subgraph OMES_Internal_Network
  direction TB

    BATCH[\"**Batch Server**<br/>app-bat01-835.agency.ok.local<br/><code>E:\\Updates\\ArcUpdateScripts</code>\"/]:::host
    NOTE((Task Scheduler<br/>runs <code>wr_updates.py</code>)):::host

    OWRP[(**OWRP Oracle (Cheyenne)**<br/>dat-orc01-835 / owrp.owrb.thinkbig)]:::db
    OWRPGIS[(**OWRPGIS**<br/>Oracle SDE 11gR2 — PROD)]:::db
    OWRTGIS[(**OWRTGIS**<br/>Oracle SDE 11gR2 — TEST)]:::db

    ARAPAHO[\"Arapaho server<br/><code>\\\\Arapaho\\MasterCovs\\z_GDBs\\Water_Rights.gdb</code>\" ]:::host
    SCISSOR[\"Scissortail server<br/><code>\\\\Scissortail\\MasterCovs\\</code>\"]:::host
    OWRBGIS[\"OWRBGIS server<br/><code>\\\\OWRBGIS\\GeoDat\\</code>\"]:::host

    WEBFINAL[\"**WebFinal share**<br/><code>\\\\172.30.73.39\\WebFinal</code>\" ]:::pub

  end
  class OMES_Internal_Network omes

  %% ========= CSA ZONE =========
  subgraph CSA_OU_Network
  direction TB
    CSA_PG[(**CSA PostgreSQL**<br/><code>owrp_csa.sde</code>)]:::db
    CSA_PORTAL[\"**CSA ArcGIS Enterprise**<br/>Portal/Server/Data Store\"]:::host
  end
  class CSA_OU_Network csa

  %% ========= PUBLIC ZONE =========
  subgraph Public_Access
  direction TB
    ODP[\"**OWRB Open Data (future)**<br/>home-owrb.opendata.arcgis.com\"]:::host
    PUB_USERS[[Public & Partners]]:::host
  end
  class Public_Access pub

  %% ========= FLOWS =========
  BATCH -->|Launch nightly| NOTE
  NOTE -->|reads config<br/><code>settings.json</code>| BATCH

  %% Source → SDE mirrors
  OWRP -->|ETL / mirror| OWRPGIS
  OWRP -. optional QA .-> OWRTGIS

  %% SDE → CSA (public services)
  OWRPGIS -->|Nightly sync| CSA_PG
  OWRTGIS -. optional staging .-> CSA_PG

  CSA_PG -->|Publish services| CSA_PORTAL
  CSA_PORTAL -->|Dashboards & APIs| PUB_USERS
  CSA_PORTAL --> ODP

  %% Maps/Excel & packaging on batch server using FGDBs
  BATCH -. reads/writes .-> ARAPAHO
  BATCH -. reads/writes .-> SCISSOR
  BATCH -. reads/writes .-> OWRBGIS
  BATCH -->|Export maps + Excel| WEBFINAL

```

# 3. How the System Works
### Nightly Flow Summary
1. **Load configuration** from `settings.json`.
2. **Mirror data** from Arapaho -> OWRPGIS -> OWRTGIS -> CSA.
3. **Import metadata** for mirrored layers.
4. **Process proposals** (CSV -> geodatabase tables -> publish).
5. **Generate maps and Excel overlays** for QA and publication.
6. **Package deliverables** and copy to `WebFinal` share.
7. **Write watermark** timestamp on successful completion.
8. **Rotate logs** and maintain a rolling 14-day archive.

---

# 4. Configuration Guide
All environment paths and connections are defined `settings.json`.
This is the only file you ever need to edit when system paths or database connections change.

### Example Structure
```json
{
  "paths": {
    "arapaho_wr_gdb": "E:\\GIS\\Arapaho\\WaterRights.gdb",
    "owrpgis": "C:\\Connections\\owrpgis.sde",
    "owrtgis": "C:\\Connections\\owrtgis.sde",
    "csa": "C:\\Connections\\csa.sde",
    "metadata_dir": "E:\\GIS\\Metadata\\WaterRights",
    "applications_csv": "E:\\GIS\\Applications\\proposals.csv",
    "web_datastore_gdb": "E:\\GIS\\WebDatastore\\WebDatastore.gdb",
    "map_export_dir_staging": "E:\\GIS\\Exports\\Maps",
    "logs_dir": "E:\\GIS\\Logs\\WR_Nightly",
    "watermark": "E:\\GIS\\Logs\\WR_Nightly\\watermark.json"
  }
}
```
### Making Changes
- **If a database connection changes:** update the `.sde` path in `settings.json`.
- **If file locations change:** update only the corresponding `"path"` entries.
- **No Python edits required.** The system reads all paths dynamically at runtime.
- **Always maintain double backslashes** (`\\`) in file paths to escape correctly.

---

# 5. Running the Process Manually
You can run the process manually from the ArcGIS Pro Python Command Prompt. Located by click the Windows Icon on the task bar and typing 'Python Command Prompt'.

### Dry Run (no writes):
```bash
python wr_updates.py --config settings.json --dry-run
```

### Full Run:
```bash
python wr_updates.py --config settings.json
```

### Skip Packaging:
```bash
python wr_updates.py --config settings.json --no-packaging
```

---

# 6. Scheduling the Nightly Job
### Windows Task Scheduler Configuration

| Setting           | Value                                                                 |
| :---------------- | :------------------------------------------------------------------   |
| Program/script    | `C:\Program Files\ArcGIS\Pro\bin\Python\envs\wr-nightly\python.exe`   |
| Arguments         | `"E:\Updates\ArcUpdateScripts\WR_Updates\wr_updates.py" --config`     |
|                   | `"E:\Updates\ArcUpdateScripts\WR_Updates\settings.json"`              |
| Start in          | `E:\Updates\ArcUpdateScripts\WR_Updates`                              |
| Trigger           | Daily @ 3:00 AM                                                       |
| Run As            | `domain\service.account` (must have R/W access to all UNC paths)      |

---

# 7. Logging and Monitoring
Logs are created automatically in the directory defined under `"logs_dir"` in `settings.json`.
Example structure:
```pgsql
E:\GIS\Logs\WR_Nightly\
    WR_Nightly_2025-11-04.log
    WR_Nightly_2025-11-04.jsonl
    watermark.json
```
### How to Read the Logs
- `.log` -> human-readable text summary
- `.jsonl` -> machine-readable event stream
- `watermark.json` -> timestamp of last successful run
### Example watermark:
```json
{"last_run_utc": "2025-11-04T09:00:12+00:00"}
```

---

# 8. Troubleshooting

| Symptom                                                               | Likely Cause                                                      | Fix                                                           |
| :-------------------------------------------------------------------- | :-------------------------------------------------------------    | :------------------------------------------------------------ |
| **"0xC0000022 - Application was <br />unable to start correctly"**    | Python environment permission or <br />VC runtime issue           | Run as admin or recreate the <br />`wr-nightly` environment   |
| **"pywin32 not found"**                                               | Missing COM library                                               | Run `conda install -c esri pywin32`                           |
| **Script completes but data doesn't <br />update**                    | Check SDE connection credentials                                  | Reconnect `.sde` files using ArcGIS Pro                       |
| **No new logs appear**                                                | Task Scheduler user lack write <br />access                       | Grant Modify permission to logs <br />directory               |
| **Metadata not updating**                                             | XML path in `settings.json` <br />incorrect                       | Verify `"metadata_dir"` and file names                        |

---

# 9. Extending the Workflow
To add new datasets:
1. Add the source and destination paths in `settings.json`.
2. Copy an existing truncate-append block in `wr_updates.py` and update variable names.
3. Optionally add metadata and map export steps.

To disable a section temporarily, comment out its block in `wr_updates.py` or use `--dry-run`.

---

# 10. Future Roadmap
- Retire `\\172.30.73.39\WebFinal` and transition to **ArcGIS Open Data**.
- Replace static Excel exports with dynamic dashboardd feeds.
- Migrate all SDE references to **PostgreSQL Enterprise GDB** connections under CSA.
- Integrate email notifications via Power Automate after run completion.

---

# 11. Dependencies

| **Component** | **Version**           | **Source**                |
| :------------ | :-------------------- | :------------------------ |
| ArcGIS Pro    | 3.4+                  | Esri                      |
| Python        | 3.8+                  | Bundled with ArcGIS Pro   |
| arcpy         | Same as ArcGIS Pro    | Esri                      |
| pywin32       | 306+                  | Esri Conda Channel        |
| pandas        | 2.2+                  | conda-forge               |
| openpyxl      | 3.1%+                 | conda-forge               |

---

# 12. Contact and Maintenance

| **Role**              | **Name**          | **Responsibility**                                                | **Email**                 |
| :-------------------- | :---------------- | :---------------------------------------------------------------- | :------------------------ |
| Primary Maintainer    | Derrick Stark     | GIS Manager, OWRB                                                 | derrick.stark@owrb.ok.gov |
| Support               | OWRB GIS Section  | Maintenance of server paths, connectoions, and <br />credentials  | gisrequests@owrb.ok.gov   |
| Backup Admin          | Scot Roberson     | Fallback contact for Water Rights processes                       | scott.roberson@owrb.ok.gov|

---

# Last Updated: November 2025
# Author: Derrick Stark, Oklahoma Water Resources Board