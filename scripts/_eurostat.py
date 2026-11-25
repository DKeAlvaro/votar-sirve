import requests,json,os,time
B='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/%s?format=JSON&lang=en&%s'
def fetch(code,params,raw):
    if not os.path.exists(raw):
        os.makedirs(os.path.dirname(raw),exist_ok=True)
        q='&'.join('%s=%s'%(k,v) for k,v in params)
        for i in range(3):
            try:
                r=requests.get(B%(code,q),timeout=25);r.raise_for_status();break
            except Exception as e: err=e;time.sleep(2)
        else: raise err
        open(raw,'w',encoding='utf-8').write(r.text)
    return json.load(open(raw,encoding='utf-8'))
def rows(d):
    ids=d['id'];dim=d['dimension'];idx={k:list(dim[k]['category']['index']) for k in ids}
    out=[]
    for flat,v in d['value'].items():
        f=int(flat);pos={}
        for k in reversed(ids):
            n=len(idx[k]);pos[k]=idx[k][f%n];f//=n
        pos['value']=v;out.append(pos)
    return out
