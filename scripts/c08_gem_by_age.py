"""GEM APS individual files -> attitude indicators by age for ES, NL (ages 18-64; GEM APS covers 18-64).
usage: python -I c08_gem_by_age.py <scratch_dir> <year> [<year>...]  -> data/interim/c08_gem_age_<year>.csv
Weighted % yes among valid yes/no answers: fearfail, nbgoodc, nbstatus, futsupno (futsup in 2001).
Disk is tight: each extracted .sav is deleted after use."""
import zipfile,glob,os,sys,subprocess,shutil,pyreadstat,pandas as pd
S=sys.argv[1]
CAND=['country','age','weight','weight_a','weight_l','fearfail','nbgoodc','nbstatus','futsupno','futsup']
for y in sys.argv[2:]:
    f=f'data/raw/c08/gem_micro/gem{y}_ind.zip'; d=os.path.join(S,y); os.makedirs(d,exist_ok=True)
    g=lambda:[x for x in glob.glob(d+'/**/*.sav',recursive=True) if os.path.isfile(x)]
    if not g():
        try:
            z=zipfile.ZipFile(f); n=[i for i in z.namelist() if i.endswith('.sav') and '__MACOSX' not in i][0]; z.extract(n,d)
        except NotImplementedError:  # deflate64 (2012/2013 zips): stream-inflate with the inflate64 package
            import inflate64,struct
            z=zipfile.ZipFile(f); zi=[i for i in z.infolist() if i.filename.endswith('.sav')][0]
            with open(f,'rb') as fh:
                fh.seek(zi.header_offset); h=fh.read(30); nl,el=struct.unpack('<HH',h[26:30]); fh.seek(nl+el,1)
                inf=inflate64.Inflater(); left=zi.compress_size
                with open(os.path.join(d,'gem.sav'),'wb') as out:
                    while left>0:
                        b=fh.read(min(1<<20,left)); left-=len(b); out.write(inf.inflate(b))
    p=g()[0]
    for enc in (None,'latin1'):
        try: _,m=pyreadstat.read_sav(p,metadataonly=True,encoding=enc);break
        except Exception: pass
    low={c.lower():c for c in m.column_names}
    cols=[low[c] for c in CAND if c in low]
    df,_=pyreadstat.read_sav(p,usecols=cols,encoding=enc,apply_value_formats=True)
    shutil.rmtree(d,ignore_errors=True)
    df.columns=[c.lower() for c in df.columns]
    df['geo']=df.country.astype(str).str.strip().str.lower().map({'spain':'ES','es':'ES','netherlands':'NL','nl':'NL','the netherlands':'NL'})
    df=df[df.geo.notna()].copy()
    df['age']=pd.to_numeric(df.age,errors='coerce')
    df=df[(df.age>=18)&(df.age<=64)]
    wcol='weight_a' if 'weight_a' in df else 'weight'
    df['w']=pd.to_numeric(df[wcol],errors='coerce').fillna(1) if wcol in df else 1.0
    rows=[]
    for v in ['fearfail','nbgoodc','nbstatus','futsupno','futsup']:
        if v not in df or (v=='futsup' and 'futsupno' in df): continue
        s=df[v].astype(str).str.strip().str.lower()
        df['_y']=s.isin(['yes','1','1.0']); df['_v']=df._y|s.isin(['no','2','2.0'])
        for geo,gd in df.groupby('geo'):
            for grp,mask in [('18-34',gd.age<=34),('35-64',gd.age>=35),('18-24',gd.age<=24),('25-34',(gd.age>=25)&(gd.age<=34)),('18-64',gd.age>=18)]:
                x=gd[mask&gd._v]
                if len(x)==0: continue
                rows.append([y,geo,grp,('entrepreneurial_intentions' if v.startswith('futsup') else v)+'_pct_yes',round(100*(x.w*x._y).sum()/x.w.sum(),2),'percent of valid answers, weighted',f'gem_aps_micro_{y}',len(x),wcol])
    pd.DataFrame(rows,columns=['date','geo','group','variable','value','unit','source_id','n_valid','weight_var']).to_csv(f'data/interim/c08_gem_age_{y}.csv',index=False)
    print(y,len(df),cols,len(rows),{v:df[v].astype(str).value_counts().head(5).to_dict() for v in ('fearfail','futsupno','futsup') if v in df},flush=True)
