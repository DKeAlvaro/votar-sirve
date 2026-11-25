"""Extract the few columns charts A and C need from the GESIS microdata into data/interim.

A: Mannheim Eurobarometer Trend File 1970-2002 (GESIS ZA3521, doi:10.4232/1.10074), variable `better`.
C: ISSP Work Orientations I-IV cumulation (GESIS ZA8797, doi:10.4232/1.14391), v19-v21 and v42.
Both need a free GESIS login; put the .dta files in data/raw/cA and data/raw/cC.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "interim"
OUT.mkdir(parents=True, exist_ok=True)

JOBS = {
    "cA": (ROOT / "data/raw/cA/ZA3521_v2-0-1.dta",
           ["year", "eb", "nation1", "wnation", "age", "better", "satislfe"]),
    "cC": (ROOT / "data/raw/cC/ZA8797_v1-0-0.dta",
           ["year", "country", "c_sample", "AGE", "WEIGHT", "v19", "v20", "v21", "v42",
            "EMPREL", "TYPORG2", "MAINSTAT", "WORK"]),
}

for key in sys.argv[1:] or JOBS:
    path, cols = JOBS[key]
    reader = pd.io.stata.StataReader(path)
    labels = reader.value_labels()
    lab_names = reader._lbllist if hasattr(reader, "_lbllist") else None
    varnames = reader._varlist if hasattr(reader, "_varlist") else None
    df = pd.read_stata(path, columns=cols, convert_categoricals=False)
    df.to_csv(OUT / f"{key}_micro.csv", index=False)
    meta = {}
    if lab_names and varnames:
        for v, ln in zip(varnames, lab_names):
            if v in cols and ln in labels:
                meta[v] = {str(k): str(t) for k, t in labels[ln].items()}
    (OUT / f"{key}_labels.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(key, df.shape)
