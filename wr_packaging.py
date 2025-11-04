'''
********************************************************************************************************************************************************
Tool Name: Wr Packaging (Legacy)
Version: Python 3.11.11
Author: DAS (OWRB GIS)

Description: Build zip packages from a temp folder and copy to \\172.30.73.39\WebFinal paths.

History:
    Initial coding - DAS 20251024
********************************************************************************************************************************************************
'''

import os
import glob
import zipfile
import shutil
from typing import List, Dict, Any, Callable

def _ensure_dir(d: str) -> None:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def build_zip_from_patterns(zip_path: str, source_dir: str, patterns: List[str]) -> int:
    count = 0
    _ensure_dir(os.path.dirname(zip_path))
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for pat in patterns:
            for full in glob.glob(os.path.join(source_dir, pat)):
                if os.path.isfile(full):
                    z.write(full, arcname=os.path.basename(full))
                    count += 1
    return count

def copy_files(patterns: List[str], source_dir: str, dest_dir: str) -> int:
    _ensure_dir(dest_dir)
    count = 0
    for pat in patterns:
        for full in glob.glob(os.path.join(source_dir, pat)):
            if os.path.isfile(full):
                shutil.copy2(full, os.path.join(dest_dir, os.path.basename(full)))
                count += 1
    return count

def remove_files(patterns: List[str], dest_dir: str) -> int:
    count = 0
    for pat in patterns:
        for full in glob.glob(os.path.join(dest_dir, pat)):
            try:
                os.remove(full); count += 1
            except FileNotFoundError:
                pass
    return count

def build_and_publish_packages(cfg: Dict[str, Any], log: Callable[[str], None]) -> None:
    pconf = cfg.get("packaging", {})
    if not pconf:
        log("[PACK] packaging disabled via settings")
        return
    
    webfinal_dir = pconf.get("webfinal_dir", "")
    src_dir = pconf.get("temp_mastercovs_dir", "")
    delete_old = bool(pconf.get("delete_old_first", True))
    packages = pconf.get("packages", [])
    extra_copy = pconf.get("extra_copy", [])

    if not webfinal_dir or not src_dir:
        log("[PACK] missing webfinal_dir/src_dir in settings; skipping")
        return
    
    built = []
    for pkg in packages:
        zip_name = pkg["zip_name"]
        patterns = pkg["include_patterns"]
        zip_path = os.path.join(src_dir, zip_name)
        count = build_zip_from_patterns(zip_path, src_dir, patterns)
        log(f"[PACK] {zip_name}: added {count} files")
        built.append(zip_path)

    if delete_old:
        removed = remove_files([p["zip_name"] for p in packages] + [*extra_copy], webfinal_dir)
        log(f"[PACK] removed {removed} old file(s) from WebFinal")

    copied = 0
    for zip_path in built:
        dest = os.path.join(webfinal_dir, os.path.basename(zip_path))
        shutil.copy2(zip_path, dest)
        copied += 1
    log(f"[PACK] copied {copied} new zip(s) to WebFinal")

    if extra_copy:
        copied_extra = copy_files(extra_copy, src_dir, webfinal_dir)
        log(f"[PACK] copied {copied_extra} extra file(s) to WebFinal")