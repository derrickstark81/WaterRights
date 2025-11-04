'''
********************************************************************************************************************************************************
Tool Name: WR Metadata
Version: ArcGIS Pro 3.4+ Python 3.11.11
Author: DAS (OWRB GIS)

Description: Minimal FGDC metadata import using arcpy.conversion.ImportMetadata.

History:
    Initial coding - DAS 20251024
********************************************************************************************************************************************************
'''

import arcpy
import os

def import_fgdc(md_xml_path: str, target: str) -> bool:
    if not os.path.exists(md_xml_path):
        return False
    arcpy.conversion.ImportMetadata(md_xml_path, "FROM_FGDC", target, "ENABLED")
    return True