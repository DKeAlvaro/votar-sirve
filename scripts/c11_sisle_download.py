"""Download all SISLE national summary PDFs listed on the Ministerio de Sanidad page. Run from repo root."""
import re,os,urllib.request,urllib.parse
P='https://www.sanidad.gob.es/estadEstudios/estadisticas/inforRecopilaciones/'
R='data/raw/c11/sisle/'
t=open('data/raw/c11/listaEsperaInfAnt.htm',encoding='utf8',errors='ignore').read()
t+=open('data/raw/c11/listaEspera.htm',encoding='utf8',errors='ignore').read()
links=sorted(set(re.findall(r'href="([^"]+\.pdf)"',t)))
for l in links:
    if 'boe.es' in l: continue
    u=urllib.parse.urljoin(P+'listaEsperaInfAnt.htm',l.strip()); fn=R+os.path.basename(u)
    if os.path.exists(fn) and os.path.getsize(fn)>1000: continue
    try:
        req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
        open(fn,'wb').write(urllib.request.urlopen(req,timeout=25).read()); print('ok',fn)
    except Exception as e: print('FAIL',u,e)
