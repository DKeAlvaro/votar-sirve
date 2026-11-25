// Text of every card. verdict: ok | ko | mid | na. Keep "take" to one or two sentences.
const TLDR = `<p><b>El problema es real.</b> La mitad de los españoles de 25 a 34 años vive con sus padres (en Holanda, el 11%), y un piso de 80 m² cuesta 6 años de sueldo joven, frente a 4 en 1995.</p>
<p><b>La etiqueta del partido explica poco.</b> Ningún indicador mejora de forma sistemática con un partido frente a su control. La emancipación y la vivienda siguen al ciclo económico, y el déficit de construcción lo comparten todos los gobiernos.</p>
<p><b>Las leyes concretas sí mueven cosas, aunque a veces solo el papel.</b> La reforma laboral cambió el nombre de los contratos más que la estabilidad real. La subida del SMI de 2019 no dejó rastro de destrucción de empleo joven. Tras la reforma de cuotas de 2023 crecieron los autónomos jóvenes.</p>
<p><b>Menos cultura y más reglas.</b> Emprender está peor visto en España, pero esa opinión se hundió con la crisis (en 2005 era mejor que en Alemania), y los jóvenes españoles creen en el esfuerzo tanto como los holandeses. Lo que separa de verdad a los dos países son reglas: ganando 0 €, un autónomo paga 2.471 € al año en España y 350 € en Holanda, y el 21% del coste de un sueldo va a pagar las pensiones actuales (en Holanda, el 3%). Querer ser funcionario es una apuesta racional: la plaza paga un 30-45% más.</p>
<p><b>Y los jóvenes pesan cada vez menos en las urnas:</b> el 14% de los votos, frente al 25% de los mayores de 65, sobre todo por demografía.</p>
<p><b>Veredicto:</b> votar PP o PSOE, por la etiqueta, cambia poco de lo que mide este estudio. Pero las reglas que más pesan sobre un joven (cuotas, pensiones, vivienda, contratos) se deciden por ley y se pueden cambiar. Lo que importa es qué medidas concretas apoya cada voto, más que el color del partido.</p>`;

