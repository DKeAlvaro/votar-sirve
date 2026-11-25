"""c11: Spain SISLE-SNS waiting times -> data/clean/c11_sisle.csv.
Values were transcribed by hand from the national TOTAL rows of the Ministerio de Sanidad semester PDFs in
data/raw/c11/sisle/ (downloaded by scripts/c11_sisle_download.py) and cross-checked by grepping the numbers in
pdftotext output. The PDFs have no machine-readable table, so there is no automatic parser.
Per row: period, file, surgical patients, surgical mean wait (days), consult patients/1000, consult mean wait (days).
None = not unambiguously readable (consultation days of 2007-12, 2009-06, 2010-06, 2011-12 are scrambled by the PDF layout).
Run from repo root: python -I scripts/c11_sisle_clean.py"""
import csv
S='SISLE-SNS %s'
R=[ # period, file, surg_pts, surg_days, cons_per1000, cons_days
('2004-12','listasEspera04',421716,74,None,None),
('2005-12','listasEspera05',385050,83,None,None),
('2006-12','listasDiciembre06CI',362762,70,35.412,54),
('2007-06','listaPublicacion07CI',364901,70,37.668,53),
('2007-12','listaDiciembre08CI',376242,74,39.344,None),
('2008-06','listaJunio08CI',372572,68,37.057,60),
('2008-12','listaDiciembre08CI2',364397,71,37.485,68),
('2009-06','ListaEsperaJunio09CI',374194,63,39.114,None),
('2009-12','ListaEsperaDic09_CISNS',372468,67,40.236,67),
('2010-06','ListaEsperaJunio10_CISNS',381753,61,39.84,None),
('2010-12','ListaEsperaDic10_CISNS',392072,65,33.001,63),
('2011-06','ListaEsperaJun11_CISNS',417407,64,40.36,67),
('2011-12','ListaEsperaDic11_CISNS',459885,73,36.105,None),
('2012-06','LISTAS_PUBLICACION_CI_JUN12_18122012',536911,76,35.942,53),
('2012-12','LISTAS_DE_ESPERA_Diciembre_2012',571395,100,42.167,59),
('2013-06','LISTAS_PUBLICACION_JUN13',583612,101,39.940,54),
('2013-12','LISTAS_PUBLICACION_DIC13',559335,98,39.0,67),
('2014-06','LISTAS_PUBLICACION_JUN14_CISNS',552016,90,38.55,53),
('2014-12','LISTAS_PUBLICACION_DIC14',511923,87,39.43,82),
('2015-06','LISTAS_PUBLICACION_JUN15',522180,81,38.96,62),
('2015-12','LISTAS_PUBLICACION_DIC15',549424,89,43.35,58),
('2016-06','LISTAS_PUBLICACION_JUN2016.1',569097,83,40.91,52),
('2016-12','LISTAS_PUBLICACION_DIC16',614101,115,45.66,72),
('2017-06','Indicadores_Resumen_Junio_2017',604103,104,43.86,58),
('2017-12','Indicadores_Resumen_Diciembre_2017',592175,106,45.87,66),
('2018-06','LLEE_SNS_IndicadoresResumen_Junio2018',584018,93,43.06,57),
('2018-12','LLEE_SNS_IndicadoresResumen_Diciembre2018',668288,129,62.48,96),
('2019-06','LLEE_SNS_IndicadoresResumen_Junio2019',671494,115,61.84,81),
('2019-12','LISTAS_PUBLICACION_dic19',704997,121,63.72,88),
('2020-06','LISTAS_PUBLICACION_jun2020',691508,170,46.45,115),
('2020-12','LISTAS_PUBLICACION_dic_2020',649879,155,53.60,99),
('2021-06','LISTAS_PUBLICACION_JUN21',661162,121,62.00,75),
('2021-12','LISTAS_PUBLICACION_dic21',706740,123,77.23,89),
('2022-06','LISTAS_PUBLICACION_jun2022',742518,113,79.30,79),
('2022-12','LISTAS_PUBLICACION_dic_2022',793521,120,85.43,95),
('2023-06','LISTAS_PUBLICACION_jun2023',819964,112,78.47,87),
('2023-12','LISTAS_PUBLICACION_dic2023',849535,128,81.47,101),
('2024-06','LISTAS_PUBLICACION_jun2024',848340,121,83.79,94),
('2024-12','LISTAS_PUBLICACION_dic2024',846583,126,83.21,105),
('2025-06','LISTAS_PUBLICACION_jun25',832728,119,81.37,96),
('2025-12','LISTAS_PUBLICACION_Dic_2025_rectificado',853740,122,84.42,102),
]
V=[('sisle_surgical_patients_waiting','persons',2),('sisle_surgical_mean_wait_days','days',3),
   ('sisle_consult_patients_per_1000','per 1,000 inhabitants',4),('sisle_consult_mean_wait_days','days',5)]
with open('data/clean/c11_sisle.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','))
    for r in R:
        for v,u,i in V:
            if r[i] is not None: w.writerow([r[0],'ES','',v,r[i],u,'sanidad_sisle_'+r[1]])
print(len(R),'periods')
