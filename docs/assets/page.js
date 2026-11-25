// Renders SECTIONS (content.js) and draws each chart with DRAW[id].
const VERDICT = { ok: "Predicción cumplida", ko: "Predicción fallada", mid: "A medias", na: "Sin datos suficientes" };
const GOVKEY = `<p class="govkey">Fondo: <i style="background:${PARTY.PSOE}33"></i>PSOE <i style="background:${PARTY.PP}33"></i>PP · punteado: euro, crisis 2008, covid</p>`;

function tabs(el, names, onPick) {
  const bar = document.createElement("div");
  bar.className = "tabs";
  const box = document.createElement("div");
  box.className = "chart";
  names.forEach((n, i) => {
    const b = document.createElement("button");
    b.textContent = n;
    b.onclick = () => { [...bar.children].forEach((c) => c.classList.remove("on")); b.classList.add("on"); bar.dataset.on = i; onPick(i, box); };
    bar.appendChild(b);
  });
  el.append(bar, box);
  bar.children[0].classList.add("on");
  bar.dataset.on = 0;
  register(() => onPick(+bar.dataset.on, box));
}

const DRAW = {
  async c01(el) {
    const d = await load("c01");
    const names = d.share_epa.length ? ["España desde 1999", "Comparado con Holanda y la UE", "Edad media al irse de casa"] : ["Comparado con Holanda y la UE", "Edad media al irse de casa"];
    tabs(el, names, (i, box) => {
      const n = names[i];
      if (n === "España desde 1999") line(box, d.share_epa, { pct: true, y: "% de 25-34 que vive con algún progenitor (EPA)", ymax: 55 });
      else if (n.startsWith("Comparado")) line(box, d.share, { pct: true, y: "% de 25-34 que vive con sus padres (EU-SILC)" });
      else line(box, d.age, { ymin: 20, ymax: 32, y: "años", dec: 1 });
    });
    el.insertAdjacentHTML("beforeend", GOVKEY);
  },
  async c02(el) {
    const d = await load("c02");
    tabs(el, ["Años de sueldo para comprar 80 m²", "Precio / renta de un hogar, desde 1987", "% del sueldo joven para alquilar"], (i, box) => {
      if (i === 0) line(box, d.years, { y: "años de sueldo bruto", dots: true, colors: { "Joven de 25-34": COLORS["España"], "Todas las edades": "#8a8f98" }, mr: 110, mrs: 90, xmin: 1994 });
      else if (i === 1) line(box, d.bde, { y: "años de renta bruta de un hogar", endLabels: false, colors: { "Precio / renta bruta de un hogar (Banco de España)": "#2c3e50" } });
      else line(box, d.rent, { pct: true, y: "% del sueldo bruto mensual de 25-34", ymax: 55, colors: { "Alquiler nuevo medio en Cataluña": COLORS["España"], "Alquiler mediano de 70 m² en España (contratos en vigor)": "#8a8f98" }, endLabels: false });
    });
    el.insertAdjacentHTML("beforeend", GOVKEY + `<div class="legend"><span class="lg"><i style="background:${COLORS["España"]}"></i>Joven 25-34 / alquiler nuevo (Cataluña)</span><span class="lg"><i style="background:#8a8f98"></i>Todas las edades / alquiler en vigor (España)</span></div>`);
  },
  async c03(el) {
    const d = await load("c03");
    const col = { "Precios del joven que alquila (alquiler nuevo)": COLORS["España"], "Ídem con el alquiler del IPC": "#e8a39e", "IPC general": "#8a8f98", "Sueldo bruto medio de 25-34": "#1e7b4f" };
    const ch = el.appendChild(Object.assign(document.createElement("div"), { className: "chart" }));
    register(() => line(ch, d, { y: "índice, 2008 = 100", ymin: 80, ymax: 145, colors: col, endLabels: false }));
    const lg = document.createElement("div"); lg.className = "legend"; legend(lg, Object.keys(col), col); el.appendChild(lg);
    el.insertAdjacentHTML("beforeend", GOVKEY);
  },
  async c04(el) {
    const d = await load("c04");
    line(el, d, { y: "miles al año", colors: { "Viviendas terminadas": "#2c3e50", "Hogares nuevos": COLORS["España"], "Protegidas (VPO)": "#9aa5b1" }, mr: 170, mrs: 120 });
    el.insertAdjacentHTML("beforeend", GOVKEY);
  },
  async c05(el) {
    const d = await load("c05_labour");
    const panel = await load("c05_panel").catch(() => null);
    const names = ["Paro juvenil", "Jóvenes con < 1 año en su empleo"];
    if (panel) names.push("Panel: España menos control");
    tabs(el, names, (i, box) => {
      if (i === 0) line(box, d.unemp, { pct: true, y: "% de la población activa" });
      else if (i === 1) line(box, d.tenure, { pct: true, y: "% de ocupados 15-24" });
      else drawPanel(box, panel);
    });
    el.insertAdjacentHTML("beforeend", GOVKEY);
  },
  async c07(el) {
    const d = await load("c07");
    register(() => {
      const width = el.clientWidth || 640;
      const box = el.querySelector(".chart") || el.appendChild(Object.assign(document.createElement("div"), { className: "chart" }));
      box.replaceChildren(Plot.plot({
        width, height: Math.round(Math.max(260, Math.min(380, width * 0.55))), marginLeft: 50, marginBottom: 40,
        style: { fontSize: width > 520 ? "12px" : "10.5px" },
        x: { label: "Margen del PP en las municipales (puntos) →", grid: true },
        y: { label: "↑ Viviendas construidas en los 4 años siguientes por 1.000 hab.", grid: true },
        color: { type: "ordinal", domain: [2015, 2019], range: ["#2c3e50", COLORS["España"]], legend: true, tickFormat: (v) => `municipales ${v}` },
        marks: [
          Plot.rectX([{ a: -10, b: 10 }], { x1: "a", x2: "b", fill: "#f2efe8" }),
          Plot.ruleX([0], { stroke: "#333" }),
          Plot.dot(d, { x: "m", y: "d", stroke: "year", r: 3.5 }),
          Plot.tip(d, Plot.pointer({ x: "m", y: "d", title: (r) => `${r.name} (${r.year})
Margen PP: ${r.m}
Viviendas/1.000: ${r.d}
Habitantes: ${r.pop}` })),
        ],
      }));
    });
  },
  async c08(el) {
    const d = await load("c08");
    const ms = [...new Set(d.map((x) => x.m))];
    tabs(el, ms, (i, box) => {
      const rows = d.filter((x) => x.m === ms[i] && ["España", "Holanda", "Alemania", "Francia"].includes(x.s));
      line(box, rows, { pct: true, govs: false, shocks: false, dots: true, y: "% de adultos 18-64" });
    });
  },
  async c09(el) {
    const d = await load("c09");
    const col = { "España": COLORS["España"], "España, 1.er año (tarifa plana)": "#e8a39e", "Holanda": COLORS["Holanda"], "Holanda, empezando (startersaftrek)": "#f9c999" };
    const lg = document.createElement("div");
    lg.className = "legend";
    legend(lg, Object.keys(col), col);
    tabs(el, ["Lo que pagas al año", "Zoom: de 0 a 24.000 €"], (i, box) => {
      const rows = i === 0 ? d : d.filter((r) => r.x <= 24000);
      const width = box.clientWidth || 640;
      box.replaceChildren(Plot.plot({
        width, height: Math.round(Math.max(260, Math.min(380, width * 0.56))), marginLeft: 56, marginRight: width > 520 ? 20 : 10, marginBottom: 42,
        style: { fontSize: width > 520 ? "12px" : "10.5px" },
        x: { label: "Beneficio neto anual del negocio (€) →", tickFormat: (v) => v / 1000 + "k", grid: true },
        y: { label: "↑ Pagas al año (€): cotizaciones + IRPF + sanidad", grid: true },
        marks: [
          Plot.ruleY([0]),
          Plot.line(rows, { x: "x", y: "y", z: "s", stroke: (r) => col[r.s], strokeWidth: 2.4 }),
          Plot.tip(rows, Plot.pointer({ x: "x", y: "y", title: (r) => `${r.s}\nGanando ${fmt(r.x)} €: pagas ${fmt(r.y)} €` })),
        ],
      }));
    });
    el.appendChild(lg);
  },
  async c12(el) {
    const d = await load("c12");
    const cats = ["Pensiones actuales (reparto)", "Tu propio fondo / reserva", "Sanidad y dependencia", "Paro, incapacidad y otros", "Impuesto sobre la renta", "Te queda neto"];
    const col = ["#b3261e", "#1e7b4f", "#3b7dd8", "#8a8f98", "#2c3e50", "#e9e5dc"];
    const box = document.createElement("div");
    box.className = "chart";
    box.style.minHeight = "0";
    const lg = document.createElement("div");
    lg.className = "legend";
    lg.innerHTML = cats.map((c, i) => `<span class="lg"><i style="background:${col[i]}"></i>${c}</span>`).join("");
    el.append(box, lg);
    register(() => {
      const width = el.clientWidth || 640;
      box.replaceChildren(Plot.plot({
        width, height: 170, marginLeft: 70, marginRight: 10,
        style: { fontSize: width > 520 ? "12px" : "10.5px" },
        caption: "% del coste laboral total: sueldo bruto + cotización de la empresa",
        x: { label: null, domain: [0, 100], tickFormat: (v) => v + "%" },
        y: { label: null, domain: ["España", "Holanda"] },
        color: { domain: cats, range: col },
        marks: [
          Plot.barX(d, Plot.stackX({ x: "pct", y: "geo", fill: "cat", order: cats, inset: 0.5 })),
          Plot.text(d, Plot.stackX({ x: "pct", y: "geo", z: "cat", order: cats, text: (r) => (r.pct >= (width > 520 ? 5 : 9) ? Math.round(r.pct) + "%" : ""), fill: (r) => (r.cat === "Te queda neto" ? "#333" : "white"), fontWeight: 700 })),
          Plot.tip(d, Plot.pointer(Plot.stackX({ x: "pct", y: "geo", z: "cat", order: cats, title: (r) => `${r.geo} · ${r.cat}\n${fmt(r.eur)} € al año (${r.pct}%)` }))),
        ],
      }));
    });
  },
  async c06(el) {
    const d = await load("c06");
    const gapChart = (box, ev, rows, ylab, xmax) => {
      const width = box.clientWidth || 640;
      const ys = rows.map((r) => r.y).concat([ev.pre_min, ev.pre_max]);
      const lo = Math.min(...ys), hi = Math.max(...ys), pad = (hi - lo) * 0.15;
      box.replaceChildren(Plot.plot({
        width, height: Math.round(Math.max(240, Math.min(330, width * 0.5))), marginLeft: 46, marginRight: width > 520 ? 20 : 8,
        style: { fontSize: width > 520 ? "12px" : "10.5px" },
        x: { label: "Meses desde la ley →", grid: true },
        y: { label: "↑ " + ylab, domain: [lo - pad, hi + pad], grid: true },
        marks: [
          Plot.rect([ev], { x1: -36, x2: xmax, y1: "pre_min", y2: "pre_max", fill: "#ece8df" }),
          Plot.text([ev], { x: -35, y: "pre_max", text: () => "rango antes de la ley", textAnchor: "start", dy: -6, fill: "#777", fontSize: 10 }),
          Plot.ruleX([0], { stroke: "#222", strokeWidth: 1.5 }),
          Plot.text([0], { x: 0, frameAnchor: "top", text: () => "ley", dx: 14, fill: "#222", fontWeight: 700 }),
          Plot.ruleY([ev], { y: "post_mean", x1: 0, x2: xmax, stroke: COLORS["España"], strokeDasharray: "5,4", strokeWidth: 1.6 }),
          Plot.line(rows, { x: "x", y: "y", stroke: "#2c3e50", strokeWidth: 1.8 }),
          Plot.tip(rows, Plot.pointer({ x: "x", y: "y", title: (r) => `Mes ${r.x}: ${fmt(r.y, { dec: 2 })}` })),
        ],
      }));
    };
    const cfg = [
      { name: "SMI 2019", e: d.smi, y: "Provincias donde el SMI pesa más − donde pesa menos (puntos)", what: "Parte de los afiliados que tiene 16-24 años: provincias donde el SMI pesa más menos provincias donde pesa menos.", xmax: 36 },
      { name: "Reforma laboral 2022", e: d.reform, y: "España − Portugal (puntos)", what: "Parte de los ocupados de 15-24 que lleva menos de 3 meses en su empleo: España menos Portugal. Más alto = menos estabilidad en España.", xmax: 36 },
      { name: "...y la etiqueta del contrato", label: true },
      { name: "Cuotas de autónomos 2023", e: d.reta, y: "Menores de 30 − 30-44 (%)", what: "Crecimiento de los autónomos menores de 30 menos el de los de 30-44 (índice, diciembre de 2022 = 0).", xmax: 35 },
    ];
    const note = document.createElement("div");
    tabs(el, cfg.map((c) => c.name), (i, box) => {
      const c = cfg[i];
      if (c.label) {
        line(box, d.reform.label.map((r) => ({ ...r, x: r.x })), { govs: false, shocks: false, endLabels: false, pct: true, ymin: 0, ymax: 100, xmin: -36, xmax: 36, y: "% de afiliados menores de 30 con contrato indefinido", colors: { "Menores de 30 con contrato indefinido": "#2c3e50" } });
        note.innerHTML = '<p class="govkey">El nombre del contrato cambió de golpe en abril de 2022. La pestaña anterior mide si cambió la estabilidad real.</p>';
        return;
      }
      gapChart(box, c.e.eval, c.e.gap, c.y, c.xmax);
      const e = c.e.eval;
      note.innerHTML = `<p class="govkey">${c.what} Franja gris: rango de la diferencia en los ${e.n_pre} periodos previos. Línea roja discontinua: media después de la ley (${fmt(e.post_mean, { dec: 2 })}). ${e.moved ? "<b>Se sale de la franja: la ley movió algo.</b>" : "<b>Se queda dentro de la franja: nada medible.</b>"}</p>`;
    });
    el.appendChild(note);
  },
  async c10(el) {
    const d = await load("c10");
    tabs(el, ["Empleo público (% del total)", "Sueldo por hora: público vs privado", "Temporalidad de los jóvenes"], (i, box) => {
      const width = box.clientWidth || 640;
      const fs = { fontSize: width > 520 ? "12px" : "10.5px" };
      if (i === 0) {
        const hl = { "España": COLORS["España"], "Holanda": COLORS["Holanda"], "Media OCDE": "#222" };
        box.replaceChildren(Plot.plot({
          caption: `% del empleo total que trabaja para las administraciones públicas (${d.year})`,
          width, height: 26 * d.bars.length + 40, marginLeft: 92, marginRight: 30, style: fs,
          x: { label: null, grid: true },
          y: { label: null, domain: d.bars.slice().sort((a, b) => b.v - a.v).map((b) => b.geo) },
          marks: [
            Plot.barX(d.bars, { x: "v", y: "geo", fill: (b) => hl[b.geo] || "#c9ccd1" }),
            Plot.text(d.bars, { x: "v", y: "geo", text: (b) => fmt(b.v), dx: 16, fill: "#333" }),
          ],
        }));
      } else if (i === 1) {
        const rows = d.pay.filter((r) => r.var === "median_gross_hourly_wage_ft_fullyear").flatMap((r) => [
          { g: (r.age === "all" ? "Todas las edades" : "20-29 años"), edu: r.edu, s: "Público", v: r.public },
          { g: (r.age === "all" ? "Todas las edades" : "20-29 años"), edu: r.edu, s: "Privado", v: r.private }]);
        box.replaceChildren(Plot.plot({
          width, height: 300, marginLeft: 120, marginRight: 30, style: fs,
          fy: { label: null }, x: { label: `Mediana del salario bruto por hora, jornada completa (${d.pay_year}, €) →`, grid: true },
          y: { label: null, domain: ["Público", "Privado"], axis: null },
          color: { domain: ["Público", "Privado"], range: [COLORS["España"], "#8a8f98"], legend: true },
          marks: [
            Plot.barX(rows, { x: "v", y: "s", fy: (r) => `${r.edu} · ${r.g}`, fill: "s" }),
            Plot.text(rows, { x: "v", y: "s", fy: (r) => `${r.edu} · ${r.g}`, text: (r) => fmt(r.v, { dec: 2 }), dx: 18, fill: "#333", fontSize: 10 }),
          ],
        }));
      } else {
        line(box, d.temp, { pct: true, y: "% de asalariados de 16-29 con contrato temporal", colors: { "Sector público": COLORS["España"], "Sector privado": "#8a8f98" } });
      }
    });
  },
  async c11(el) {
    const d = await load("c11");
    tabs(el, ["Gasto vs esperanza de vida", "Gasto vs mortalidad tratable", "Sin atención por lista de espera"], (i, box) => {
      if (i === 0) scatter(box, d.points, { x: "spend", y: "life", xl: `Gasto sanitario por persona (PPS, ${d.years.spend})`, yl: `Esperanza de vida (${d.years.life})`, highlight: ["ES", "NL"] });
      else if (i === 1) scatter(box, d.points, { x: "spend", y: "treat", xl: `Gasto sanitario por persona (PPS, ${d.years.spend})`, yl: `Muertes tratables por 100.000 (${d.years.treat}; abajo = mejor)`, yrev: true, highlight: ["ES", "NL"] });
      else line(box, d.wait_ts, { pct: true, govs: false, y: "% de mayores de 16", dec: 1 });
    });
  },
  async c13(el) {
    const d = await load("c13_spend");
    const votes = await load("c13_votes").catch(() => null);
    const names = ["Euros por mayor / euros por joven", "Euros por persona en España"];
    if (votes) names.unshift("Quién vota");
    tabs(el, names, (i, box) => {
      const n = names[i];
      if (n === "Quién vota") drawVotes(box, votes);
      else if (n.startsWith("Euros por mayor")) line(box, d.map((r) => ({ x: r.x, y: r.ratio, s: r.geo === "ES" ? "España" : "Holanda" })), { y: "veces", dec: 2, ymax: 5.5 });
      else line(box, d.filter((r) => r.geo === "ES").flatMap((r) => [{ x: r.x, y: r.old, s: "Por cada mayor de 65" }, { x: r.x, y: r.young, s: "Por cada menor de 30" }]), { y: "€ de 2025", colors: { "Por cada mayor de 65": "#555", "Por cada menor de 30": COLORS["España"] }, mr: 150, mrs: 110 });
    });
    el.insertAdjacentHTML("beforeend", GOVKEY);
  },
  async cA(el) {
    const d = await load("cA");
    const ms = [...new Set(d.map((x) => x.m))].sort((a, b) => (a.includes("mejor") ? -1 : 1));
    tabs(el, ms, (i, box) => {
      const rows = d.filter((x) => x.m === ms[i]);
      line(box, rows, { pct: true, ymin: 0, ymax: i === 0 ? 75 : 36, y: "% de cada grupo", mr: 112, mrs: 92,
        breaks: [{ x: 1994.5, n: "cambia la pregunta" }] });
    });
    el.insertAdjacentHTML("beforeend", GOVKEY.replace("</p>", " · líneas: media de 3 años (cada oleada tiene unos ±7 puntos de margen)</p>"));
  },
  async cC(el) {
    const d = await load("cC");
    const ms = [...new Set(d.map((x) => x.m))].sort((a, b) => (a.includes("Estado") ? -1 : 1));
    tabs(el, ms, (i, box) => {
      const rows = d.filter((x) => x.m === ms[i]);
      const order = ["España", "Francia", "Portugal", "Alemania", "Holanda"];
      const width = box.clientWidth || 640;
      const span = order.map((c) => { const v = rows.filter((r) => r.s === c).map((r) => r.y); return { s: c, a: Math.min(...v), b: Math.max(...v) }; });
      const yc = { 1989: "#c9c9c9", 1997: "#8a8f98", 2005: "#1d1d1f" };
      box.replaceChildren(Plot.plot({
        width, height: 300, marginLeft: 76, marginRight: 20, marginTop: 30, marginBottom: 46,
        style: { fontSize: width > 520 ? "12.5px" : "11px" },
        x: { domain: [0, 85], grid: true, tickFormat: (v) => v + "%", label: "% de los jóvenes de 18-29 años que eligen esa opción", labelAnchor: "center", labelOffset: 40 },
        y: { domain: order, label: null, tickFormat: (c) => c },
        marks: [
          Plot.link(span, { x1: "a", x2: "b", y1: "s", y2: "s", stroke: "#bbb", strokeWidth: 2 }),
          Plot.dot(rows, { x: "y", y: "s", fill: (r) => yc[r.x], r: 6.5, stroke: "white", strokeWidth: 1.5 }),
          ...[1989, 1997, 2005].map((yr) => Plot.text(rows.filter((r) => r.x === yr), { x: "y", y: "s", text: (r) => Math.round(r.y) + "%", dy: yr === 1997 ? 16 : -14, fontSize: 10.5, fontWeight: 600, fill: yr === 1989 ? "#9a9a9a" : yc[yr] })),
          Plot.tip(rows, Plot.pointer({ x: "y", y: "s", title: (r) => `${r.s} ${r.x}: ${fmt(r.y, { pct: true })}` })),
        ],
      }));
      box.insertAdjacentHTML("beforeend", `<div class="legend">${Object.entries(yc).map(([y, c]) => `<span class="lg"><i style="background:${c};border-radius:99px"></i>${y}</span>`).join("")}</div>`);
    });
  },
  async cB(el) {
    const d = await load("cB");
    const ms = [...new Set(d.map((x) => x.m))];
    tabs(el, ms, (i, box) => line(box, d.filter((x) => x.m === ms[i]), { pct: true, govs: false, shocks: false, dots: true, y: "% que responde así", mr: 110 }));
  },
};

