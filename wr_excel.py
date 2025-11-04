"""
*************************************************************************************************************************
Tool Name:  WR_Excel Helpers
Version:    ArcGIS Pro 3.4+ (Python 3.11.x) on Windows
Author:     DAS (OWRB GIS)

Description:
    - Refresh Excel workbook links (equivalent to Data > Edit Links > Open Source / Refresh All)
    - Export a specific cell range to PNG by copying the reante to a temporary ChartObject and exporting the chart.
    - Optional .dbf -> .xlsx helper for the PT 2025 workflow.

Requires:
    - Microsoft Excel installed on the batch server (COM automation).
    - pywin32 available in the ArcGIS Pro Python environment.

History:
    Initial coding - DAS 20251023

Notes:
    - This is designed for server automation. Excel runs headless via COM.
*************************************************************************************************************************
"""

import os
import time
import pythoncom
import win32com.client as win32

def refresh_links(xlsx_path: str) -> None:
    """
    Open workbook, refresh all external links/queries, save, close.
    """

    if not os.path.exists(xlsx_path):
        return
    
    pythoncom.CoInitialize()
    excel = win32.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    try:
        wb = excel.Workbooks.Open(xlsx_path)
        # Refresh links (Edit Links > Open Source equivalent)
        try:
            wb.RefreshAll()
            # Some workbooks need a tiny wait to finish queries
            time.sleep(2)
        except Exception:
            pass
        wb.Save()
        wb.Close(SaveChanges=True)
    finally:
        excel.Quit()
        pythoncom.CoUninitialize()

def export_range_to_png(xlsx_path: str, sheet_name: str, cell_range: str, out_png: str) -> None:
    """
    Export a rectangular cell range to a PNG by pasting the range into a temporary ChartObject and exporting the chart.
    """

    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    pythoncom.CoInitialize()
    excel = win32.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    try:
        wb = excel.Workbooks.Open(xlsx_path)
        ws = wb.Worksheets(sheet_name)
        rng = ws.Range(cell_range)

        # Create a temp chart sized to the range
        ch = ws.ChartObjects().Add(Left=rng.Left, Top=rng.Top, Width=rng.Width, Height=rng.Height)
        chart = ch.Chart

        # Clear default chart and paste the range as a picture into it
        ws.Range(cell_range).CopyPicture(Format=win32.constants.xlPicture)
        chart.Paste()
        chart.Export(Filename=out_png, FilterName="PNG")

        # Clean up
        ch.Delete()
        wb.Close(SaveChanges=False)
    finally:
        excel.Quit()
        pythoncom.CoUninitialize()

def dbf_to_xlsx(dbf_path: str, xlsx_out: str) -> None:
    """
    Minimal helper: open DBF via OLEDB is finicky; the recommended approach is to load the DBF in Excel and Save As.
    This function automates Excel to do that.
    """

    pythoncom.CoInitialize()
    excel = win32.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    try:
        # Force Excel to open DBF; this typically works when DBF is dBASE III/IV
        wb = excel.Workbooks.Open(dbf_path)
        wb.SaveAs(xlsx_out, FileFormat=51) # 51 = xlOpenXMLWorkbook (.xlsx)
        wb.Close(SaveChanges=False)

    finally:
        excel.Quit()
        pythoncom.CoUninitialize()
