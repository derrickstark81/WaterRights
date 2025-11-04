'''
********************************************************************************************************************************************************
Tool Name: WR Proposals
Version: ArcGIS Pro 3.4+ Python 3.11.11
Author: DAS (OWRB GIS)

Description: CSV -> Proposed_Permits -> WR_Applications (join to points) -> publish to OWRT & CSA.

History:
    Initial coding - DAS 20251024
********************************************************************************************************************************************************
'''

import arcpy
import os

def refresh_proposals(applications_csv: str, web_gdb: str,
                      proposed_name: str, applications_name: str,
                      owrpgis_pts_view: str, join_key_csv: str, join_key_pts: str) -> str:
    proposed = os.path.join(web_gdb, proposed_name)
    wr_apps = os.path.join(web_gdb, applications_name)

    # Proposed_Permits from CSV
    arcpy.management.TruncateTable(proposed)
    arcpy.management.Append(applications_csv, proposed, "NO_TEST")

    # Join OWRBGIS points to permits and dissolve by PermitNo
    pts_layer = "wr_pts_layer"
    arcpy.management.MakeFeatureLayer(owrpgis_pts_view, pts_layer)
    arcpy.management.AddJoin(pts_layer, join_key_pts, proposed, join_key_csv, "KEEP_COMMON")
    dissolved = arcpy.management.Dissolve(pts_layer, r"in_memory\z_WR_Applications",
                                          f"{proposed}.{join_key_csv}")[0]
    arcpy.management.TruncateTable(wr_apps)
    arcpy.management.Append(dissolved, wr_apps, "NO_TEST")
    return wr_apps

def publish_pend_points(source_wr_apps: str, owrt_dest: str, csa_dest: str) -> None:
    for dest in (owrt_dest, csa_dest):
        arcpy.management.TruncateTable(dest)
        arcpy.management.Append(source_wr_apps, dest, "NO_TEST")