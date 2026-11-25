// Chart helpers on top of Observable Plot. Data files live in data/*.json.
const GOVS = [
  { s: 1977.5, e: 1982.92, p: "UCD", n: "UCD" },
  { s: 1982.92, e: 1996.33, p: "PSOE", n: "González" },
  { s: 1996.33, e: 2004.33, p: "PP", n: "Aznar" },
  { s: 2004.33, e: 2011.97, p: "PSOE", n: "Zapatero" },
  { s: 2011.97, e: 2018.42, p: "PP", n: "Rajoy" },
  { s: 2018.42, e: 2026.9, p: "PSOE", n: "Sánchez" },
];
const PARTY = { UCD: "#9e9e9e", PSOE: "#e30613", PP: "#1d84ce" };
const SHOCKS = [{ x: 2002, n: "euro" }, { x: 2008.7, n: "crisis" }, { x: 2020.2, n: "covid" }];
const COLORS = {
  "España": "#b3261e", "Holanda": "#f28e2b", "Media UE": "#8a8f98", "Portugal": "#3b7dd8",
  "Alemania": "#59a14f", "Francia": "#76b7b2", "Italia": "#af7aa1",
  "España <30": "#b3261e", "España 50+": "#e8a39e", "Holanda <30": "#f28e2b", "Holanda 50+": "#f9c999",
  "España 18-29": "#b3261e", "Holanda 18-29": "#f28e2b",
};
const colorOf = (s, extra = {}) => extra[s] || COLORS[s] || COLORS[s.split(" (")[0]] || "#444";

const cache = {};
function load(name) {
  if (!cache[name]) cache[name] = fetch(`data/${name}.json`).then((r) => r.json());
  return cache[name];
}

function fmt(v, o = {}) {
  if (v == null || Number.isNaN(v)) return "–";
  const s = Math.abs(v) >= 1000 ? Math.round(v).toLocaleString("es-ES") : (+v).toLocaleString("es-ES", { maximumFractionDigits: o.dec ?? 1 });
  return o.pct ? s + "%" : o.unit ? `${s} ${o.unit}` : s;
}

function govLayer(xmin, xmax, ymin, ymax, width, lag = 0) {
  const g = GOVS.map((d) => ({ ...d, s: Math.max(d.s + lag, xmin), e: Math.min(d.e + lag, xmax) })).filter((d) => d.e - d.s > 0.3);
  const m = [Plot.rect(g, { x1: "s", x2: "e", y1: ymin, y2: ymax, fill: (d) => PARTY[d.p], fillOpacity: 0.075 })];
  if (width > 480) m.push(Plot.text(g.filter((d) => d.e - d.s > 1.6), { x: (d) => (d.s + d.e) / 2, y: ymax, text: "n", dy: -7, fill: (d) => PARTY[d.p], fontSize: 10 }));
  return m;
}

