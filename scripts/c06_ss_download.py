"""Download Seguridad Social PXWeb tables (afiliados medios) to data/raw/c06. python -I scripts/c06_ss_download.py [idx]"""
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import _ssweb
T={'01':('01m. Por sexo, edad y regimen.px','ss_01m_sexo_edad_regimen.px'),
 '07':('07m. Afiliados R. GENERAL por tipo de contrato y jornada, tramos de edad y sexo.px','ss_07m_rg_contrato_jornada_edad_sexo.px'),
 '11':('11m. Por provincia, edad y sexo.px','ss_11m_provincia_edad_sexo.px')}
for k in (sys.argv[1:] or T):
    n,o=T[k];_ssweb.download(n,'data/raw/c06/'+o,timeout=120);print('ok',o,os.path.getsize('data/raw/c06/'+o))
