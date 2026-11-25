"""Shared chart style: government shading, shocks, deflator, save. Labels in Spanish."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT, "data", "clean")
CHARTS = os.path.join(ROOT, "charts")

# (start, end, party, label). Dates as decimal years (month/12).
GOVS = [
    (1977.5, 1982.92, "UCD", "UCD"),
    (1982.92, 1996.33, "PSOE", "González"),
    (1996.33, 2004.33, "PP", "Aznar"),
    (2004.33, 2011.97, "PSOE", "Zapatero"),
    (2011.97, 2018.42, "PP", "Rajoy"),
    (2018.42, 2027.0, "PSOE", "Sánchez"),
]
PARTY_COLOR = {"UCD": "#9e9e9e", "PSOE": "#e30613", "PP": "#1d84ce"}
SHOCKS = [(2002.0, "Euro"), (2008.7, "Crisis 2008"), (2020.2, "COVID")]

COL_ES = "#c0392b"
COL_NL = "#e67e22"
COL_CTRL = "#7f8c8d"
COL_ALT = "#2c3e50"


def setup():
    plt.rcParams.update({
        "figure.figsize": (11, 6.2), "figure.dpi": 150, "font.size": 12,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlesize": 17, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.grid": True, "grid.alpha": 0.25, "legend.frameon": False,
    })


def shade_govs(ax, lag=0.0, labels=True, alpha=0.09):
    """Background by government. lag shifts periods right (policy takes time)."""
    x0, x1 = ax.get_xlim()
    for s, e, party, name in GOVS:
        s, e = s + lag, e + lag
        if e < x0 or s > x1:
            continue
        ax.axvspan(max(s, x0), min(e, x1), color=PARTY_COLOR[party], alpha=alpha, lw=0, zorder=0)
        if labels:
            mid = (max(s, x0) + min(e, x1)) / 2
            ax.text(mid, 1.01, name, transform=ax.get_xaxis_transform(), ha="center",
                    va="bottom", fontsize=9, color=PARTY_COLOR[party])
    ax.set_xlim(x0, x1)


def mark_shocks(ax):
    x0, x1 = ax.get_xlim()
    for x, name in SHOCKS:
        if x0 <= x <= x1:
            ax.axvline(x, color="#555", lw=0.8, ls=":", zorder=1)
            ax.text(x, 0.02, f" {name}", transform=ax.get_xaxis_transform(), rotation=90,
                    fontsize=8, color="#555", va="bottom")


def cpi_annual():
    df = pd.read_csv(os.path.join(CLEAN, "common_cpi_es.csv"))
    df = df[df.variable == "cpi_annual_avg"].copy()
    df["year"] = df.date.astype(int)
    return df.set_index("year").value


def to_eur2025(values, years):
    """Nominal euros -> 2025 euros with INE CPI (annual average)."""
    cpi = cpi_annual()
    return [v * 100 / cpi.get(int(y), float("nan")) for v, y in zip(values, years)]


def finish(fig, ax, name, subtitle=None, source=None):
    if subtitle:
        ax.text(0, 1.07, subtitle, transform=ax.transAxes, fontsize=11, color="#444", va="bottom")
    if source:
        fig.text(0.01, 0.01, f"Fuente: {source}", fontsize=8.5, color="#666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    os.makedirs(CHARTS, exist_ok=True)
    path = os.path.join(CHARTS, f"{name}.png")
    fig.savefig(path)
    plt.close(fig)
    return path
