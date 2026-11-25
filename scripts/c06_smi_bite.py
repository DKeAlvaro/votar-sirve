"""c06 SMI bite by province (pre-2019): INE Atlas de Distribucion de Renta + EES by CCAA.
Run: python -I scripts/c06_smi_bite.py   (downloads to data/raw/c06 if missing)"""
import sys,os,csv,json,re,unicodedata,statistics
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import _ine
R='data/raw/c06/';O='data/clean/'
_ine.get('',None) if False else None
def dl(path,raw):
    import requests
    if not os.path.exists(raw):
        r=requests.get(_ine.B+path,timeout=25);r.raise_for_status();open(raw,'w',encoding='utf-8').write(r.text)
    return json.load(open(raw,encoding='utf-8'))
atlas=dl('DATOS_TABLA/53689?date=20150101:20241231&tip=A',R+'ine_atlas_53689.json')
ees=dl('DATOS_TABLA/28191?tip=A&date=20100101:20261231',R+'ine_ees_28191.json')
names={r['name']:r['geo'] for r in csv.DictReader(open(O+'c06_province_names.csv',encoding='utf-8'))}
rows=[]
VAR={'Mediana de la renta por unidad de consumo':'atlas_median_income_per_consumption_unit','Media de la renta por unidad de consumo':'atlas_mean_income_per_consumption_unit','Renta neta media por persona':'atlas_mean_net_income_per_person'}
vals={}
for x in atlas:
    nm,rest=x['Nombre'].split('. ',1)
    if nm=='Total Nacional': geo='ES'
    elif nm in names: geo=names[nm]
    else: continue
    for k,v in VAR.items():
        if k in rest:
            for y in x['Data']:
                if y['Valor'] is not None and 2015<=y['Anyo']<=2018:
                    vals[(geo,v,y['Anyo'])]=y['Valor']
for (g,v,y),val in sorted(vals.items()):
    rows.append([y,g,'',v,val,'EUR_per_year_nominal','ine_adrh_53689'])
# bite index: reference (unweighted median across the provinces with data, per year) / province value, mean over 2015-2018.
# >1 = poorer than the typical province = SMI bites harder. (Atlas has no national value for 2015-2018.)
for v in ['atlas_median_income_per_consumption_unit','atlas_mean_net_income_per_person']:
    gs=sorted({k[0] for k in vals if k[1]==v})
    ref={y:statistics.median(vals[(g,v,y)] for g in gs if (g,v,y) in vals) for y in range(2015,2019)}
    for g in gs:
        ys=[y for y in range(2015,2019) if (g,v,y) in vals]
        if len(ys)==4:
            idx=statistics.mean(ref[y]/vals[(g,v,y)] for y in ys)
            rows.append(['2015-2018',g,'',v.replace('atlas_','bite_index_refmedian_over_prov_'),round(idx,4),'ratio','derived_ine_adrh_53689'])
# EES by CCAA: median / mean annual gross wage, and SMI bite = annual SMI (14 pagas) / median wage
CC={'Andaluc':'ES-AN','Arag':'ES-AR','Asturias':'ES-AS','Balears':'ES-IB','Canarias':'ES-CN','Cantabria':'ES-CB','Castilla y Le':'ES-CL','Castilla - La':'ES-CM','Catalu':'ES-CT','Comunitat Valenciana':'ES-VC','Extremadura':'ES-EX','Galicia':'ES-GA','Madrid':'ES-MD','Murcia':'ES-MC','Navarra':'ES-NC','Pa�s Vasco':'ES-PV','Rioja':'ES-RI','Ceuta':'ES-CE','Melilla':'ES-ML'}
def cc(n):
    if n.startswith('Total Nacional'): return 'ES'
    n=n.replace('�','�')
    if n.startswith('Pa') and 'Vasco' in n: return 'ES-PV'
    for k,v in CC.items():
        if n.startswith(k): return v
    return None
SMI={2015:648.60,2016:655.20,2017:707.70,2018:735.90}
ev={}
for x in ees:
    p=x['Nombre'].split('. ')
    if p[0]!='Ambos sexos': continue
    g=cc(p[1])
    st=p[3].strip() if len(p)>3 else ''
    if g is None or st not in('Mediana','Media','Percentil 10'): continue
    for y in x['Data']:
        if 2015<=y['Anyo']<=2018 and y['Valor'] is not None: ev[(g,st,y['Anyo'])]=y['Valor']
VN={'Mediana':'ees_median_gross_annual_wage','Media':'ees_mean_gross_annual_wage','Percentil 10':'ees_p10_gross_annual_wage'}
for (g,st,y),v in sorted(ev.items()):
    rows.append([y,g,'',VN[st],v,'EUR_per_year_nominal','ine_eaes_28191'])
for (g,st,y),v in sorted(ev.items()):
    if st=='Mediana': rows.append([y,g,'','ees_smi_over_median_wage',round(SMI[y]*14/v,4),'ratio','derived_ine_eaes_28191_boe_smi'])
    if st=='Percentil 10': rows.append([y,g,'','ees_smi_over_p10_wage',round(SMI[y]*14/v,4),'ratio','derived_ine_eaes_28191_boe_smi'])
for g in sorted({k[0] for k in ev}):
    ys=[y for y in range(2015,2019) if (g,'Mediana',y) in ev]
    if len(ys)==4: rows.append(['2015-2018',g,'','ees_smi_over_median_wage_mean',round(statistics.mean(SMI[y]*14/ev[(g,'Mediana',y)] for y in ys),4),'ratio','derived_ine_eaes_28191_boe_smi'])
with open(O+'c06_smi_bite_province.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
print(len(rows),len({r[1] for r in rows}))
