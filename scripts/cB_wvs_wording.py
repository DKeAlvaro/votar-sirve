"""Fetch original-language wording (WVS 'Additional translations') for Spain/Netherlands samples.
Output: data/clean/cB_wording.csv (item,wave,translation_sample,text,english_items)"""
import requests,re,json,html,csv
B="https://www.worldvaluessurvey.org/"
d=json.load(open('data/raw/cB/discover.json'))
ITEMS={"E040_hardwork":r"^Hard work brings success$|^Success: hard work vs luck$","A173_freedom":r"^How much freedom of choice and control$","A170_lifesat":r"^Satisfaction with your life$","E039_competition":r"^Competition good or harmful$","E036_ownership":r"^Private vs state ownership of business$","E037_govresp":r"^Government responsibility$|^Government's vs individual's responsibility$"}
s=requests.Session(); s.get(B+"AJOnline.jsp")
def txt(x): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",x))).strip()
out=[]; seen=set()
for w,v in d.items():
    if not v['samples']: continue
    am,sa,t=v['samples'][0]
    for var,pat in ITEMS.items():
        q=[c for c,(n,tt) in v['questions'].items() if re.search(pat,tt.strip())]
        if not q: continue
        base={"WAVE":w,"SAIDS":sa,"AMIDS":am,"MAIDX":q[0],"ulthost":"WVS"}
        h=s.post(B+"AJOnlineQtn.jsp",data=base,timeout=40).text
        i=h.find("Question wording"); j=h.find("Equivalences",i)
        eng=txt(h[i+16:j])
        for ps,nm in re.findall(r'<option value="(\d+)" >((?:Spain|Netherlands)[^<]*)</OPTION>',h,re.I):
            r=s.post(B+"AJOnlineQtnTextTrad.jsp",data={**base,"PSIDSA":ps},timeout=40).content.decode("cp1252",errors="replace")
            m=re.search(r"<textarea name=PSID>(.*?)</textarea>",r,re.S)
            tr=txt(m.group(1)) if m else ""
            out.append((var,v['label'],nm,tr,eng))
            print(var,v['label'],nm,tr[:80])
with open('data/clean/cB_wording.csv','w',newline='',encoding='utf-8') as f:
    w_=csv.writer(f); w_.writerow(['item','wave','translation_sample','text_original_language','text_english']); w_.writerows(out)
