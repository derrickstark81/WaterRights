'''
********************************************************************************************************************************************************
Tool Name: WR Watermark
Version: Python 3.11.11
Author: DAS (OWRB GIS)

Description: Stores last successful run (UTC) at a fixed path.

History:
    Initial coding - DAS 20251024
********************************************************************************************************************************************************
'''

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any

def read_watermark(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"last_run_utc": None}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_watermark(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"last_run_utc": datetime.now(timezone.utc).isoformat()}, f)