function drawPanel(box, panel) {
  box.innerHTML = "";
  const lagName = { lag0: "sin retraso", lag2: "+2 años", lag4: "+4 años" };
  for (const m of panel.metrics) {
    const h = document.createElement("p");
    h.className = "sub";
    h.textContent = m.label + (m.better === "down" ? " · abajo = mejor para España" : " · arriba = mejor para España");
    const c = document.createElement("div");
    c.className = "chart";
    box.append(h, c);
    const ys = m.series.map((d) => d.y);
    const lo = Math.min(0, ...ys), hi = Math.max(...ys);
    line(c, m.series, { ymin: lo - Math.abs(hi - lo) * 0.08, ymax: hi + Math.abs(hi - lo) * 0.12, refY: 0, endLabels: false, height: 210, dec: 1 });
    const sum = panel.summary[m.key];
    const govs = [...new Set(Object.values(sum).flatMap((l) => l.rows.map((r) => r.gov)))];
    const tbl = document.createElement("table");
    tbl.className = "mini";
    tbl.innerHTML = `<tr><th>Mejora media por año</th>${govs.map((g) => `<th>${g}</th>`).join("")}<th>Patrón</th></tr>` +
      Object.entries(sum).map(([lag, l]) => `<tr><td>${lagName[lag]}</td>${govs.map((g) => { const r = l.rows.find((x) => x.gov === g); return `<td>${r ? (r.improve > 0 ? "+" : "") + r.improve.toFixed(2) : "–"}</td>`; }).join("")}<td><b>${l.pattern}</b></td></tr>`).join("");
    box.append(tbl);
  }
}
function drawVotes(box, votes) {
  const rows = votes.filter((r) => r.s === "Votos de 18-29" || r.s === "Votos de 65+");
  line(box, rows, { pct: true, y: "% de todos los votos emitidos", dots: true, ymax: 30, colors: { "Votos de 18-29": COLORS["España"], "Votos de 65+": "#2c3e50" }, xmin: 1981, xmax: 2024 });
}

