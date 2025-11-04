"""
********************************************************************************************************************************************************
Tool Name: WR_Maps (Static Exports + Excel Overlays)
Version: ArcGIS Pro 3.4+ (Python 3.11.x)
Author: DAS (OWRB GIS)

Description:
    - Export WR GW/SW/Apps/PT layouts PDF and JPEG
    - Stamp "LastUpdated" TEXT_ELEMENT with today's date (if present).
    - If configured, export Excel table ranges to PNG and replace named PictureElements in layouts.
    - Copy results to both \\OWRBGIS\GeoDat\Maps\... targets and \\172.30.73.39\WebFinal\maps\pdf_map\ as required by SOP.

History:
    Initial Coding - DAS 20251023

SOP references:
    - Export GW/SW/Apps/PT maps to \\OWRBGIS\GeoDat folders, ensure current date on layouts, then copy PDFs to \\17230.73.39\WebFinal\maps\pdf_map
        (The "Updating the Water Rights Maps" document)
********************************************************************************************************************************************************
"""

import os
import shutil
import datetime
import arcpy

from wr_excel import refresh_links, export_range_to_png, dbf_to_xlsx

def _ensure(p: str) -> None:
    if not os.path.exists(p):
        os.makedirs(p, exist_ok=True)

def _set_layout_date(layout) -> None:
    for el in layout.listElements("TEXT_ELEMENT"):
        if el.name == "LastUpdated":
            el.text = datetime.date.today().strftime("%B %d, %Y")

def _replace_picture(layout, element_name: str, png_path: str) -> bool:
    pe = next((e for e in layout.listElements("MAPSURROUND_ELEMENT") if e.name == element_name), None)
    if pe is None:
        pe = next((e for e in layout.listElements("PICTURE_ELEMENT") if e.name == element_name), None)
    if pe is None or not os.path.exists(png_path):
        return False
    
    # Modern Pro uses PICTURE_ELEMENT for images
    try:
        pe.sourceImage = png_path
        return True
    except Exception:
        return False
    
def _export_layout(aprx_path: str, layout_name: str, out_dir: str, dpi: int = 300) -> tuple[str, str]:

    proj = arcpy.mp.ArcGISProject(aprx_path)
    layout = next((ly for ly in proj.listLayouts() if ly.name == layout_name), None)
    if layout is None:
        return "", ""
    _set_layout_date(layout)
    safe = layout_name.replace(" ", "_")
    pdf_out = os.path.join(out_dir, f"{safe}.pdf")
    jpg_out = os.path.join(out_dir, f"{safe}.jpg")
    layout.exportToPDF(pdf_out, resolution=dpi)
    layout.exportToJPEG(jpg_out, resolution=dpi)
    return pdf_out, jpg_out

def _copy_to_targets(pdf_path: str, jpg_path: str, g_out: str, v_pdf: str) -> None:
    for pth in (g_out, v_pdf):
        _ensure(pth)
    if pdf_path and os.path.exists(pdf_path):
        shutil.copy2(pdf_path, os.path.join(v_pdf, os.path.basename(pdf_path))) # V:\ pdf sink
        shutil.copy2(pdf_path, os.path.join(g_out, os.path.basename(pdf_path)))
    if jpg_path and os.path.exists(jpg_path):
        shutil.copy2(jpg_path, os.path.join(g_out, os.path.basename(jpg_path)))

def _run_overlay(overlay_cfg: dict, cfg: dict, staging_dir: str, logger) -> None:
    paths = cfg["paths"]
    maps_out = paths["maps_out"]
    aprx = paths["aprx"]
    sums = paths["sum_tables"]

    aprx_key    = overlay_cfg["aprx"]
    layout_nm   = overlay_cfg["layout"]
    wb_key      = overlay_cfg["workbook"]
    sheet       = overlay_cfg["sheet"]
    cell_rng    = overlay_cfg["range"]
    pic_name    = overlay_cfg["picture_element"]

    # PT 2025 special: convert DBF to XLSX ahead of time if workbook is pt_2025_xlsx
    if wb_key == "pt_2025_xlsx":
        dbf = sums["pt_2025_dbf"]
        xlsx = sums["pt_2025_xlsx"]
        if os.path.exists(dbf) and not os.path.exists(xlsx):
            logger.info("[MAP] Converting DBF -> XLSX for PT 2025: %s", dbf)
            dbf_to_xlsx(dbf, xlsx)

    wb_path = sums[wb_key] if wb_key in sums else wb_key # allow absolute override
    refresh_links(wb_path)

    png_out = os.path.join(staging_dir, f"{layout_nm.replace(' ', '_')}_overlay.png")
    export_range_to_png(wb_path, sheet, cell_rng, png_out)

    aprx_path = aprx[aprx_key]
    proj = arcpy.mp.ArcGISProject(aprx_path)
    layout = next((ly for ly in proj.listLayouts() if ly.name == layout_nm), None)
    if not layout:
        logger.warning("[MAP] Layout not found for overlay: %s | %s", aprx_path, layout_nm)
        return
    
    if _replace_picture(layout, pic_name, png_out):
        logger.info("[MAP] Replaced picture '%s' on %s", pic_name, layout_nm)
        proj.save() # persist replaced image path if desired
    else:
        logger.warning("[MAP] Could not replace picture '%s' on %s", pic_name, layout_nm)

def export_maps(cfg: dict, logger, dpi: int = 300) -> int:
    paths = cfg["paths"]
    maps_out = paths["maps_out"]
    aprx = paths["aprx"]
    staging = paths.get("map_export_dir_staging", "")
    _ensure(staging)

    maps = cfg.get("maps", {})
    overlays = cfg.get("map_overlays", {})

    # 1) Overlays (Excel tables pasted as pictures) BEFORE exporting layouts
    for name, ocfg in overlays.items():
        try:
            _run_overlay(ocfg, cfg, staging, logger)
        except Exception as ex:
            logger.warning("[MAP] Overlay '%s' failed: %s", name, ex)

    # 2) Export layouts (PDF/JPG), copy to targets per SOP
    total = 0
    def _batch(aprx_key: str, layouts_key: str, g_key: str):
        nonlocal total
        if aprx_key not in aprx or layouts_key not in maps: return
        for layout_nm in maps[layouts_key]:
            pdf, jpg = _export_layout(aprx[aprx_key], layout_nm, staging, dpi=dpi)
            _copy_to_targets(pdf, jpg, maps_out[g_key], maps_out["pdf_push"])
            total += 2 if (pdf and jpg) else 0

    _batch("gw",  "gw_layouts", "gw")
    _batch("sw",  "sw_layouts", "sw")
    _batch("apps", "apps_layouts", "apps")
    _batch("pt", "pt_layouts", "pt")

    logger.info("[MAP] Exported %d files (pdf+jpg) to staging and copied to targets", total)
    return total