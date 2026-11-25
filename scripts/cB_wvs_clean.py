"""Clean data/raw/cB/harvest_long.csv -> data/clean/cB_wvs_age.csv
Items are all 1-10 scales. Shares are of valid answers (codes 1-10, DK/NA/missing excluded)."""
import pandas as pd, re, numpy as np
d=pd.read_csv('data/raw/cB/harvest_long.csv')
YEAR={("Netherlands EVS",346):1981,("Spain EVS",346):1981,("Netherlands EVS",345):1990,("Spain EVS",345):1990,
 ("Netherlands EVS",1562):2017,("Spain EVS",1562):2017}
def year(sample,wave):
    if (sample,wave) in YEAR: return YEAR[(sample,wave)]
    return int(re.search(r"\d{4}",sample).group())
def num(x):
    x=str(x).replace('%','').replace(',','').replace('(','').replace(')','')
    return 0.0 if x=='-' else float(x)
out=[]
for (w,sample,var),g in d.groupby(['wave','sample','var']):
    rows=list(dict.fromkeys(g.row))  # ordered unique row labels
    # first 10 rows = codes 1..10 (labels of 1 and 10 are text, 2..9 numeric)
    if sample.startswith('Spain') and w==345 and False: pass
    codes=rows[:10]
    meanrow=[r for r in rows if r=='Mean']; nrow=[r for r in rows if r=='Base mean' or r=='(N)']
    for age,gg in g.groupby('age',sort=False):
        s=gg.set_index('row').cell
        try:
            p=np.array([num(s[r]) for r in codes]); 
            valid=p.sum()
            if valid==0: continue
            lo=p[:3].sum()/valid*100; hi=p[7:].sum()/valid*100
            mean=num(s['Mean']) if 'Mean' in s else np.nan
            n=num(s['(N)']) if '(N)' in s else np.nan
        except KeyError: continue
        grp={'up to 29':'<30','30-49':'30-49','50 and more':'50+','TOTAL':'all'}.get(age,age)
        y=year(sample,w); geo='ES' if sample.startswith('Spain') else 'NL'
        sid=f"wvs_online_{sample.replace(' ','_')}"
        for v,val,u in [('share_1to3',lo,'pct valid'),('share_8to10',hi,'pct valid'),('mean_1to10',mean,'scale 1-10'),('n_total_sample_group',n,'respondents')]:
            out.append((str(y),geo,grp,f"{var}:{v}",round(val,2),u,sid))
o=pd.DataFrame(out,columns='date,geo,group,variable,value,unit,source_id'.split(','))
# EVS and WVS Spain 1990 are the same fieldwork year: keep WVS sample, drop EVS duplicate for ES 1990
o=o[~((o.geo=='ES')&(o.date=='1990')&(o.source_id=='wvs_online_Spain_EVS'))]
m=(o.date=='1990')&o.variable.str.startswith('E040')
o.loc[m,'source_id']=o.loc[m,'source_id']+';wording_break_1990'
o.to_csv('data/clean/cB_wvs_age.csv',index=False)
print(o[o.variable.str.endswith('mean_1to10')].pivot_table(index=['variable','geo','date'],columns='group',values='value').round(2).to_string())