function line(el, data, o = {}) {
  const width = el.clientWidth || 640;
  const xs = data.map((d) => +d.x);
  const xmin = o.xmin ?? Math.min(...xs), xmax = o.xmax ?? Math.max(...xs);
  const ymin = o.ymin ?? 0;
  const ymax = o.ymax ?? Math.max(...data.map((d) => d.y)) * 1.1;
  const marks = [];
  if (o.govs !== false) marks.push(...govLayer(xmin, xmax, ymin, ymax, width, o.lag ?? 0));
  if (o.shocks !== false) marks.push(Plot.ruleX(SHOCKS.filter((d) => d.x >= xmin && d.x <= xmax), { x: "x", stroke: "#aaa", strokeDasharray: "2,3" }));
  if (o.breaks) marks.push(Plot.ruleX(o.breaks, { x: "x", stroke: "#666", strokeDasharray: "5,3" }),
    Plot.text(o.breaks, { x: "x", y: ymin, text: "n", dx: 5, dy: -8, textAnchor: "start", fontSize: 10.5, fill: "#555" }));
  if (o.refY !== undefined) marks.push(Plot.ruleY([o.refY], { stroke: "#555", strokeDasharray: "4,3" }));
  marks.push(Plot.ruleY([ymin]));
  marks.push(Plot.line(data, { x: "x", y: "y", z: "s", stroke: (d) => colorOf(d.s, o.colors), strokeWidth: 2.3, curve: o.curve ?? "monotone-x" }));
  if (o.dots) marks.push(Plot.dot(data, { x: "x", y: "y", fill: (d) => colorOf(d.s, o.colors), r: 3 }));
  marks.push(Plot.dot(data, Plot.pointer({ x: "x", y: "y", fill: (d) => colorOf(d.s, o.colors), r: 4.5 })));
  marks.push(Plot.tip(data, Plot.pointer({ x: "x", y: "y", title: (d) => `${d.s}\n${d.x}: ${fmt(d.y, o)}` })));
  const wide = width > 520;
  const height = o.height ?? Math.round(Math.max(250, Math.min(390, width * 0.56)));
  if (o.endLabels !== false) {
    // last point of each series, labels pushed apart so they never overlap (min ~13px)
    const gap = ((ymax - ymin) * 13) / (height - 54);
    const ends = [...d3.group(data.filter((d) => d.y != null && !Number.isNaN(d.y)), (d) => d.s)]
      .map(([s, a]) => { const p = a.reduce((m, d) => (+d.x > +m.x ? d : m)); return { s, x: p.x, y: p.y, ly: p.y }; })
      .sort((a, b) => a.ly - b.ly);
    for (let i = 1; i < ends.length; i++) if (ends[i].ly < ends[i - 1].ly + gap) ends[i].ly = ends[i - 1].ly + gap;
    const over = ends.length ? ends[ends.length - 1].ly - ymax : 0;
    if (over > 0) {
      ends.forEach((e) => (e.ly -= over));
      for (let i = ends.length - 2; i >= 0; i--) if (ends[i].ly > ends[i + 1].ly - gap) ends[i].ly = ends[i + 1].ly - gap;
    }
    marks.push(Plot.text(ends, { x: "x", y: "ly", text: "s", fill: (d) => colorOf(d.s, o.colors), dx: 6, textAnchor: "start", fontSize: wide ? 11.5 : 10, fontWeight: 600 }));
  }
  el.replaceChildren(Plot.plot({
    width, height,
    marginRight: o.endLabels === false ? 16 : wide ? (o.mr ?? 120) : (o.mrs ?? 84), marginTop: 24, marginLeft: o.ml ?? 48,
    style: { fontSize: wide ? "12px" : "10.5px" },
    x: { domain: [xmin, xmax], tickFormat: (d) => String(d), label: null, ticks: wide ? 9 : 4 },
    y: { domain: [ymin, ymax], label: o.y ?? null, grid: true, tickFormat: o.pct ? (d) => d + "%" : o.tickFormat },
    marks,
  }));
}

function scatter(el, pts, o) {
  const width = el.clientWidth || 640;
  const hl = new Set(o.highlight || []);
  el.replaceChildren(Plot.plot({
    width, height: Math.round(Math.max(280, Math.min(420, width * 0.62))), marginLeft: 50, marginBottom: 40,
    style: { fontSize: width > 520 ? "12px" : "10.5px" },
    x: { label: o.xl, grid: true, tickFormat: o.xfmt },
    y: { label: o.yl, grid: true, reverse: !!o.yrev },
    marks: [
      Plot.dot(pts.filter((d) => d[o.y] != null), { x: o.x, y: o.y, r: (d) => (hl.has(d.geo) ? 7 : 4.5), fill: (d) => (d.geo === "ES" ? COLORS["España"] : d.geo === "NL" ? COLORS["Holanda"] : "#c9ccd1"), stroke: "white" }),
      Plot.text(pts.filter((d) => d[o.y] != null), { x: o.x, y: o.y, text: "geo", dy: -10, fontSize: (d) => (hl.has(d.geo) ? 12 : 9), fontWeight: (d) => (hl.has(d.geo) ? 700 : 400), fill: (d) => (hl.has(d.geo) ? "#222" : "#999") }),
      Plot.tip(pts.filter((d) => d[o.y] != null), Plot.pointer({ x: o.x, y: o.y, title: (d) => `${d.geo}\n${o.xl}: ${fmt(d[o.x])}\n${o.yl}: ${fmt(d[o.y])}` })),
    ],
  }));
}

function legend(el, names, extra = {}) {
  el.innerHTML = names.map((n) => `<span class="lg"><i style="background:${colorOf(n, extra)}"></i>${n}</span>`).join("");
}

const drawers = [];
function register(fn) { drawers.push(fn); fn(); }
let rt;
window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => drawers.forEach((f) => f()), 200); });