function render() {
  const main = document.getElementById("main");
  const counts = { ok: 0, ko: 0, mid: 0, na: 0 };
  for (const sec of SECTIONS) {
    const s = document.createElement("section");
    s.className = "block";
    s.id = sec.id;
    s.innerHTML = `<h2>${sec.title}</h2><p class="intro">${sec.intro}</p>`;
    for (const c of sec.cards) {
      counts[c.verdict] = (counts[c.verdict] || 0) + 1;
      const card = document.createElement("article");
      card.className = "card";
      card.id = c.id;
      card.innerHTML = `<h3>${c.q}</h3><span class="pill ${c.verdict}">${VERDICT[c.verdict]}</span>
        <p class="take">${c.take}</p><div class="chartwrap"></div>
        <details><summary>Predicción, discusión y fuentes</summary><div class="body">
          <p class="pred"><b>Predicción (escrita antes de los datos):</b> ${c.pred}<br><b>Se refuta si:</b> ${c.refute}</p>
          ${c.body}<p class="src">${c.src}</p></div></details>`;
      s.appendChild(card);
      const wrap = card.querySelector(".chartwrap");
      if (DRAW[c.id] && !c.pending) DRAW[c.id](wrap).catch((e) => { wrap.innerHTML = `<p class="pending">Error cargando datos: ${e}</p>`; });
      else wrap.innerHTML = `<p class="pending">${c.pending || "Datos en camino"}</p>`;
    }
    main.appendChild(s);
  }
  document.getElementById("score").innerHTML =
    `<div class="ok"><b>${counts.ok}</b><span>predicciones cumplidas</span></div><div class="ko"><b>${counts.ko}</b><span>falladas</span></div>` +
    `<div class="mid"><b>${counts.mid}</b><span>a medias</span></div><div class="na"><b>${counts.na}</b><span>sin datos suficientes</span></div>`;
  document.getElementById("tldr-body").innerHTML = TLDR;
}
render();
