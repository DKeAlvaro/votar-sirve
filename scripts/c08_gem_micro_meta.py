"""Extract each GEM APS individual .sav to a scratch dir and dump column names+labels.
usage: python -I c08_gem_micro_meta.py <scratch_dir>"""
import zipfile,glob,os,sys,pyreadstat,csv
S=sys.argv[1]; os.makedirs(S,exist_ok=True)
out=open(os.path.join(S,'meta.tsv'),'w',encoding='utf8')
for f in sorted(glob.glob('data/raw/c08/gem_micro/gem*_ind.zip')):
    y=f.split('gem')[-1][:4]
    z=zipfile.ZipFile(f)
    n=[i for i in z.namelist() if i.endswith('.sav') and '__MACOSX' not in i][0]
    d=os.path.join(S,y)
    g=lambda: [x for x in glob.glob(d+'/**/*.sav',recursive=True) if os.path.isfile(x)]
    if not g():
        try: z.extract(n,d)
        except NotImplementedError:
            os.makedirs(d,exist_ok=True); import subprocess; subprocess.run(['tar','-xf',f,'-C',d,n],check=True)
    p=g()[0]
    for enc in (None,'latin1'):
        try:
            _,m=pyreadstat.read_sav(p,metadataonly=True,encoding=enc);break
        except Exception as e: print(y,'enc fail',enc,e)
    for c in m.column_names:
        out.write(f"{y}\t{c}\t{(m.column_names_to_labels.get(c) or '').replace(chr(9),' ')[:120]}\n")
    out.flush(); print(y,len(m.column_names),flush=True)
