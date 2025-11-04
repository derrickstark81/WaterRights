'''
********************************************************************************************************************************************************
Tool Name: WR Config Loader
Version: Python 3.11.11
Author: DAS (OWRB GIS)

Description: Loads settings from --config, env WR_SETTINGS_PATH, or local settings.json.

History:
    Initial coding - DAS 20251024
********************************************************************************************************************************************************
'''

import json
import os
import pathlib
from typing import Dict, Any, Optional

WR_SETTINGS_ENV = "WR_SETTINGS_PATH"

def load_settings(config_override: Optional[str] = None) -> Dict[str, Any]:
    if config_override:
        p = pathlib.Path(config_override)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        
    env_path = os.environ.get(WR_SETTINGS_ENV, "").strip()
    if env_path and os.path.exists(env_path):
        return json.loads(pathlib.Path(env_path).read_text(encoding="utf-8"))
    
    here = pathlib.Path(__file__).parent / "settings.json"
    if here.exists():
        return json.loads(here.read_text(encoding="utf-8"))
    
    raise FileNotFoundError(
        "No settings.json found and WR_SETTINGS_PATH not set. "
        "Place settings.json next to scripts or set WR_SETTINGS_PATH or pass --config."
    )