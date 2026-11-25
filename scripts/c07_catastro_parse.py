"""Sum dwellings by construction year per municipality from Catastro INSPIRE building GML zips."""
import sys,zipfile,re,glob,csv,os
src,out=sys.argv[1],sys.argv[2]
blk=re.compile(r'<bu-ext2d:Building .*?</bu-ext2d:Building>',re.S)
rows=[]
for p in sorted(glob.glob(src+'/*.zip')):
    code=os.path.basename(p)[:-4]
    try:
        z=zipfile.ZipFile(p); n=[x for x in z.namelist() if x.endswith('.building.gml')][0]
    except Exception as e: print('BAD',p,e); continue
    s=z.read(n).decode('utf-8','replace')
    agg={}
    for b in blk.findall(s):
        y=re.search(r'<bu-core2d:beginning>(\d{4})',b); d=re.search(r'numberOfDwellings>(\d+)',b); u=re.search(r'currentUse>(\w+)',b)
        if not y: continue
        k=int(y.group(1)); a=agg.setdefault(k,[0,0,0])
        a[0]+=1
        if u and u.group(1).startswith('1_'): a[1]+=1; a[2]+=int(d.group(1)) if d else 0
    for k,a in agg.items(): rows.append([code,k,a[0],a[1],a[2]])
with open(out,'w',newline='') as f:
    w=csv.writer(f); w.writerow(['ine5','year','n_buildings','n_residential_bldgs','n_dwellings']); w.writerows(rows)
print('done',len(rows))
