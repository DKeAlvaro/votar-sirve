import requests,json,os,time
B='https://servicios.ine.es/wstempus/js/ES/'
def get(path,raw=None,tries=3):
    if raw and os.path.exists(raw):
        return json.load(open(raw,encoding='utf-8'))
    for i in range(tries):
        try:
            r=requests.get(B+path,timeout=25)
            r.raise_for_status()
            d=r.json()
            if raw:
                os.makedirs(os.path.dirname(raw),exist_ok=True)
                open(raw,'w',encoding='utf-8').write(r.text)
            return d
        except Exception as e:
            err=e;time.sleep(2)
    raise err
