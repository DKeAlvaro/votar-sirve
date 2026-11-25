import sys,zipfile,csv,io,openpyxl
zp,out=sys.argv[1],sys.argv[2]
z=zipfile.ZipFile(zp)
n=z.namelist()[0]
wb=openpyxl.load_workbook(io.BytesIO(z.read(n)),read_only=True)
print(wb.sheetnames,flush=True)
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f)
    for i,r in enumerate(wb[wb.sheetnames[0]].iter_rows(values_only=True)):
        w.writerow(r)
        if i%200000==0: print(i,flush=True)
print('done',i)