const SECTIONS = [
  {
    id: "indep", title: "1. ¿Es más difícil independizarse?",
    intro: "Antes de discutir si votar cambia algo, comprobar si el problema existe y desde cuándo.",
    cards: [
      {
        id: "c01", verdict: "ko", q: "¿A qué edad nos vamos de casa?",
        take: "El 46% de los españoles de 25 a 34 años vive con sus padres; en Holanda, el 11%. Pero no es una subida continua: entre 1999 y 2010 bajó del 45% al 34%, y desde 2010 ha vuelto a subir.",
        pred: "sube de forma casi continua en España desde los 80, gobierne quien gobierne; en Holanda, bajo y plano.",
        refute: "la subida se concentra en un shock (p. ej. después de 2008) o se invierte en algún periodo.",
        body: `<p>La predicción decía que el problema crece sin parar desde los 80. Los datos dicen otra cosa: la emancipación <b>mejoró</b> durante el boom (con Aznar y con Zapatero) y empeoró desde 2010 (con Zapatero, Rajoy y Sánchez). La edad media de salida de casa cuenta lo mismo: 29,4 años en 2000, 28,3 en 2009 y 30,2-30,5 desde 2022.</p>
        <p>Lo que sí encaja con la tesis: los giros coinciden con el ciclo económico (crédito fácil y empleo en la construcción hasta 2008, crisis y vivienda cara después), no con los cambios de partido. Y la distancia con Holanda, de 35-40 puntos, existe en todo el periodo.</p>
        <p>Dos cautelas: la EPA cambió de cuestionario en 2005 y de base en 2021 (el salto de 2021 es en parte metodológico), y la EPA y la EU-SILC no miden exactamente lo mismo (la EU-SILC da 1-4 puntos más). Por eso España solo se compara con Holanda usando la misma fuente.</p>`,
        src: "Fuentes: INE, microdatos de la EPA (2.º trimestre, 1999-2025, \"vive con algún progenitor\"); Eurostat <code>ilc_lvps08</code> y <code>yth_demo_030</code> (EU-SILC). Faltan los censos de 1981 y 1991 (requieren registro en IPUMS International).",
      },
      {
        id: "c02", verdict: "ok", q: "¿Cuántos años de sueldo cuesta un piso?",
        take: "Un piso de 80 m² cuesta hoy 6,1 años del sueldo bruto medio de un joven de 25-34 años. En 1995 costaba 4,1. Lo peor fue 2006-2008, con casi 9 años.",
        pred: "claramente más años de sueldo joven ahora que a finales de los 80 y en los 90, tanto para comprar como para alquilar.",
        refute: "igual o menos que entonces.",
        body: `<p>Comprar: la predicción se cumple. Con el precio de tasación del Ministerio y el sueldo medio de 25-34 años del INE, se pasa de 4,1 años de sueldo (1995) a 6,1 (2024). La serie del Banco de España, que compara el precio con la renta de un hogar entero, cuenta lo mismo desde más atrás: 3,1 años en 1987, 3,7 en 1995, 9,4 en el pico de 2007, 6,7 en 2013 y 8,2 hoy. El esfuerzo actual es menor que en la burbuja, pero mucho mayor que en los 80 y 90, y vuelve a subir desde 2013 con gobiernos de los dos partidos.</p>
        <p>Alquilar: no se puede comparar con los 90, porque no hay series públicas de alquiler de contratos nuevos tan antiguas. Desde 2006, el alquiler nuevo medio en Cataluña se lleva entre el 35% y el 45% del sueldo bruto de un joven (40% en 2024). El alquiler mediano de los contratos en vigor en España, calculado para 70 m², ronda el 29-31%. Lo que más pesa en la tendencia es el ciclo: baja hasta 2014 y sube después.</p>
        <p>Cautelas: el sueldo del INE es la media bruta (incluye tiempo parcial) y su encuesta cambió en 2008; para 1995-2006 se usa la media de los tramos 25-29 y 30-34. La tasación va algo por detrás del precio real.</p>`,
        src: "Fuentes: Ministerio de Vivienda y Agenda Urbana, valor tasado de la vivienda libre (€/m², 1995-2025); Banco de España, precio de la vivienda / renta bruta disponible por hogar (1987-2026); INE, Encuesta de Estructura Salarial (1995, 2002, 2006) y Encuesta Anual de Estructura Salarial (2008-2024); INCASOL (Generalitat), fianzas de contratos nuevos; Ministerio, Sistema Estatal de Referencia del Precio del Alquiler (2011-2024).",
      },
      {
        id: "c03", verdict: "ko", q: "Los precios de un joven que alquila frente a su sueldo",
        take: "Entre 2008 y 2024, lo que compra un joven que alquila subió un 31% y su sueldo medio, otro 31%. En el conjunto del periodo han ido empatados; por el camino, no.",
        pred: "la línea de precios acaba por encima de la de salarios.",
        refute: "los salarios jóvenes aguantan o ganan.",
        body: `<p>Es la cesta de un hogar joven (menos de 35 años) que vive de alquiler, con el peso real que tiene cada cosa en su gasto según la Encuesta de Presupuestos Familiares: el alquiler pasó del 20% al 25% de todo lo que gastan. Al alquiler se le pone el precio de los contratos nuevos (Cataluña, la única serie larga de contratos nuevos) y al resto, el IPC de cada grupo.</p>
        <p>Resultado en 2024: precios 131,1 y sueldo 130,7 (2008 = 100). Diferencia de 0,4 puntos, dentro del ruido, así que los salarios aguantaron y la predicción falla. Pero el punto de partida importa: 2008 fue el pico de los alquileres. Entre 2008 y 2013 el sueldo joven cayó un 6% mientras los precios subían; desde 2013, los precios subieron un 29% y el sueldo un 40%.</p>
        <p>Cautelas: el sueldo es una media bruta y puede subir solo porque cambie quién trabaja (más formados, menos tiempo parcial); el alquiler de Cataluña no es el de toda España; y la cesta no incluye la compra de vivienda, que es donde más se ha deteriorado la situación (gráfico 2).</p>`,
        src: "Fuentes: INE, Encuesta de Presupuestos Familiares, microdatos 2008, 2013, 2019 y 2025 (hogares con persona de referencia menor de 35 que alquilan); INE, IPC por grupos ECOICOP (2002-2025); INCASOL, alquiler medio de contratos nuevos en Cataluña; INE, Encuesta Anual de Estructura Salarial (25-34). Cálculo: <code>scripts/build_c02_c03.py</code>.",
      },
      {
        id: "c04", verdict: "ok", q: "¿Se construyen las viviendas que hacen falta?",
        take: "Desde 2013 España termina entre 45.000 y 100.000 viviendas al año, gobierne quien gobierne. Entre 2022 y 2025 se formaron de 2 a 3 hogares por cada vivienda terminada.",
        pred: "desde ~2012 se terminan menos viviendas que hogares nuevos, con todos los gobiernos.",
        refute: "algún gobierno cerró el hueco.",
        body: `<p>Entre 2012 y 2025 se terminaron 1,09 millones de viviendas y se formaron al menos 1,9 millones de hogares (falta 2021 por un cambio de método). El hueco solo se cerró en 2015 y 2018, y no porque se construyera más, sino porque con la crisis se formaban muy pocos hogares. Ningún gobierno lo cerró en el conjunto de su mandato.</p>
        <p>La vivienda protegida pasó de 68.000 en 2008 a unas 5.000 en 2017-2018 y sigue por debajo de 15.000. Eso sí es política, y la han dejado caer tanto el PP como el PSOE. En los últimos años del boom pasaba lo contrario: se terminaban 150.000-200.000 viviendas más que hogares nuevos.</p>
        <p>Encaja con la tesis: el déficit lo comparten todos los gobiernos centrales. Con un matiz importante: el suelo y las licencias son municipales y autonómicas, así que mirar solo PP o PSOE en el Gobierno central es mirar en el sitio equivocado. Para eso está el gráfico 7.</p>`,
        src: "Fuentes: Ministerio de Vivienda y Agenda Urbana, viviendas libres terminadas (certificados de fin de obra) y calificaciones definitivas de vivienda protegida, 1991-2025; INE, hogares (EPA 1999-2020; Estadística Continua de Población 2021-2026).",
      },
    ],
  },
  {
    id: "gob", title: "2. ¿Cambia algo quién gobierna?",
    intro: "El núcleo de la tesis. Si el partido importara, las curvas cambiarían de rumbo al cambiar el color del fondo, y no en los países de control.",
    cards: [
      {
        id: "c05", verdict: "ok", q: "El panel de los gobiernos",
        take: "Ninguna métrica muestra un patrón claro por partido frente a su control: como mucho 2 de 5, y con muy pocos datos. El paro juvenil español es casi siempre el doble del europeo, gobierne quien gobierne.",
        pred: "ningún patrón consistente por partido más allá del control (Portugal/UE), con 0, 2 o 4 años de retraso.",
        refute: "al menos 3 de las 6 métricas cambian de pendiente al cambiar el gobierno, con signo consistente por partido.",
        body: `<p>Para cada métrica se mide España menos un control (Portugal, Holanda o el resto de edades) y se calcula cuánto mejora esa diferencia por año dentro de cada gobierno. "Patrón" significa que todos los gobiernos de un partido lo hicieron mejor que todos los del otro. Se repite suponiendo que las políticas tardan 0, 2 o 4 años en notarse.</p>
        <p>Resultado: paro juvenil, sin patrón; jóvenes con menos de un año en su empleo, sin patrón (salvo con 4 años de retraso); sueldo joven frente al resto de edades, sin patrón. Dos métricas salen "PSOE mejor" sin retraso: emancipación frente a Holanda y años de sueldo por piso. Pero esas dos series empiezan en 2005-2008, así que comparan dos periodos del PSOE con uno solo del PP (Rajoy). Por puro azar, uno de tres periodos queda el último una de cada tres veces. Y la de años por piso no tiene control internacional: refleja sobre todo el ciclo.</p>
        <p>Como se predijo, no hay patrón por partido. Pero es un test débil: con solo 3-4 gobiernos con datos y controles, hasta un efecto real costaría verlo. Faltan dos métricas del plan: la cuota mínima de autónomo, porque no hay serie completa desde 1980, y la estabilidad laboral para 25-34 años, porque Eurostat solo publica 15-24.</p>`,
        src: "Fuentes: INE EPA (paro desde 1976); Eurostat <code>lfsa_urgan</code> (paro 15-24, España y Portugal desde 1995), <code>lfsa_egad</code> (antigüedad en el empleo), <code>ilc_lvps08</code> (emancipación); INE, Encuesta Anual de Estructura Salarial; Ministerio de Vivienda, valor tasado. Cálculo: <code>scripts/build_site.py</code> (función <code>c05_panel</code>).",
      },
      {
        id: "c06", verdict: "mid", q: "Antes y después de cada ley",
        take: "De tres leyes, dos no movieron nada medible frente a su grupo de control: la subida del SMI de 2019 y la reforma laboral de 2022. La tercera, las cuotas de autónomos de 2023, sí coincide con más autónomos jóvenes, aunque esa tendencia ya venía de antes.",
        pred: "las líneas de afectados y de control siguen paralelas tras el mes 0.",
        refute: "la brecha media posterior sale del rango que tuvo en los 36 meses previos.",
        body: `<p><b>SMI 2019 (+22%).</b> Si subir el mínimo hubiera destruido empleo joven, se vería sobre todo donde los sueldos son más bajos. Se comparan las provincias donde el SMI pesa más (Almería, Badajoz, Huelva...) con las que menos (Bizkaia, Madrid, Barcelona...), midiendo qué parte de los afiliados tiene 16-24 años. La brecha tras la ley se queda dentro de su rango previo, también antes del covid. No hay rastro de destrucción de empleo joven, aunque la medida de "cuánto pesa" usa la renta de los hogares y no los salarios, así que es aproximada.</p>
        <p><b>Reforma laboral 2022.</b> La etiqueta cambió muchísimo: los menores de 30 con contrato indefinido pasaron del 48% al 74% en un año. Pero la estabilidad real (qué parte de los jóvenes ocupados lleva menos de 3 meses en su empleo) bajó lo mismo en España que en Portugal, que no hizo reforma. Es el efecto "fijo discontinuo": cambia el nombre del contrato más que la vida laboral. Ojo: el periodo previo incluye el covid, que hace el rango muy ancho y el test, poco exigente.</p>
        <p><b>Cuotas de autónomos 2023.</b> Los autónomos menores de 30 crecieron un 14% en los tres años siguientes, mientras los de 30-44 bajaron un 3%. Según la regla, la brecha se movió. Pero los jóvenes ya crecían más que el grupo de control antes de la ley (unos 4 puntos al año antes y unos 5 después), así que como mucho es un efecto pequeño.</p>
        <p>Conclusión: las leyes sí cambian cosas, pero a veces cambian más el papel que la realidad. Y dos de las tres pruebas tienen periodos de control contaminados por el covid.</p>`,
        src: "Fuentes: Seguridad Social, afiliados medios por provincia, edad, régimen y tipo de contrato (mensual, 2012-2026); INE, Atlas de Distribución de Renta de los Hogares 2015-2018 (medida de cuánto pesa el SMI por provincia); Eurostat, antigüedad en el empleo trimestral (<code>lfsq_egdn2</code> y relacionadas). Cálculo: <code>scripts/build_c06.py</code>.",
      },
      {
        id: "c07", verdict: "na", q: "Pueblo contra pueblo: elecciones municipales por los pelos",
        take: "Hecho solo el piloto (provincia de Valladolid, municipales de 2015 y 2019). Con unos 50 pueblos decididos por menos de 10 puntos no se puede concluir nada; la versión para toda España es viable y queda pendiente.",
        pred: "sin salto en el 0.",
        refute: "el salto en el 0 tiene un intervalo de confianza del 95% que excluye el cero.",
        body: `<p>La idea: los pueblos donde el PP ganó por un punto y los que perdió por un punto se parecen en todo menos en quién gobierna. Si en los primeros se construye distinto que en los segundos, el partido importa. Cada punto del gráfico es un municipio: a la derecha de la línea ganó el PP; a la izquierda, ganó otro.</p>
        <p>En el piloto, la mediana de viviendas construidas por 1.000 habitantes en los cuatro años siguientes fue algo mayor donde el PP ganó por poco (3,5 frente a 1,0 en 2015; 5,8 frente a 4,1 en 2019), pero con 9-14 pueblos por grupo eso es ruido. No se estima ningún salto con estos datos.</p>
        <p>Para toda España hacen falta unos 6-7 GB de datos del Catastro y los resultados de cada municipio desde 1979; daría 1.000-1.500 municipios decididos por menos de 10 puntos en cada elección, suficiente para un test serio. Quedan fuera País Vasco y Navarra (catastro propio) y los municipios de menos de 250 habitantes (no votan listas de partido).</p>`,
        src: "Fuentes: resultados oficiales de las elecciones municipales por municipio (ficheros del Ministerio del Interior, descargados de una copia en GitHub porque el portal bloquea las descargas automáticas; contrastados con resultados conocidos); Catastro, edificios INSPIRE (año de construcción y número de viviendas); cruce de códigos Catastro-INE.",
      },
    ],
  },
  {
    id: "cult", title: "3. ¿Cultura o costes?",
    intro: "La tesis dice que en España falta ambición y que emprender está mal visto. Se puede medir la actitud y el coste por separado.",
    cards: [
      {
        id: "c08", verdict: "ok", q: "¿Está mal visto emprender?",
        take: "En España, entre el 44% y el 51% ve emprender como buena opción profesional (2023-2025); en Holanda, el 79-86% (último dato, 2019). España queda última entre los países comparados.",
        pred: "España claramente peor que Holanda (más de 5 puntos) en actitudes.",
        refute: "diferencia de 5 puntos o menos: la brecha estaría en los costes, no en la mentalidad.",
        body: `<p>La predicción se cumple: la actitud ante emprender es peor en España en todo lo que se mide. El emprendedor de éxito tiene prestigio para el 53-65% en España (2022-2025), el 76% en Holanda (2019) y el ~80% en Alemania. El miedo a fracasar frena al 44-52% en España, frente al 34-47% en Holanda. Y quienes están montando algo ahora son el 6-8% de los adultos en España y el 12-14% en Holanda.</p>
        <p>Pero un dato complica la idea de una "cultura" fija: en 2005 el 71% de los españoles veía emprender como buena opción, más que en Alemania (56%) o Francia (61%). Cayó con la crisis y no se ha recuperado. Y la pregunta que más separa a los dos países es otra: "¿ves buenas oportunidades para montar un negocio donde vives?". Dicen que sí el 26-42% en España y el 60-67% en Holanda. La actitud parece seguir a la economía, no al revés.</p>
        <p>Tampoco es una cosa de generaciones. Con los microdatos del GEM, en España los de 18-34 y los de 35-64 responden casi igual (54% y 53% ven emprender como buena opción en 2018), y en Holanda también (83% y 81%). La brecha entre países, de 25-30 puntos, se mantiene en todas las edades desde 2003. Eso sí, los jóvenes tienen el doble de intención de emprender que sus mayores en los dos países (14% frente a 6% en España en 2022; 24% frente a 12% en Holanda).</p><p>Holanda no tiene datos publicados de algunas preguntas después de 2019, así que la comparación más reciente es con Alemania y Francia. Italia se ha quitado del gráfico porque su dato de 2019 tiene un salto anómalo.</p>`,
        src: "Fuente: Global Entrepreneurship Monitor (GEM), indicadores nacionales de la Adult Population Survey, 2001-2025 (encuesta a adultos de 18 a 64 años).",
      },
      {
        id: "c09", verdict: "ok", q: "¿Cuánto cuesta ser autónomo?",
        take: "Ganando 0 €, un autónomo paga 2.471 € al año en España y 350 € en Holanda (y eso es la sanidad, que paga todo el mundo). Ganando 24.000 €, paga 6.928 € en España y 1.316 € en Holanda.",
        pred: "España cobra aunque ganes 0 €; Holanda no; España más cara en ingresos bajos.",
        refute: "España más barata en la mayor parte del rango.",
        body: `<p>Cálculo propio con las reglas de 2026 para una persona soltera, menor de 30, sin hijos y sin otros ingresos. España: cuota por tramos de rendimientos e IRPF estatal más el de la Comunidad de Madrid. Holanda: impuesto box 1 con sus créditos fiscales, deducciones de autónomo, contribución sanitaria Zvw y prima del seguro básico menos el subsidio sanitario. España sale más cara en los 121 puntos calculados, de 0 a 60.000 €.</p>
        <p>La gran diferencia está abajo, justo donde se empieza: en España la cuota mínima (205,88 €/mes) se paga aunque el negocio no facture, y la tarifa plana del primer año la baja a 80 €/mes, nunca a cero. En Holanda los créditos fiscales anulan el impuesto hasta unos 24.000 € de beneficio.</p>
        <p>Matiz justo: la cuota española compra cosas (pensión contributiva, baja por enfermedad, cese de actividad). El autónomo holandés tiene la pensión pública básica (AOW, que va por residencia), pero ni pensión ligada a lo que gana ni seguro de incapacidad salvo que se lo pague él. Aun así, la prueba de "¿cuánto me cuesta probar a emprender?" la gana Holanda de calle. Y la cuota es una decisión política: la cambiaron leyes en 2013, 2017 y 2023.</p>`,
        src: "Fuentes: BOE (RDL 13/2022 y normas de cotización de 2026, Ley y Reglamento del IRPF, DL 1/2010 de la Comunidad de Madrid); Belastingdienst y Rijksoverheid (tarifas, heffingskortingen, zelfstandigenaftrek 2026, Zvw, zorgtoeslag). Cálculo: <code>scripts/c09_cost.py</code>. La tarifa plana de 2026 se asume en 80 €/mes, la cifra fijada para 2023-2025.",
      },
      {
        id: "c10", verdict: "ko", q: "¿Es racional querer ser funcionario?",
        take: "España tiene menos empleo público que la media de la OCDE (15,5% frente a 18,7%), y la plaza pública paga por hora entre un 31% y un 44% más que el sector privado para quien no tiene carrera.",
        pred: "España tiene más empleo público que Holanda y la OCDE, y la prima pública es pequeña (la preferencia sería cultural).",
        refute: "empleo público en España ≤ media OCDE, o la plaza paga más y es más segura para estudios medios (sería cálculo racional).",
        body: `<p>España tiene más empleo público que Holanda (12,6%) pero menos que la media de la OCDE, y muy lejos de Suecia (28,4%) o Dinamarca (27,3%). No es un país de funcionarios.</p>
        <p>Lo que sí es enorme es la prima. Con datos de la Encuesta de Estructura Salarial de 2022 (mediana del salario por hora a jornada completa): con estudios hasta la ESO, 16,51 € en el público frente a 12,56 € en el privado; con Bachillerato o FP, 19,94 € frente a 14,85 €. Entre los de 20-29 años con Bachillerato o FP, 16,85 € frente a 11,70 €. Con carrera universitaria la prima es menor (27,81 € frente a 23,81 €). Parte de la diferencia viene de que el público tiene trabajadores más veteranos y de ocupaciones distintas, pero se mantiene dentro de cada edad y nivel de estudios.</p>
        <p>El matiz: los jóvenes del sector público son mayoritariamente interinos o temporales (65% de los menores de 30 frente al 29% en el privado, en 2026). El premio de verdad es aprobar la oposición y conseguir la plaza fija. Con ese sueldo y esa estabilidad al final, preparar oposiciones no es falta de ambición: es una apuesta racional que el sector privado no iguala.</p>`,
        src: "Fuentes: OCDE, Government at a Glance (empleo de las administraciones públicas en % del empleo total); INE, Encuesta de Estructura Salarial 2022, microdatos (público vs privado por estudios y edad) y tablas publicadas; INE, EPA (temporalidad por sector, 2002-2026).",
      },
    ],
  },
  {
    id: "nl", title: "4. España vs Holanda, sin mitos",
    intro: "Holanda funciona mejor en muchas cosas. Pero ¿en cuáles, y a qué precio?",
    cards: [
      {
        id: "c11", verdict: "mid", q: "Sanidad: lo que pagas y lo que obtienes",
        take: "Holanda gasta un 58% más por persona. A cambio gana claramente en listas de espera y en lo que se paga de bolsillo; en mortalidad tratable empatan, y en España se vive dos años más.",
        pred: "Holanda gana a España en necesidades no cubiertas por listas de espera y en mortalidad tratable.",
        refute: "España igual o mejor en esas dos cosas, gastando menos.",
        body: `<p>Las dos caricaturas fallan. "La mejor sanidad del mundo": el 1,5% de los adultos españoles dice haberse quedado sin atención médica por una lista de espera (2025), frente al 0,2% en Holanda. En España era el 0,1-0,4% hasta 2020 y se disparó después. Además, los españoles pagan de su bolsillo el 21% del gasto sanitario, frente al 12% en Holanda.</p>
        <p>"En Holanda funciona porque es privado": Holanda gasta 5.254 PPS por persona y España 3.319 (2024). En mortalidad tratable (muertes que una buena sanidad debería evitar) empatan: 60,0 frente a 60,2 por 100.000 habitantes (2023). Y en España se vive más (84,0 años frente a 81,9), aunque eso depende de mucho más que la sanidad. Tampoco es un sistema privado al estilo americano: el seguro básico es obligatorio, las aseguradoras no pueden rechazar a nadie y el Estado fija el paquete y subvenciona la prima.</p>
        <p>En resumen, Holanda compra rapidez y menos pago de bolsillo con mucho más dinero. España logra resultados parecidos con mucho menos y lo paga en esperas. La predicción acierta en las listas de espera y falla en la mortalidad tratable.</p>`,
        src: "Fuentes: Eurostat <code>hlth_sha11_hf</code> (gasto por habitante en PPS y gasto de bolsillo), <code>demo_mlexpec</code> (esperanza de vida), <code>hlth_cd_apr</code> (mortalidad tratable, tasa estandarizada), <code>hlth_silc_08</code> (necesidades de examen médico no cubiertas por lista de espera, EU-SILC, mayores de 16).",
      },
      {
        id: "c12", verdict: "ok", q: "¿A dónde va lo que cotizas?",
        take: "Con un sueldo de 30.000 € brutos, en España el 21% del coste laboral va a pagar las pensiones actuales. En Holanda, el 3% después de créditos fiscales, y otro 8% va al fondo de pensiones del propio trabajador.",
        pred: "un joven español manda a las pensiones actuales una parte mayor de su sueldo que un holandés.",
        refute: "partes parecidas.",
        body: `<p>Para el mismo sueldo bruto, al trabajador español le queda neto el 59% de lo que cuesta a la empresa y al holandés el 73% (antes de pagar la prima del seguro sanitario, unos 1.900 € al año). La diferencia grande está en las pensiones: en España casi todo es reparto (lo que pagas hoy lo cobra el pensionista de hoy); en Holanda el reparto (AOW) pesa menos y una parte importante va a un fondo de capitalización a nombre del trabajador.</p>
        <p>Dos matices. La cifra española es un techo: las contingencias comunes también pagan bajas por enfermedad y maternidad, aunque la mayor parte va a pensiones. Y la holandesa depende de los créditos fiscales: antes de ellos, la prima AOW sería el 14% del coste laboral, que sigue siendo bastante menos que el 21% español.</p>
        <p>Esto da la razón a la tesis en un punto: el sistema español traslada mucho dinero del joven al jubilado. Pero el modelo holandés no es "privado": los fondos son obligatorios en la práctica por convenio colectivo y la AOW es pública. Fue una decisión política de hace 70 años, y ahora mismo Holanda la está reformando por ley.</p>`,
        src: "Fuentes: BOE (tipos de cotización 2026: contingencias comunes, desempleo, FOGASA, formación, MEI; IRPF estatal y de Madrid); Belastingdienst (tarifa box 1, primas AOW/Anw/Wlz, heffingskortingen, Zvw de empresa); tipos 2026 del fondo de pensiones ABP. Cálculo: <code>scripts/c12_contrib.py</code>.",
      },
      {
        id: "c13", verdict: "mid", q: "¿Quién vota, y quién se lleva el gasto?",
        take: "En 1982, el 24% de los votos venía de menores de 30 y el 16% de mayores de 65. En 2023, 14% y 25%: se han dado la vuelta. Por cada euro público que va a un joven en educación, familia y vivienda, van 3,5 € a cada mayor en pensiones.",
        pred: "el peso de los mayores de 65 en los votos y la brecha de gasto mayores/jóvenes crecieron, con PP y con PSOE por igual.",
        refute: "la brecha no creció, o cambia según el partido.",
        body: `<p><b>Votos.</b> La predicción acierta: el peso de los mayores se ha disparado. Casi todo es demografía: los menores de 30 han pasado del 26% al 15% de la población adulta y los mayores de 65 del 16% al 24%. La abstención añade algo: en 1982 los jóvenes votaban 3 puntos menos que los mayores y en 2023, unos 10 menos. Si los jóvenes votaran como los mayores, su peso subiría solo del 13,8% al 15,6%: el problema es más de número que de abstención.</p>
        <p><b>Gasto.</b> Aquí la predicción falla a medias. En euros, la distancia creció (de 11.000 € a 14.900 € de 2025 por persona entre 1995 y 2024). Pero en proporción se redujo: en 1995 cada mayor recibía 4,9 veces lo que cada joven y en 2024, 3,5 veces, porque el gasto en educación y familia creció más deprisa. Tampoco hay patrón por partido: con Aznar (PP) la proporción bajó mucho (4,9 a 3,6), con Rajoy (PP) subió (3,6 a 3,8) y con Zapatero y Sánchez (PSOE) apenas se movió o bajó. En Holanda la proporción es 1,3.</p>
        <p>Cautelas: la participación por edad sale de encuestas del CIS (la gente dice que vota más de lo que vota), reescalada a la participación oficial de cada elección; la población incluye a extranjeros sin voto en generales, que se concentran en edades jóvenes y medias; y el gasto holandés en mayores no incluye sus fondos de pensiones, que son privados.</p>`,
        src: "Fuentes: CIS, encuestas postelectorales de las 14 elecciones generales 1982-2023 (participación declarada por edad); Ministerio del Interior, participación oficial; Eurostat <code>demo_pjan</code> (población por edad) y <code>gov_10a_exp</code> (gasto público por funciones: vejez y supervivencia para mayores; familia, vivienda y educación para menores de 30), en euros de 2025.",
      },
    ],
  },
  {
    id: "esp", title: "5. Esperanza, esfuerzo y ambición",
    intro: "La parte cualitativa: qué piensan los jóvenes. Solo preguntas con la misma redacción en todas las oleadas.",
    cards: [
      {
        id: "cA", verdict: "na", q: "¿Esperan los jóvenes que les vaya mejor?",
        take: "No se puede responder con datos abiertos. Las preguntas existen desde los 80 (Eurobarómetro, CIS), pero los resultados por edad y país solo están en microdatos con registro.",
        pred: "los jóvenes españoles son hoy menos optimistas que en los 80, y menos que los holandeses.",
        refute: "no son menos optimistas que entonces, o no menos que los holandeses.",
        body: `<p>La pregunta del Eurobarómetro sobre si el año que viene será mejor o peor se hace desde 1980 (España desde 1985). Su redacción cambió en 1995 ("los próximos doce meses") y otra vez en 2020, así que hay dos tramos comparables: 1985-1994 y 1995-2019. El CIS pregunta por la situación económica personal dentro de un año, pero solo publica totales, sin cruce por edad.</p>
        <p>Para hacer este gráfico hace falta una cuenta gratuita en GESIS (microdatos del Eurobarómetro) o pedir los microdatos al CIS por su formulario. Queda pendiente.</p>`,
        src: "Detalle de preguntas, redacciones y accesos en <code>sources/cA.md</code> del repositorio.",
        pending: "Sin datos abiertos por edad: pendiente de microdatos (GESIS / CIS)",
      },
      {
        id: "cB", verdict: "ko", q: "¿Creen que el esfuerzo merece la pena?",
        take: "Los jóvenes españoles creen en el esfuerzo tanto como los holandeses: el 37% de los menores de 30 (2011) frente al 38% en Holanda (2012). Y en España ha subido: en 1990 era el 23%.",
        pred: "menos en España que en Holanda, y bajando en España.",
        refute: "parecido a Holanda o sin bajar.",
        body: `<p>La pregunta es la misma en todas las oleadas: en una escala de 1 a 10, ¿el trabajo duro suele traer una vida mejor (1) o el éxito es más cuestión de suerte y contactos (10)? Aquí se cuenta a quien responde de 1 a 3.</p>
        <p>La predicción falla en las dos partes: los jóvenes españoles no creen menos en el esfuerzo que los holandeses, y la cifra no ha bajado con el tiempo. Con la competencia pasa lo mismo: la valoran tanto o más los jóvenes españoles (39-48%) que los holandeses (28-41%).</p>
        <p>Límites importantes: la última oleada española disponible con la pregunta del esfuerzo es de 2011, así que no recoge a la generación que hoy tiene 20-30 años. Cada grupo de edad tiene unas 190-400 respuestas por oleada (margen de unos 5-7 puntos). Y el salto español entre 1990 y 1995 es sospechoso: puede deberse a un cambio de cuestionario. La comparación más sólida es la de España 2011 con Holanda 2012, porque es la misma oleada y el mismo cuestionario.</p>`,
        src: "Fuente: World Values Survey y European Values Study, ficheros integrados, por edad (ítems E040 \"trabajo duro vs suerte\" y E039 \"competencia buena vs dañina\"). España: 1990-2017; Holanda: 1990-2022.",
      },
      {
        id: "cC", verdict: "na", q: "¿Dónde quieren trabajar?",
        take: "No se puede responder: no existe una pregunta sobre empleo público, empresa privada o negocio propio repetida con la misma redacción desde 1984.",
        pred: "más jóvenes quieren hoy un empleo público que en 1984.",
        refute: "igual o menos.",
        body: `<p>Los Informes Juventud en España de 2020 y 2024 y la Encuesta de Juventud 2023 no preguntan por el sector preferido. El de 2020 pregunta por la "ocupación ideal", que no es comparable, y del informe de 1984 no hay versión digital con esa pregunta. Lo más parecido es el módulo de orientación laboral del ISSP (1997, 2005 y 2015, con registro en GESIS), que daría 1997-2015 y no 1984-2024.</p>
        <p>Lo que sí se puede medir está en el gráfico 10: no hay más empleo público que en otros países, y la plaza paga bastante más que el sector privado.</p>`,
        src: "Detalle de la búsqueda en <code>sources/cC.md</code> del repositorio.",
        pending: "Sin pregunta comparable entre 1984 y 2024",
      },
    ],
  },
];
