"""c07 pilot, province 47 (Valladolid). Usage: python -I scripts/c07_pilot.py [prov]
Inputs : data/raw/c07/dat/{03,05,06}04YYMM.DAT (Interior municipal DAT files, 2015 and 2019)
         data/raw/c07/cat<prov>/*.zip (Catastro INSPIRE buildings)  -> parsed with c07_catastro_parse.py
Outputs: data/clean/c07_pilot.csv (tidy long), data/clean/c07_pilot_wide.csv, data/clean/c07_cat<prov>_by_year.csv
"""
import sys, os, re, subprocess
import pandas as pd
prov = sys.argv[1] if len(sys.argv) > 1 else '47'
R = 'data/raw/c07'; C = 'data/clean'
PROVNAME = {'47': 'VALLADOLID'}  # add provinces as needed (OVC province names)
# national candidacy code (last 6 chars of each 03 record) changes between elections; derive from siglas

cat_csv = f'{C}/c07_cat{prov}_by_year.csv'
if not os.path.exists(cat_csv):
    subprocess.run([sys.executable, '-I', 'scripts/c07_catastro_parse.py', f'{R}/cat{prov}', cat_csv], check=True)
cat = pd.read_csv(cat_csv)

# Catastro municipal code (cmc) != INE code. Official crosswalk: OVC ConsultaMunicipio (one call per province)
xw_xml = f'{R}/ovc_{prov}_municipios.xml'
if not os.path.exists(xw_xml):
    import requests
    from urllib.parse import quote
    open(xw_xml, 'wb').write(requests.get('https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaMunicipio?Provincia=%s&Municipio=' % quote(PROVNAME[prov]), timeout=25).content)
cat2ine = {}
for m in re.findall(r'<muni>.*?</muni>', open(xw_xml, encoding='utf8').read(), re.S):
    g = lambda t: re.search(rf'<{t}>(\d+)</{t}>', m).group(1)
    cat2ine[int(g('cd')) * 1000 + int(g('cmc'))] = int(g('cp')) * 1000 + int(g('cm'))
cat['ine5'] = cat.ine5.map(cat2ine)
assert cat.ine5.notna().all(), 'unmapped catastro codes'
cat = cat.groupby(['ine5', 'year'], as_index=False).sum()

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)

rows = []
for yr, ym in [(2015, '1505'), (2019, '1905')]:
    d = f'{R}/dat'
    code2nat = {}; cnt = {'PP': {}, 'PSOE': {}}
    for l in open(f'{d}/0304{ym}.DAT', encoding='latin1'):
        nat = l.rstrip('\r\n')[-6:]; code2nat[l[8:14]] = nat
        sg = l[14:64].strip()
        if sg in cnt: cnt[sg][nat] = cnt[sg].get(nat, 0) + 1
    PP = max(cnt['PP'], key=cnt['PP'].get); PSOE = max(cnt['PSOE'], key=cnt['PSOE'].get)
    print(yr, 'PP code', PP, 'PSOE code', PSOE)
    # 05: municipality basics (only municipalities > 250 inhabitants; <=250 are in files 11/12)
    muni = {}
    for l in open(f'{d}/0504{ym}.DAT', encoding='latin1'):
        if l[11:13] != prov: continue
        muni[l[11:16]] = (l[18:118].strip(), int(l[128:136]))
    votes = {}
    for l in open(f'{d}/0604{ym}.DAT', encoding='latin1'):
        k = l[9:14]
        if k[:2] != prov: continue
        nat = code2nat.get(l[16:22], l[16:22])
        e = votes.setdefault(k, {}).setdefault(nat, [0, 0]); e[0] += int(l[22:30]); e[1] += int(l[30:33])
    for k, (name, pop) in muni.items():
        v = votes.get(k, {})
        tv = sum(a for a, b in v.values()); ts = sum(b for a, b in v.values())
        ppv, pps = v.get(PP, [0, 0]); psv, pss = v.get(PSOE, [0, 0])
        riv = {n: x for n, x in v.items() if n != PP}
        rn = max(riv, key=lambda n: riv[n][0]) if riv else ''
        rv, rs = riv[rn] if riv else (0, 0)
        # homes built in the 4 calendar years after the election year
        c = cat[cat.ine5 == int(k)]
        w = c[(c.year >= yr + 1) & (c.year <= yr + 4)]
        w0 = c[(c.year >= yr) & (c.year <= yr + 3)]
        rows.append(dict(ine5=k, name=name, year=yr, population=pop, votes_to_lists=tv, seats=ts, n_lists=len(v),
            pp_ran=int(PP in v), pp_votes=ppv, pp_seats=pps, pp_share=100*ppv/tv if tv else None,
            psoe_share=100*psv/tv if tv else None, top_rival_code=rn, top_rival_is_psoe=int(rn == PSOE),
            top_rival_share=100*rv/tv if tv else None,
            pp_margin_pts=100*(ppv-rv)/tv if tv else None,
            pp_seat_margin=(pps-rs), pp_first=int(ppv > rv), pp_abs_majority=int(pps > ts/2),
            dwellings_y1_4=int(w.n_dwellings.sum()), buildings_y1_4=int(w.n_buildings.sum()),
            resid_bldgs_y1_4=int(w.n_residential_bldgs.sum()), dwellings_y0_3=int(w0.n_dwellings.sum()),
            dwellings_per1000=1000*w.n_dwellings.sum()/pop if pop else None))
df = pd.DataFrame(rows).sort_values(['year', 'ine5'])
print('municipalities without Catastro data:', [r.ine5 for r in df.itertuples() if r.dwellings_y1_4 == 0 and r.buildings_y1_4 == 0][:20])
df.to_csv(f'{C}/c07_pilot_wide.csv', index=False, float_format='%.4f')
unit = dict(population='persons', votes_to_lists='votes', seats='seats', pp_share='% of votes to lists', psoe_share='% of votes to lists',
    top_rival_share='% of votes to lists', pp_margin_pts='pp (PP share minus strongest non-PP list share)',
    pp_seat_margin='seats (PP minus strongest non-PP list)', pp_first='0/1', pp_abs_majority='0/1 (PP seats > half)', pp_ran='0/1',
    dwellings_y1_4='dwellings', buildings_y1_4='buildings', resid_bldgs_y1_4='buildings', dwellings_y0_3='dwellings',
    dwellings_per1000='dwellings per 1,000 inhabitants', pp_votes='votes', pp_seats='seats', n_lists='lists', top_rival_is_psoe='0/1')
src = {'population': 'interior_05', 'dwellings_y1_4': 'catastro_inspire', 'buildings_y1_4': 'catastro_inspire',
       'resid_bldgs_y1_4': 'catastro_inspire', 'dwellings_y0_3': 'catastro_inspire', 'dwellings_per1000': 'catastro_inspire+interior_05'}
long = []
for r in df.to_dict('records'):
    for var, u in unit.items():
        if r[var] is None or r[var] != r[var]: continue
        long.append([r['year'], 'ES-' + r['ine5'], '', var, round(float(r[var]), 4), u, src.get(var, 'interior_06')])
pd.DataFrame(long, columns=['date', 'geo', 'group', 'variable', 'value', 'unit', 'source_id']).to_csv(f'{C}/c07_pilot.csv', index=False)
print(len(df), 'rows;', len(long), 'long rows')
