import re,itertools
def parse(f,enc='latin-1'):
    t=open(f,encoding=enc).read()
    i=t.index('DATA=');h=t[:i]
    def lst(key):
        m=re.search(key+r'=(.*?);',h,re.S);return re.findall(r'"([^"]*)"',m.group(1))
    stub=lst('STUB');head=lst('HEADING')
    V={}
    for v in stub+head:
        m=re.search(r'VALUES\("%s"\)=(.*?);'%re.escape(v),h,re.S);V[v]=re.findall(r'"([^"]*)"',m.group(1))
    data=re.search(r'DATA=(.*?);',t[i:],re.S).group(1).split()
    rws=list(itertools.product(*[V[s] for s in stub]));cols=list(itertools.product(*[V[s] for s in head]))
    assert len(data)==len(rws)*len(cols),(len(data),len(rws),len(cols))
    k=0
    for r in rws:
        for c in cols:
            v=data[k];k+=1
            yield dict(zip(stub,r))|dict(zip(head,c)),(None if v.startswith('"') or v in('.','..','-') else float(v))
