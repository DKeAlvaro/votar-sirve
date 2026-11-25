"""Chart A, 1996-2025: 'life in general, next 12 months: better / worse / same' from single
Eurobarometer waves (GESIS ZA numbers in data/raw/cA/eb/list.txt plus ZA3085).

Usage: python -I scripts/cA_eb_waves.py scan   -> print candidate variables per file
       python -I scripts/cA_eb_waves.py build  -> data/interim/cA_eb_waves.csv (ES, NL rows)
"""
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EB = ROOT / "data/raw/cA/eb"
OVERRIDE = {}  # ZA number -> {"life"|"age"|"weight": varname} when the label scan picks wrong


def dta_files():
    for z in sorted(EB.glob("*.zip")):
        with zipfile.ZipFile(z) as f:
            for n in f.namelist():
                if n.endswith(".dta") and not (EB / Path(n).name).exists():
                    (EB / Path(n).name).write_bytes(f.read(n))
    return sorted(EB.glob("ZA*.dta"))


def pick(labels, pats, exclude=None):
    out = []
    for k, v in labels.items():
        s = f"{k} {v}"
        if all(re.search(p, s, re.I) for p in pats) and not (exclude and re.search(exclude, s, re.I)):
            out.append(k)
    return out


def find_vars(labels):
    life = pick(labels, [r"life in general"], r"satisf|five years|5 years|two years|2 years|compared|past|last")
    life = [k for k in life if re.search(r"expect|next|year to come|12 m|twelve|better|futur", labels[k], re.I)] or life
    age = pick(labels, [r"age"], r"stud|educ|left|start|quit|marri|child|house|cohort|langu|voyage|manage|stage|wage|percent|engage|image|average|pass|message|usage|damage|mortgage|baggage|page|village|leave|heritage|teen")
    age_exact = [k for k in age if re.search(r"exact", labels[k], re.I)] or age
    weight = pick(labels, [r"weight result from target"]) or pick(labels, [r"post.?strat|weight.*target|w1\b"])
    country = ["isocntry"] if "isocntry" in labels else pick(labels, [r"ISO 3166"])
    return life, age_exact, weight, country


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    rows = []
    for f in dta_files():
        r = pd.io.stata.StataReader(f)
        lab = r.variable_labels()
        life, age, weight, country = find_vars(lab)
        if mode == "scan":
            print(f.name)
            print("  life:", [(k, lab[k][:70]) for k in life])
            print("  age:", [(k, lab[k][:50]) for k in age][:4])
            print("  weight:", [(k, lab[k][:50]) for k in weight][:3], "country:", country[:2])
            if len(life) > 1:
                d = pd.read_stata(f, columns=[country[0]] + life, convert_categoricals=False)
                d = d[d[country[0]].astype(str).str.strip() == "ES"]
                for k in life:
                    print("   ES", k, d[k].value_counts(dropna=False).sort_index().to_dict())
            continue
        over = OVERRIDE.get(f.name.split("_")[0], {})
        lv, av, wv = over.get("life", life[0]), over.get("age", age[0]), over.get("weight", weight[0])
        df = pd.read_stata(f, columns=[country[0], lv, av, wv], convert_categoricals=False)
        vl = r.value_labels()
        lname = dict(zip(r._varlist, r._lbllist)).get(lv)
        codes = {}
        for code, text in vl.get(lname, {}).items():
            t = str(text).lower()
            codes[code] = "better" if "better" in t else "worse" if "worse" in t else "same" if "same" in t else "dk"
        df.columns = ["iso", "life", "age", "w"]
        df["life"] = df["life"].map(codes).fillna("dk")
        df = df[df.iso.astype(str).str.strip().isin(["ES", "NL"])]
        df["za"] = f.name.split("_")[0]
        rows.append(df)
        print(f.name, lv, av, wv, len(df))
    if mode == "build":
        pd.concat(rows).to_csv(ROOT / "data/interim/cA_eb_waves.csv", index=False)

