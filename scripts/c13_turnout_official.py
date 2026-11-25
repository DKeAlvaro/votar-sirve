"""c13: official Congreso turnout per general election from Ministerio del Interior open data
(data/raw/c13/interior/Elecciones-Congreso.xlsx, https://descargas.interior.gob.es/datasets/resultados_electorales/Elecciones-Congreso.xlsx;
the infoelectoral site is behind Cloudflare for curl, the descargas host is not).
turnout (official headline) = (Votantes - Votantes CERA) / Electores CER = residents only; also total incl. CERA = Votantes/Electores.
Output data/clean/c13_turnout_official.csv. Run from repo root: python -I scripts/c13_turnout_official.py"""
import openpyxl,csv,datetime
ws=openpyxl.load_workbook('data/raw/c13/interior/Elecciones-Congreso.xlsx',read_only=True).active
D={}
for r in ws.iter_rows(min_row=5,values_only=True):
    if isinstance(r[0],datetime.datetime) and r[3] in('Electores','Electores CER','Votantes','Votantes CERA'):
        D.setdefault(r[0],{})[r[3]]=sum(x for x in r[4:56] if isinstance(x,(int,float)))
rows=[]
for d,v in sorted(D.items()):
    if d.year<1977 or 'Votantes' not in v: continue
    t=100*(v['Votantes']-v.get('Votantes CERA',0))/v['Electores CER']   # headline convention: residents (CER) only
    ta=100*v['Votantes']/v['Electores']
    rows.append(['%d-%02d'%(d.year,d.month) if d.year==2019 else str(d.year),round(t,2),v['Electores'],v['Votantes'],round(ta,2)])
    print(d.date(),rows[-1])
with open('data/clean/c13_turnout_official.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','))
    for r in rows:
        w.writerow([r[0],'ES','all','official_turnout_pct',r[1],'% of resident census (CER), headline','interior_Elecciones-Congreso'])
        w.writerow([r[0],'ES','all','official_turnout_incl_cera_pct',r[4],'% of census incl. CERA abroad','interior_Elecciones-Congreso'])
