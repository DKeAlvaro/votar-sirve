import os,sys,urllib.request
R='data/raw/c11/'
B='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/%s?format=JSON&lang=en%s'
def get(code,q='',name=None):
    p=R+(name or code)+'.json'
    if not os.path.exists(p): urllib.request.urlretrieve(B%(code,q),p)
    return p
if __name__=='__main__':
    for c in sys.argv[1:]: print(get(c))
