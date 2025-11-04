'''
********************************************************************************************************************************************************
Tool Name: WR Logging
Version: Python 3.11.11
Author: DAS (OWRB GIS)

Description: Rotating text log + JSONL event log (+ console).

History:
    Initial coding - DAS 20251024
********************************************************************************************************************************************************
'''

import os
import json
import logging
import logging.handlers
import datetime
from typing import Callable, Tuple

def _ensure(d: str) -> None:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def make_logger(logs_dir: str, level: str = "INFO") -> Tuple[logging.Logger, Callable[[dict], None], str, str]:
    _ensure(logs_dir)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    text_log = os.path.join(logs_dir, f"WR_Nightly_{ts}.log")
    json_log = os.path.join(logs_dir, f"WR_Nightly_{ts}.jsonl")

    logger = logging.getLogger("wr_nightly")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    fhandler = logging.handlers.RotatingFileHandler(text_log, maxBytes=2*1024*1024, backupCount=10, encoding="utf-8")
    fhandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fhandler)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    logger.addHandler(ch)

    def write_json(obj: dict) -> None:
        with open(json_log, "a", encoding="utf-8") as jf:
            jf.write(json.dumps(obj, default=str) + "\n")

    return logger, write_json, text_log, json_log