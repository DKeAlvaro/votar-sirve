"""Discover ES/NL samples and the question ids for the cB items in each WVS online-analysis wave.
Usage: python -I scripts/cB_wvs_discover.py  -> data/raw/cB/discover.json"""
import requests, re, json, os, sys
B="https://www.worldvaluessurvey.org/"
WAVES={346:"1981-84",345:"1990-94",341:"1995-98",12:"1999-2004",2:"2005-09",1:"2010-14",1562:"2017-22"}
OUT="data/raw/cB"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0"
s.get(B+"AJOnline.jsp",timeout=20)
res={}
for w,lab in WAVES.items():
    r=s.post(B+"AJOnlineCountries.jsp",data={"WAVE":w,"MAIDX":"","COUNTRY":"","ulthost":"WVS"},timeout=25)
    h=r.text
    samples=[]
    for m in re.finditer(r'value="(\d+):(\d+)"\s*onclick="[^"]*"\s*title="([^"]*)"',h,re.S):
        if m.group(1) in ("724","528"): samples.append(m.groups())
    sa=[x for x in samples]
    print(lab,sa)
    if not sa: res[w]={"label":lab,"samples":[],"questions":{}}; continue
    ids=",".join(x[1] for x in sa); am=",".join(x[0] for x in sa)
    r=s.post(B+"AJOnlineIndex.jsp",data={"WAVE":w,"SAIDS":ids,"AMIDS":am,"ulthost":"WVS"},timeout=30)
    open(f"{OUT}/index_{w}.html","w",encoding="utf-8").write(r.text)
    rows=re.findall(r"ShowQuestion\('([A-Z]_\d+)'\)\">([^<]*)</a></td>\s*<td>([^<]*)</td>",r.text)
    res[w]={"label":lab,"samples":sa,"questions":{c:[n,t] for c,n,t in rows}}
json.dump(res,open(f"{OUT}/discover.json","w"),indent=1)
