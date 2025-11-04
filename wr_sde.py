'''
********************************************************************************************************************************************************
Tool Name: WR SDE helpers
Version: ArcGIS Pro 3.4+ Python 3.11.11
Author: DAS (OWRB GIS)

Description: Simple mirror refresh via Truncate + Append (idempotent for non-editable targets).

History:
    Initial coding - DAS 20251024
********************************************************************************************************************************************************
'''

import arcpy

def truncate_append(src: str, dest: str, field_map: str = "", schema_type: str = "NO_TEST") -> None:
    arcpy.management.TruncateTable(dest)
    arcpy.management.Append(src, dest, schema_type, field_map)