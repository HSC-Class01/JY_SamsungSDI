from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/"SamsungSDI_OpenDART_Agent.zip"
EXCLUDE_DIRS={".git",".github","__pycache__",".venv","venv"}
EXCLUDE_NAMES={".env"}
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED) as z:
    for p in ROOT.rglob("*"):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts) or p.name in EXCLUDE_NAMES:
            continue
        if p.name.endswith(".pyc"): continue
        z.write(p,rel)
print(OUT)
