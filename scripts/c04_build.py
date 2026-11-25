"""Build c04_completions.csv and c04_households.csv from raw files in data/raw/c04 (+ EPA microdata households from c01_epa.csv).
Usage: python -I scripts/c04_build.py   (run from repo root; run c01_epa_compute.py first)
"""
import pandas as pd,json
R='data/raw/c04/';C='data/clean/'
def natl(f):
    d=pd.read_excel(R+f+'.xls',header=None)
    lc=[c for c in d.columns if (d[c].astype(str).str.strip()=='TOTAL NACIONAL').any()][0]
    ri=d.index[d[lc].astype(str).str.strip()=='TOTAL NACIONAL'][0]
    out={}
    for c in d.columns[lc+1:]:
        h=pd.to_numeric(d.loc[ri-1,c],errors='coerce');v=pd.to_numeric(d.loc[ri,c],errors='coerce')
        if pd.notna(h) and pd.notna(v): out[int(h)]=float(v)
    return out
libres=natl('32201000');prot=natl('31306000')
rows=[]
for y in sorted(libres):
    for var,s,sid,note in [('homes_completed_libres',libres,'mivau_3.2_libres_terminadas','Ministry note: estimated figures'),
                           ('homes_completed_protegidas',prot,'mivau_1.6_protegidas_calif_definitivas','definitive qualifications (table titled "viviendas protegidas terminadas" before 2010); 2003-2005 estimated')]:
        rows.append(dict(date=str(y),geo='ES',group='',variable=var,value=s[y],unit='homes',source_id=sid,note=note))
    rows.append(dict(date=str(y),geo='ES',group='',variable='homes_completed_total',value=libres[y]+prot[y],unit='homes',source_id='mivau_3.2+1.6',note='libres + protegidas'))
pd.DataFrame(rows).to_csv(C+'c04_completions.csv',index=False)
epa=json.load(open(R+'epa_65269.json',encoding='utf8'))[0]['Data']
q={(x['Anyo'],x['T3_Periodo']):x['Valor']*1000 for x in epa}
mic=pd.read_csv(C+'c01_epa.csv');mic=mic[mic.variable=='households_epa_microdata']
mic={int(r.date[:4]):r.value for r in mic.itertuples()}
stock={}
for y in range(1999,2027):
    if (y,'T2') in q: stock[y]=(q[(y,'T2')],'ine_epa_hogares_65269','EPA published table 65269 (Hogares), Q2')
    elif y in mic: stock[y]=(mic[y],'ine_epa_microdata_q2','own weighted count of reference persons (RELPP1=1) in EPA Q2 microdata; published table starts 2002')
rows=[];prev=None
for y in sorted(stock):
    v,sid,note=stock[y]
    rows.append(dict(date=str(y),geo='ES',group='',variable='households_stock',value=round(v),unit='households',source_id=sid,note=note))
    if prev==y-1:
        n=[]
        if stock[prev][1]!=sid: n.append('SOURCE SWITCH '+stock[prev][1]+' -> '+sid+'; not strictly comparable')
        if y==2005: n.append('EPA 2005 questionnaire reform')
        if y==2021: n.append('EPA 2021 new base (Census 2021 population, new questionnaire)')
        rows.append(dict(date=str(y),geo='ES',group='',variable='households_change_yoy',value=round(v-stock[prev][0]),unit='households',source_id=sid,note='; '.join(n)))
    prev=y
ech=pd.read_csv(R+'ech_01001.csv',sep=';',dtype=str)
e=ech[(ech.iloc[:,0]=='Total (tipo de hogar)')&(ech.iloc[:,1]=='Total')]
for r in e.itertuples(index=False):
    rows.append(dict(date=r[2],geo='ES',group='',variable='households_ech_check',value=round(float(r[3].replace('.','').replace(',','.'))*1000),unit='households',source_id='ine_ech_01001',note='Encuesta Continua de Hogares 2014-2020, cross-check only'))
ecp=json.load(open(R+'ine_60131.json',encoding='utf8'))[0]['Data']
for x in ecp:
    if x['Fecha'][5:10]=='01-01': rows.append(dict(date=x['Fecha'][:4],geo='ES',group='',variable='households_ecp_check',value=round(x['Valor']),unit='households',source_id='ine_ecp_ECP355533',note='INE ECP355533 households in family dwellings, 1 Jan, '+x['T3_TipoDato']+'; cross-check only'))
ev={int(r['date']):r['value'] for r in rows if r['variable']=='households_ecp_check'}
for y in sorted(ev):
    if y-1 in ev: rows.append(dict(date=str(y),geo='ES',group='',variable='households_change_yoy_ecp',value=ev[y]-ev[y-1],unit='households',source_id='ine_ecp_ECP355533',note='change in 1 Jan stock; clean series across the 2021 EPA break'))
o=pd.DataFrame(rows);o.to_csv(C+'c04_households.csv',index=False)
print(o[o.variable.isin(['households_stock','households_change_yoy'])].pivot(index='date',columns='variable',values='value').T.to_string())
print(o[o.variable.str.contains('check')][['date','variable','value']].to_string())
