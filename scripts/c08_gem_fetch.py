"""Fetch GEM APS key indicators (national level) from gemconsortium.org/data/key-aps (the site's own JSON endpoint).
Raw responses saved to data/raw/c08/gem_<indicator>.json. Rerunnable."""
import requests, re, json, os, sys
R='data/raw/c08/'
ECO={'ES':'spain','NL':'netherlands','DE':'germany','FR':'france','IT':'italy','PT':'portugal','UK':'united-kingdom','US':'united-states'}
IND=['perceived_opportunities_rate','perceived_capabilities_rate','fear_of_failure_rate','entrepreneurial_intentions_rate',
 'total_early_stage_entrepreneurial_activity_tea_rate','established_business_ownership_rate',
 'high_status_to_successful_entrepreneurs_rate','entrepreneurship_as_a_good_career_choice_rate']
s=requests.Session(); s.headers['User-Agent']='Mozilla/5.0'
h=s.get('https://www.gemconsortium.org/data/key-aps',timeout=25).text
tok=re.search(r'name="_token" type="hidden" value="([^"]+)"',h).group(1)
ids={}
for k,slug in ECO.items():
    m=re.search(r'value="(\d+)" name="economy\[\]" id="e_%s"'%slug,h); ids[k]=m.group(1)
print(ids)
years=list(range(2001,2026))
for ind in IND:
    fn=R+'gem_%s.json'%ind
    if os.path.exists(fn): continue
    data=[('_token',tok),('url','https://www.gemconsortium.org')]+[('economy[]',v) for v in ids.values()]+[('indicator[]',ind)]+[('year[]',y) for y in years]
    r=s.post('https://www.gemconsortium.org/data/key-aps/data',data=data,timeout=25,headers={'X-CSRF-TOKEN':tok,'X-Requested-With':'XMLHttpRequest'})
    print(ind,r.status_code,len(r.text))
    open(fn,'w',encoding='utf8').write(r.text)
