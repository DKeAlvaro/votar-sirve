"""Download full tables from Seguridad Social PXWeb (ASP.NET) as csv/px by driving the form."""
import requests,re,html,urllib.parse
BASE='https://w6.seg-social.es/PXWeb/pxweb/es/Afiliados%20en%20alta%20laboral/Afiliados%20en%20alta%20laboral__Afiliados%20Medios/'
def hidden(t):
    return {m.group(1):html.unescape(m.group(2)) for m in re.finditer(r'<input type="hidden" name="([^"]*)"[^>]*value="([^"]*)"',t)}
def selects(t):
    out={}
    for m in re.finditer(r'<select[^>]*name="([^"]*ValuesListBox)"[^>]*>(.*?)</select>',t,re.S):
        out[m.group(1)]=[html.unescape(x) for x in re.findall(r'<option[^>]*value="([^"]*)"',m.group(2))]
    return out
def table(name,subset=None,fmt=None,timeout=28):
    s=requests.Session()
    url=BASE+urllib.parse.quote(name)+'/'
    r=s.get(url,timeout=timeout);t=r.text
    data=hidden(t);sel=selects(t)
    pairs=list(data.items())
    for k,vals in sel.items():
        for v in vals:
            pairs.append((k,v))
    pairs.append(('ctl00$ContentPlaceHolderMain$VariableSelector1$VariableSelector1$ButtonViewTable','Continuar'))
    r=s.post(url,data=pairs,timeout=timeout)
    return s,r

def download(name,out,ftype='FileTypePX',timeout=28):
    import os
    if os.path.exists(out): return out
    s,r=table(name,timeout=timeout)
    u=BASE+urllib.parse.quote(name)+'/table/tableViewLayout1/?downloadfile='+ftype
    r=s.get(u,timeout=timeout)
    r.raise_for_status()
    os.makedirs(os.path.dirname(out),exist_ok=True)
    open(out,'wb').write(r.content)
    return out
