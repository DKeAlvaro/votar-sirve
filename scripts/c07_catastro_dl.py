import sys,re,os,requests,concurrent.futures as cf
prov=sys.argv[1]; out=sys.argv[2]; os.makedirs(out,exist_ok=True)
feed=requests.get(f"https://www.catastro.hacienda.gob.es/INSPIRE/buildings/{prov}/ES.SDGC.bu.atom_{prov}.xml",timeout=60).text
urls=sorted(set(re.findall(r'href="([^"]*\.zip)"',feed)))
print(len(urls),flush=True)
def get(u):
    code=re.search(r'BU\.(\d+)\.zip',u).group(1); p=f"{out}/{code}.zip"
    if os.path.exists(p) and os.path.getsize(p)>1000: return code,os.path.getsize(p)
    for _ in range(3):
        try:
            r=requests.get(u,timeout=120); r.raise_for_status()
            open(p,'wb').write(r.content); return code,len(r.content)
        except Exception as e: err=e
    return code,str(err)
with cf.ThreadPoolExecutor(6) as ex:
    tot=0
    for c,s in ex.map(get,urls):
        if isinstance(s,int): tot+=s
        else: print('FAIL',c,s,flush=True)
print('done',tot,flush=True)
