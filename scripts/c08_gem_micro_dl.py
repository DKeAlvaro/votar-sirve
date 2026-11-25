"""Download GEM APS individual-level files (public, 3-year lag) via the site's download@file endpoint.
usage: python -I c08_gem_micro_dl.py <file_id> <outname>"""
import requests,re,sys
fid,out=sys.argv[1],sys.argv[2]
s=requests.Session();s.headers['User-Agent']='Mozilla/5.0'
h=s.get('https://www.gemconsortium.org/data/sets?id=aps',timeout=25).text
tok=re.search(r'name="_token" type="hidden" value="([^"]+)"',h).group(1)
r=s.post('https://www.gemconsortium.org/download@file',data={'id':fid,'_token':tok},headers={'X-CSRF-TOKEN':tok},timeout=25,stream=True)
print(r.status_code,r.headers.get('content-type'),r.headers.get('content-disposition'))
with open(out,'wb') as f:
    for c in r.iter_content(1<<16): f.write(c)
