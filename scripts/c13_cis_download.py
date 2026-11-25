"""Download CIS post-electoral microdata zips (free, no registration needed: direct links on each study page).
Run from repo root: python -I scripts/c13_cis_download.py"""
import os,urllib.request,subprocess
S={1982:(1327,1547136),1986:(1542,1548496),1989:(1842,1549736),1993:(2061,1550871),1996:(2210,1551666),
   2000:(2384,1552491),2004:(2559,1553366),2008:(2757,1554341),2011:(2920,1555156),2015:(3126,1556266),2016:(3145,1556361),
   '2019a':(3248,1556906),'2019b':(3269,1557046),2023:(3420,1558341)}
import sys
for y,(n,fid) in S.items():
    d='data/raw/c13/cis/%d/'%n; os.makedirs(d,exist_ok=True); fn=d+'MD%d.zip'%n
    if os.path.exists(fn) and subprocess.call(['unzip','-tq',fn],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)==0: continue
    u='https://www.cis.es/documents/20117/%d/MD%d.zip'%(fid,n)
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    open(fn,'wb').write(urllib.request.urlopen(req,timeout=120).read()); print('ok',fn,flush=True)
