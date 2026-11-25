"""Harvest WVS online-analysis crosstabs (item x single-year Age) for Spain/Netherlands samples.
Reads data/raw/cB/discover.json (from cB_wvs_discover.py). Writes data/raw/cB/qtn_*.html.gz (raw),
data/raw/cB/trans_*.txt (original-language wording) and data/clean/cB_wvs_age.csv (long: counts per age/response).
Usage: python -I scripts/cB_wvs_harvest.py"""
import requests, re, json, gzip, os, csv, html
B="https://www.worldvaluessurvey.org/"
OUT="data/raw/cB"
d=json.load(open(f"{OUT}/discover.json"))
ITEMS={ # variable -> regex on title
 "E040_hardwork":r"^Hard work brings success$|^Success: hard work vs luck$",
 "A173_freedom":r"^How much freedom of choice and control$",
 "A170_lifesat":r"^Satisfaction with your life$",
 "E039_competition":r"^Competition good or harmful$",
 "E036_ownership":r"^Private vs state ownership of business$",
 "E037_govresp":r"^Government responsibility$|^Government's vs individual's responsibility$",
}
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0"; s.get(B+"AJOnline.jsp",timeout=20)
rows=[]; wording={}
def txt(x): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",x))).strip()
for w,v in d.items():
    for (am,sa,title) in v["samples"]:
        for var,pat in ITEMS.items():
            qs=[c for c,(n,t) in v["questions"].items() if re.search(pat,t.strip())]
            if not qs: continue
            q=qs[0]; vname=v["questions"][q][0]
            fn=f"{OUT}/qtn_{w}_{sa}_{var}.html.gz"
            if os.path.exists(fn): h=gzip.open(fn,"rt",encoding="utf-8").read()
            else:
                base={"WAVE":w,"SAIDS":sa,"AMIDS":am,"MAIDX":q,"ulthost":"WVS"}
                h0=s.post(B+"AJOnlineQtn.jsp",data=base,timeout=40).text
                m=re.search(r"<option value='(\d+)'>Age</option>",h0)
                if not m: print("no age var",w,sa,var); continue
                h=s.post(B+"AJOnlineQtn.jsp",data={**base,"MACRUCE1":m.group(1),"MACRUCE2":""},timeout=60).text
                gzip.open(fn,"wt",encoding="utf-8").write(h)
            i=h.find("Question wording"); j=h.find("Equivalences",i)
            wording[(w,sa,var)]=(title,vname,txt(h[i+16:j]))
            # translation (original language), Spanish samples only
            tf=f"{OUT}/trans_{w}_{sa}_{var}.txt"
            if not os.path.exists(tf):
                hb=s.post(B+"AJOnlineQtn.jsp",data={"WAVE":w,"SAIDS":sa,"AMIDS":am,"MAIDX":q,"ulthost":"WVS"},timeout=40).text
                mt=re.search(r"<option value=\"(\d+)\" >((?:Spain|Netherlands)[^<]*)</OPTION>",hb,re.I)
                if mt:
                    r=s.post(B+"AJOnlineQtnTextTrad.jsp",data={"WAVE":w,"SAIDS":sa,"AMIDS":am,"MAIDX":q,"PSIDSA":mt.group(1),"ulthost":"WVS"},timeout=40)
                    open(tf,"w",encoding="utf-8").write(txt(r.text)+" || "+mt.group(2))
            # parse table
            mtab=re.search(r"<table style='table-layout:fixed;width:680px;'.*?</table>",h,re.S)
            if not mtab: print("no table",w,sa,var); continue
            trs=re.findall(r"<tr[^>]*>(.*?)</tr>",mtab.group(0),re.S)
            cells=[[txt(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>",tr,re.S)] for tr in trs]
            cells=[c for c in cells if any(c)]
            hdr=None
            for k,c in enumerate(cells):
                if len(c)>=2 and c[1]=="TOTAL": hdr=k+1;break
            if hdr is None: print("no hdr",w,sa,var); continue
            cols=cells[hdr]
            for c in cells[hdr+1:]:
                if len(c)<3: continue
                for a,val in zip(["TOTAL"]+cols,c[1:]):
                    rows.append((w,v["label"],title,sa,var,vname,c[0],a,val))
            print("ok",v["label"],title,var,len(cells))
with open("data/raw/cB/harvest_long.csv","w",newline="",encoding="utf-8") as f:
    wr=csv.writer(f); wr.writerow("wave,wave_label,sample,said,var,vname,row,age,cell".split(",")); wr.writerows(rows)
json.dump({"|".join(map(str,k)):v for k,v in wording.items()},open(f"{OUT}/wording.json","w"),indent=1,ensure_ascii=False)
