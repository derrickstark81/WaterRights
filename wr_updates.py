'''
********************************************************************************************************************************************************
Tool Name: WR Updates (Unified Nightly)
Version: ArcGIS Pro 3.4+ Python 3.11.11
Author: DAS (OWRB GIS)

Description: 
    - WR_Main -> OWRT & CSA mirrors
    - LT Points/Lands -> CSA mirrors
    - Metadata imports (optional)
    - Proposals pipeline (CSV -> Proposed_Permits -> WR_Applications -> publish)
    - Static map exports w/Excel overlays
    - Legacy WebFinal packaging (temporary)

History:
    Initial coding - DAS 20251024
********************************************************************************************************************************************************
'''

import os
import sys
import argparse
import datetime
import traceback
import arcpy

from wr_config import load_settings
from wr_logging import make_logger
from wr_watermark import write_watermark
from wr_sde import truncate_append
from wr_metadata import import_fgdc
from wr_proposals import refresh_proposals, publish_pend_points
from wr_maps import export_maps

def parse_args():
    ap = argparse.ArgumentParser(description="Unified WR nightly updates")
    ap.add_argument("--config", help="Path to settings.json (overrides env & local)")
    ap.add_argument("--no-packaging", action="store_true", help="Skip legacy WebFinal packaging step")
    ap.add_argument("--dry-run", action="store_true", help="Report actions without writing")
    return ap.parse_args()

def main():
    args = parse_args()
    cfg = load_settings(args.config)

    logger, write_json, tlog, jlog = make_logger(cfg["paths"]["logs_dir"], level="INFO")
    start = datetime.datetime.now()
    logger.info("=== WR Nightly start: %s ===", start.isoformat())
    write_json({"event":"start","ts":start.isoformat()})

    try:
        arcpy.env.overwriteOutput = True

        # Connections & paths
        owrpgis = cfg["conn"]["owrpgis"]
        owrtgis = cfg["conn"]["owrtgis"]
        csa     = cfg["conn"]["csa"]
        arapaho_wr_gdb  = cfg["paths"]["arapaho_wr_gdb"]
        web_gdb         = cfg["paths"]["web_datastore_gdb"]
        metadata_dir    = cfg["paths"]["metadata_dir"]
        applications_csv= cfg["paths"]["applications_csv"]
        watermark_path  = cfg["paths"]["watermark"]
        ds = cfg["datasets"]

        # 1) WR_Main -> OWRT & CSA
        wr_main_src = os.path.join(arapaho_wr_gdb,  ds["wr_main"]["arapaho"])
        wr_main_owrt = os.path.join(owrtgis,        ds["wr_main"]["owrtgis"])
        wr_main_csa = os.path.join(csa,             ds["wr_main"]["csa"])
        logger.info("[WR_MAIN] refresh OWRT")
        if not args.dry_run: truncate_append(wr_main_src, wr_main_owrt)
        logger.info("[WR_MAIN] refresh CSA")
        if not args.dry_run: truncate_append(wr_main_src, wr_main_csa)

        # 2) LT Points/Lands -> CSA
        lt_pts_src = os.path.join(owrpgis,  ds["lt_points"]["owrpgis"])
        lt_pts_csa = os.path.join(csa,      ds["lt_points"]["csa"])
        lt_land_src= os.path.join(owrpgis,  ds["lt_lands"]["owrpgis"])
        lt_land_csa= os.path.join(csa,      ds["lt_lands"]["csa"])
        logger.info("[LT_POINTS] CSA mirror")
        if not args.dry_run: truncate_append(lt_pts_src, lt_pts_csa)
        logger.info("[LT_LANDS] CSA mirror")
        if not args.dry_run: truncate_append(lt_land_src, lt_land_csa)

        # 3) Metadata (optional)
        if import_fgdc(os.path.join(metadata_dir, ds["lt_points"]["md_xml"]), lt_pts_csa):
            logger.info("[MD] LT Points metadata imported")
        if import_fgdc(os.path.join(metadata_dir, ds["lt_lands"]["md_xml"]), lt_land_csa):
            logger.info("[MD] LT Lands metadata imported")
        if import_fgdc(os.path.join(metadata_dir, ds["wr_main_md"]["md_xml"]), wr_main_csa):
            logger.info("[MD] WR_MAIN metadata imported")

        # 4) Proposals pipeline
        logger.info("[Proposals] CSV -> Proposed_Permits / WR_Applications")
        wr_apps_src = refresh_proposals(
            applications_csv=applications_csv,
            web_gdb=web_gdb,
            proposed_name=ds["proposals"]["proposed_permits"],
            applications_name=ds["proposals"]["wr_applications"],
            owrpgis_pts_view=os.path.join(owrpgis, ds["lt_points"]["owrpgis"]),
            join_key_csv=ds["proposals"]["join_key_csv"],
            join_key_pts=ds["proposals"]["join_key_pts"]
        )
        logger.info("[Proposals] Publish pending points to OWRT & CSA")
        if not args.dry_run:
            publish_pend_points(
                source_wr_apps=wr_apps_src,
                owrt_dest=os.path.join(owrtgis, ds["proposals"]["owrt_points_pend"]),
                csa_dest=os.path.join(csa,      ds["proposals"]["csa_points_pend"])
            )

        # 5) Static map exports + Excel overlays
        logger.info("[MAP] Exporting WR map (PDF/JPG) + Excel overlays")
        if not args.dry_run:
            export_maps(cfg, logger, dpi=300)

        # 6) Legacy packaging to \\172.30.73.39\WebFinal (temporary)
        if not args.no_packaging and cfg.get("packaging") and not args.dry_run:
            from wr_packaging import build_and_publish_packages
            logger.info("[PACK] Building & publishing packages to WebFinal")
            build_and_publish_packages(cfg, lambda m: logger.info(m))
        else:
            logger.info("[PACK] Skipped (disabled or dry-run)")

        # Watermark
        write_watermark(watermark_path)

        end = datetime.datetime.now()
        logger.info("=== WR Nightly success: %s (elapsed %s) ===", end.isoformat(), end-start)
        write_json({"event":"success","ts":end.isoformat(),"elapsed_sec":(end-start).total_seconds(),
                    "text_log":tlog,"json_log":jlog})
        return 0
    
    except Exception as e:
        trace = traceback.format_exc()
        logger.error("*** FAILURE ***\n%s", trace)
        write_json({"event":"failure","error":str(e),"trace":trace})
        return 1
    
if __name__ == "__main__":
    sys.exit(main())