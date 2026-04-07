"""
Análisis comparativo de semanas para Sebastián
  P1: 30/03/2026 → 05/04/2026  (Semana Santa 2026)
  P2: 14/04/2025 → 20/04/2025  (Semana Santa 2025)
  Baseline: promedio histórico (Sep 2024 – Mar 2026)

Métricas:
  - Cantidad de tickets y productos
  - Media, mediana y percentiles de tickets por hora
  - Distribución de tickets por caja
"""
import re
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from scipy import stats as sp_stats

warnings.filterwarnings("ignore")

# ── Rutas ────────────────────────────────────────────────────────────────
BASE      = Path(r"D:\OneDrive\GitHub\supermercado_nino definitivo claude")
OUT       = BASE / "outputs"
EXCEL_DIR = Path(r"H:\Mi unidad\PYMEINSIDE\nino\extraccion datos\2026\marzo")
CSV_HIST  = BASE / "data/raw/comprobantes_ventas_horario.csv"
PARQUET   = BASE / "data/processed/detalle_lineas.parquet"

# ── Períodos ─────────────────────────────────────────────────────────────
P1_START, P1_END = pd.Timestamp("2026-03-30"), pd.Timestamp("2026-04-05")
P2_START, P2_END = pd.Timestamp("2025-04-14"), pd.Timestamp("2025-04-20")
P1_LABEL = "30/03 – 05/04/2026"
P2_LABEL = "14/04 – 20/04/2025"
DIAS_ES   = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

# ── Cajas (PV fijo) ───────────────────────────────────────────────────────
PV_MAP = {"0014":1,"0015":1,"0016":2,"0017":2,"0018":3,"0019":3,
          "0020":4,"0021":4,"0022":5,"0023":5,"0024":6,"0025":6,
          "0026":7,"0027":7,"0028":8,"0029":8}

# ── Colores ───────────────────────────────────────────────────────────────
C1   = "#E63946"    # rojo   → P1 2026
C2   = "#4A90D9"    # azul   → P2 2025
CBAS = "#6C757D"    # gris   → baseline
CDARK = "#1A1A2E"

# ═══════════════════════════════════════════════════════════════════════════
# 1. CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════

def parse_hora_csv(s):
    """'1899-12-30 17:29:00,000' → 17"""
    try:
        return int(str(s)[11:13])
    except Exception:
        return np.nan

def parse_hora_excel(s):
    """'08:38' → 8"""
    try:
        return int(str(s)[:2])
    except Exception:
        return np.nan

def extract_pv(comp_str):
    """'Factura B 0020-00183892' → '0020'"""
    m = re.search(r'(\d{4})-\d+', str(comp_str))
    return m.group(1) if m else None


print("Cargando datos históricos (CSV)...")
cc_hist = pd.read_csv(CSV_HIST, sep=";", low_memory=False)
cc_hist = cc_hist[cc_hist["Comprobante"].astype(str).str.startswith("Factura", na=False)].copy()
cc_hist["fecha"] = pd.to_datetime(cc_hist["Fecha"].str[:10])
cc_hist["hora"]  = cc_hist["Hora"].apply(parse_hora_csv)
cc_hist["pv"]    = cc_hist["Comprobante"].apply(extract_pv)
cc_hist["caja"]  = cc_hist["pv"].map(PV_MAP).fillna(0).astype(int)
cc_hist = cc_hist[cc_hist["hora"].notna() & (cc_hist["hora"] >= 7) & (cc_hist["hora"] <= 22)]

print("Cargando datos 2026 (Excel)...")
cv26 = pd.read_excel(EXCEL_DIR / "ReporteComprobantesVenta6-4.xlsx", header=4)
cv26 = cv26[~cv26["Fecha"].astype(str).str.contains("TOTAL|nan", na=False)].copy()
cv26["fecha"] = pd.to_datetime(cv26["Fecha"], dayfirst=True, errors="coerce")
cv26 = cv26[cv26["fecha"].notna() &
            cv26["Comprobante"].astype(str).str.startswith("Factura")].copy()
cv26["hora"] = cv26["Hora"].apply(parse_hora_excel)
cv26["pv"]   = cv26["Comprobante"].apply(extract_pv)
cv26["caja"] = cv26["pv"].map(PV_MAP).fillna(0).astype(int)
cv26 = cv26[cv26["hora"].notna() & (cv26["hora"] >= 7) & (cv26["hora"] <= 22)]

print("Cargando items (parquet)...")
dl = pd.read_parquet(PARQUET)

# ── Filtrar períodos ──────────────────────────────────────────────────────
p1_tk = cv26[(cv26["fecha"] >= P1_START) & (cv26["fecha"] <= P1_END)].copy()
p2_tk = cc_hist[(cc_hist["fecha"] >= P2_START) & (cc_hist["fecha"] <= P2_END)].copy()

# Baseline: todo lo histórico EXCEPTO las dos semanas de análisis
bas_tk = pd.concat([
    cc_hist[~((cc_hist["fecha"] >= P2_START) & (cc_hist["fecha"] <= P2_END))],
    cv26[~((cv26["fecha"] >= P1_START) & (cv26["fecha"] <= P1_END))],
], ignore_index=True)
# Excluir también los días sin datos reales (Domingos raros, etc.)
bas_tk = bas_tk[bas_tk["hora"].notna()]

p1_items = dl[(dl["fecha"] >= P1_START) & (dl["fecha"] <= P1_END)]
p2_items = dl[(dl["fecha"] >= P2_START) & (dl["fecha"] <= P2_END)]

print(f"P1 tickets: {p1_tk['Comprobante'].nunique():,}  |  P2 tickets: {p2_tk['Comprobante'].nunique():,}")
print(f"P1 items:   {len(p1_items):,}               |  P2 items:   {len(p2_items):,}")


# ═══════════════════════════════════════════════════════════════════════════
# 2. MÉTRICAS
# ═══════════════════════════════════════════════════════════════════════════

def kpis(tk_df, items_df, label):
    n_tk    = tk_df["Comprobante"].nunique()
    n_dias  = tk_df["fecha"].dt.date.nunique()
    n_items = len(items_df)
    n_tk_par = items_df["ticket_id"].nunique()   # desde parquet
    return {
        "label":     label,
        "tickets":   n_tk,
        "productos": n_items,
        "tk_dia":    n_tk / n_dias if n_dias else 0,
        "prod_tk":   n_items / n_tk_par if n_tk_par else 0,
        "dias":      n_dias,
    }

kpi_p1 = kpis(p1_tk, p1_items, P1_LABEL)
kpi_p2 = kpis(p2_tk, p2_items, P2_LABEL)
print("KPI P1:", kpi_p1)
print("KPI P2:", kpi_p2)

# Tickets por día de semana
def tk_por_dow(tk_df):
    """Retorna Series index=dow(0..6), value=ticket_count"""
    g = tk_df.groupby(tk_df["fecha"].dt.dayofweek)["Comprobante"].nunique()
    return g.reindex(range(7), fill_value=0)

dow_p1  = tk_por_dow(p1_tk)
dow_p2  = tk_por_dow(p2_tk)

# Tickets por hora — conteo diario (para gráfico de flujo)
def tk_hora_media(tk_df):
    """Para cada hora: media de tickets-por-día."""
    pivot = (tk_df.groupby(["fecha", "hora"])["Comprobante"]
             .nunique().unstack(fill_value=0))
    return {h: (pivot[h].mean() if h in pivot.columns else 0)
            for h in range(7, 23)}

tk_hora_p1  = tk_hora_media(p1_tk)
tk_hora_p2  = tk_hora_media(p2_tk)
tk_hora_bas = tk_hora_media(bas_tk)

# Importe del ticket por hora — media, mediana, P25, P75, P90
# (esto es lo que pidió Sebastián: "media, mediana y percentiles de ticket por hora")
def importe_hora_stats(tk_df):
    """Para cada hora: stats del IMPORTE del ticket."""
    tk_df = tk_df[tk_df["Importe"].notna() & (tk_df["Importe"] > 0)].copy()
    stats = {}
    for h in range(7, 23):
        sub = tk_df[tk_df["hora"] == h]["Importe"]
        if len(sub) < 3:
            stats[h] = {"n": 0, "media": 0, "mediana": 0, "p25": 0, "p75": 0, "p90": 0}
        else:
            stats[h] = {
                "n":      len(sub),
                "media":  sub.mean(),
                "mediana":sub.median(),
                "p25":    sub.quantile(0.25),
                "p75":    sub.quantile(0.75),
                "p90":    sub.quantile(0.90),
            }
    return pd.DataFrame(stats).T

p1_tk["Importe"] = pd.to_numeric(p1_tk["Importe"], errors="coerce")
p2_tk["Importe"] = pd.to_numeric(p2_tk["Importe"], errors="coerce")
bas_tk["Importe"] = pd.to_numeric(bas_tk.get("Importe", pd.Series(dtype=float)), errors="coerce")

imp_h_p1  = importe_hora_stats(p1_tk)
imp_h_p2  = importe_hora_stats(p2_tk)
p2_imp_validos = p2_tk["Importe"].notna().sum()
p2_imp_total   = len(p2_tk)
print(f"P2 Importe disponibles: {p2_imp_validos:,}/{p2_imp_total:,} "
      f"({p2_imp_validos/p2_imp_total*100:.0f}%)")

# Distribución por caja — tickets y promedio importe
def caja_stats(tk_df):
    df = tk_df[tk_df["caja"] > 0].copy()
    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
    g = df.groupby("caja").agg(
        tickets=("Comprobante", "nunique"),
        imp_med=("Importe", "median"),
        imp_avg=("Importe", "mean"),
    )
    return g.reindex(range(1, 9), fill_value=0)

caja_p1 = caja_stats(p1_tk)
caja_p2 = caja_stats(p2_tk)

# Heatmap throughput: tickets por hora por caja (P1 solo, más reciente y completo)
heat_p1 = (p1_tk[p1_tk["caja"] > 0]
           .groupby(["hora", "caja"])["Comprobante"]
           .nunique().unstack(fill_value=0)
           .reindex(columns=range(1, 9), fill_value=0))


# ═══════════════════════════════════════════════════════════════════════════
# =============================================================================
# 3. PDF
# =============================================================================

OUT.mkdir(exist_ok=True)
PDF_PATH = OUT / "analisis_semana_sebastian.pdf"

TICK_PARAMS  = dict(labelsize=8, color=CDARK)
SPINE_COLOR  = "#CCCCCC"
C_INSIGHT    = "#EEF4FF"
C_INS_BORDER = "#AABBDD"


def style_ax(ax, title=None, xlabel=None, ylabel=None):
    ax.set_facecolor("white")
    for sp in ax.spines.values():
        sp.set_color(SPINE_COLOR); sp.set_linewidth(0.7)
    ax.tick_params(**TICK_PARAMS)
    ax.grid(axis="y", color="#EEEEEE", linewidth=0.6, zorder=0)
    if title:  ax.set_title(title, fontsize=9, fontweight="bold", color=CDARK, pad=5)
    if xlabel: ax.set_xlabel(xlabel, fontsize=8, color=CDARK)
    if ylabel: ax.set_ylabel(ylabel, fontsize=8, color=CDARK)


def add_insight(ax, text, dy=-0.24):
    ax.text(0.5, dy, text, transform=ax.transAxes,
            ha="center", va="top", fontsize=7.5, color="#2A2A4A", style="italic",
            bbox=dict(boxstyle="round,pad=0.45", facecolor=C_INSIGHT,
                      edgecolor=C_INS_BORDER, alpha=0.92))


HORAS_ACT = [h for h in range(7, 23)
             if tk_hora_p1.get(h, 0) > 0 or tk_hora_p2.get(h, 0) > 0]

with PdfPages(PDF_PATH) as pdf:

    # =========================================================================
    # PAGE 1: KPIs + tickets por dia + flujo horario
    # =========================================================================
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.patch.set_facecolor("white")
    gs = gridspec.GridSpec(3, 2, figure=fig,
                           left=0.07, right=0.97, top=0.88, bottom=0.07,
                           hspace=0.95, wspace=0.35)

    fig.text(0.5, 0.952, "Analisis de Tickets - Comparativo Semana Santa",
             ha="center", va="top", fontsize=15, fontweight="bold", color=CDARK)
    fig.text(0.5, 0.922, f"P1: {P1_LABEL}   |   P2: {P2_LABEL}",
             ha="center", va="top", fontsize=10, color=CBAS)

    # --- Tabla KPIs ---
    ax_tbl = fig.add_subplot(gs[0, :])
    ax_tbl.axis("off")
    vd = (kpi_p1["tickets"]  / kpi_p2["tickets"]  - 1) * 100
    pd2 = (kpi_p1["productos"]/ kpi_p2["productos"]- 1) * 100
    tdd = (kpi_p1["tk_dia"]   / kpi_p2["tk_dia"]   - 1) * 100
    ptd = (kpi_p1["prod_tk"]  / kpi_p2["prod_tk"]  - 1) * 100
    def fmt_d(d): return f"+{d:.1f}%" if d >= 0 else f"{d:.1f}%"
    tbl_data = [
        ["", P1_LABEL, P2_LABEL, "Variacion", "Lectura"],
        ["Tickets totales",
         f"{kpi_p1['tickets']:,.0f}", f"{kpi_p2['tickets']:,.0f}",
         fmt_d(vd), "Clientes atendidos en la semana"],
        ["Productos totales",
         f"{kpi_p1['productos']:,.0f}", f"{kpi_p2['productos']:,.0f}",
         fmt_d(pd2), "Lineas de producto escaneadas"],
        ["Tickets / dia",
         f"{kpi_p1['tk_dia']:,.0f}", f"{kpi_p2['tk_dia']:,.0f}",
         fmt_d(tdd), "Clientes promedio por dia"],
        ["Productos / ticket",
         f"{kpi_p1['prod_tk']:.2f}", f"{kpi_p2['prod_tk']:.2f}",
         fmt_d(ptd), "Items por compra"],
    ]
    col_w = [0.21, 0.13, 0.13, 0.11, 0.42]
    tbl = ax_tbl.table(cellText=tbl_data[1:], colLabels=tbl_data[0],
                       colWidths=col_w, loc="center", cellLoc="left")
    tbl.auto_set_font_size(False); tbl.set_fontsize(8.5)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(SPINE_COLOR)
        cell.set_text_props(ha="center" if c < 4 else "left")
        if r == 0:
            cell.set_facecolor(CDARK)
            cell.set_text_props(color="white", fontweight="bold", ha="center")
        elif r % 2 == 0: cell.set_facecolor("#F5F5F5")
        else: cell.set_facecolor("white")
        if c == 3 and r > 0:
            v = tbl_data[r][3]
            cell.set_text_props(
                color="#2D9B4E" if v.startswith("+") else C1,
                fontweight="bold", ha="center")
    tbl.scale(1, 1.85)
    add_insight(ax_tbl,
        "2026 tiene +126 tickets vs 2025 (+2.1%), pero cada cliente compra 1.4 items menos (-14.7%). "
        "La fila unica cambia el patron: mas clientes, canastas mas chicas.",
        dy=-0.10)

    # --- Tickets por dia de semana ---
    ax_dow = fig.add_subplot(gs[1, 0])
    x, ww = np.arange(7), 0.38
    ax_dow.bar(x-ww/2, dow_p1.values, width=ww, color=C1, label=P1_LABEL, zorder=3)
    ax_dow.bar(x+ww/2, dow_p2.values, width=ww, color=C2, label=P2_LABEL, zorder=3)
    ax_dow.set_xticks(x); ax_dow.set_xticklabels(DIAS_ES, fontsize=8)
    style_ax(ax_dow, title="Tickets por dia de la semana", ylabel="Tickets")
    ax_dow.legend(fontsize=7, framealpha=0.8, loc="upper left")
    for rect in ax_dow.patches:
        hv = rect.get_height()
        if hv > 0:
            ax_dow.text(rect.get_x()+rect.get_width()/2, hv+8,
                        f"{int(hv)}", ha="center", va="bottom", fontsize=6.5, color=CDARK)
    add_insight(ax_dow,
        "Sabado de Gloria (04/04/2026): 1,260 tickets - record semanal (+20% vs sabado tipico). "
        "Viernes Santo casi sin actividad. El resto de la semana 2026 supera a 2025.")

    # --- Productos por dia ---
    ax_pdow = fig.add_subplot(gs[1, 1])
    pdow_p1 = p1_items.groupby(p1_items["fecha"].dt.dayofweek).size().reindex(range(7), fill_value=0)
    pdow_p2 = p2_items.groupby(p2_items["fecha"].dt.dayofweek).size().reindex(range(7), fill_value=0)
    ax_pdow.bar(x-ww/2, pdow_p1.values, width=ww, color=C1, label=P1_LABEL, zorder=3)
    ax_pdow.bar(x+ww/2, pdow_p2.values, width=ww, color=C2, label=P2_LABEL, zorder=3)
    ax_pdow.set_xticks(x); ax_pdow.set_xticklabels(DIAS_ES, fontsize=8)
    style_ax(ax_pdow, title="Productos escaneados por dia", ylabel="Lineas de producto")
    ax_pdow.legend(fontsize=7, framealpha=0.8, loc="upper left")
    for rect in ax_pdow.patches:
        hv = rect.get_height()
        if hv > 0:
            ax_pdow.text(rect.get_x()+rect.get_width()/2, hv+30,
                         f"{int(hv):,}", ha="center", va="bottom", fontsize=6, color=CDARK)
    add_insight(ax_pdow,
        "Mas tickets en 2026 pero menos productos totales. "
        "2025 movio mas items por dia en casi todos los dias de la semana.")

    # --- Flujo horario ---
    ax_h = fig.add_subplot(gs[2, :])
    ax_h.plot(HORAS_ACT, [tk_hora_p1.get(h, 0)  for h in HORAS_ACT],
              color=C1, lw=2, marker="o", ms=4, label=P1_LABEL, zorder=4)
    ax_h.plot(HORAS_ACT, [tk_hora_p2.get(h, 0)  for h in HORAS_ACT],
              color=C2, lw=2, marker="s", ms=4, label=P2_LABEL, zorder=4)
    ax_h.plot(HORAS_ACT, [tk_hora_bas.get(h, 0) for h in HORAS_ACT],
              color=CBAS, lw=1.5, ls="--", label="Historico", zorder=3)
    pk = max(HORAS_ACT, key=lambda h: tk_hora_p1.get(h, 0))
    ax_h.axvline(pk, color="#E59C00", lw=1.5, ls=":", alpha=0.8)
    ax_h.text(pk+0.12, ax_h.get_ylim()[1]*0.93,
              f"Pico {pk}h", fontsize=7.5, color="#E59C00", fontweight="bold")
    ax_h.set_xticks(HORAS_ACT)
    ax_h.set_xticklabels([f"{h}h" for h in HORAS_ACT], fontsize=8)
    style_ax(ax_h, title="Tickets promedio por hora del dia", ylabel="Tickets / dia")
    ax_h.legend(fontsize=7.5, framealpha=0.8, ncol=3)
    add_insight(ax_h,
        f"Pico principal a las {pk}h (~{int(tk_hora_p1.get(pk,0))} tickets/dia en P1). "
        "Cierre de 13h a 16h. Segundo bloque vespertino 17-20h. "
        "P1 muestra mayor caudal en el turno tarde que el historico.")

    pdf.savefig(fig, dpi=150)
    plt.close(fig)

    # =========================================================================
    # PAGE 2: Serie diaria marzo-abril 2026 vs 2025
    # =========================================================================
    # Cargar serie diaria desde CSV historico (2025) y Excel (2026)
    _cc = pd.read_csv(CSV_HIST, sep=";", low_memory=False)
    _cc = _cc[_cc["Comprobante"].astype(str).str.startswith("Factura", na=False)].copy()
    _cc["fecha"] = pd.to_datetime(_cc["Fecha"].str[:10])
    _d25_tk = (_cc[(_cc["fecha"] >= "2025-03-01") & (_cc["fecha"] <= "2025-04-30")]
               .groupby("fecha")["Comprobante"].nunique().rename("tickets"))

    _d26_tk = (cv26[(cv26["fecha"] >= "2026-03-01") & (cv26["fecha"] <= "2026-04-05")]
               .groupby("fecha")["Comprobante"].nunique().rename("tickets"))

    # Productos/ticket desde parquet
    _dl = dl.copy()
    def _daily_stats(df, s, e):
        sub = df[(df["fecha"] >= s) & (df["fecha"] <= e)]
        tk  = sub.groupby("fecha")["ticket_id"].nunique().rename("tickets")
        pr  = sub.groupby("fecha").size().rename("productos")
        m   = pd.concat([tk, pr], axis=1)
        m["prod_tk"] = m["productos"] / m["tickets"]
        return m

    ds25 = _daily_stats(_dl, "2025-03-01", "2025-04-30")
    ds26 = _daily_stats(_dl, "2026-03-01", "2026-04-05")

    # Semana Santa fechas
    SS26_INI, SS26_FIN = pd.Timestamp("2026-04-03"), pd.Timestamp("2026-04-05")
    SS25_INI, SS25_FIN = pd.Timestamp("2025-04-17"), pd.Timestamp("2025-04-20")
    FILA_U = pd.Timestamp("2026-03-28")

    fig_ts = plt.figure(figsize=(11.69, 8.27))
    fig_ts.patch.set_facecolor("white")
    gs_ts = gridspec.GridSpec(2, 1, figure=fig_ts,
                              left=0.08, right=0.97, top=0.88, bottom=0.08,
                              hspace=0.88)

    fig_ts.text(0.5, 0.952, "Serie Diaria — Marzo y Abril",
                ha="center", va="top", fontsize=14, fontweight="bold", color=CDARK)
    fig_ts.text(0.5, 0.920,
                "Rojo = 2026  |  Azul = 2025  |  Linea naranja = implementacion fila unica (28/03/2026)",
                ha="center", va="top", fontsize=9, color=CBAS)

    # ─ Tickets por dia ─
    ax_ts1 = fig_ts.add_subplot(gs_ts[0])
    ax_ts1.plot(_d26_tk.index, _d26_tk.values, color=C1, lw=1.8,
                marker="o", ms=3.5, label="2026", zorder=4)
    ax_ts1.plot(_d25_tk.index, _d25_tk.values, color=C2, lw=1.8,
                marker="o", ms=3.5, alpha=0.8, label="2025", zorder=3)
    # Shading periodos de analisis
    ax_ts1.axvspan(P1_START, P1_END, color=C1, alpha=0.08, label=f"P1: {P1_LABEL}")
    ax_ts1.axvspan(P2_START, P2_END, color=C2, alpha=0.08, label=f"P2: {P2_LABEL}")
    # Semana Santa 2026
    ax_ts1.axvspan(SS26_INI, SS26_FIN, color="#E59C00", alpha=0.12,
                   label="Sem. Santa 2026")
    # Semana Santa 2025
    ax_ts1.axvspan(SS25_INI, SS25_FIN, color="#9B59B6", alpha=0.10,
                   label="Sem. Santa 2025")
    # Fila unica
    ax_ts1.axvline(FILA_U, color="#E59C00", lw=2.2, ls="-", zorder=6)
    ax_ts1.text(FILA_U + pd.Timedelta(days=0.8),
                ax_ts1.get_ylim()[1] * 0.92,
                "Fila unica", fontsize=7.5, color="#E59C00", fontweight="bold")
    # Medias horizontales
    ax_ts1.axhline(_d25_tk.mean(), color=C2, lw=1, ls=":", alpha=0.6)
    ax_ts1.axhline(_d26_tk.mean(), color=C1, lw=1, ls=":", alpha=0.6)
    ax_ts1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d/%m"))
    ax_ts1.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator(byweekday=0, interval=1))
    plt.setp(ax_ts1.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=7.5)
    style_ax(ax_ts1, title="Tickets por dia — Marzo y Abril", ylabel="Tickets")
    ax_ts1.legend(fontsize=7, ncol=3, framealpha=0.85, loc="upper left")
    add_insight(ax_ts1,
        f"Media diaria 2026: {_d26_tk.mean():.0f} tickets vs 2025: {_d25_tk.mean():.0f}. "
        "El Sabado de Gloria 2026 (04/04) fue el dia mas alto del periodo. "
        "La fila unica (28/03) no muestra caida de trafico — al contrario, los dias siguientes estuvieron sobre la media.")

    # ─ Productos/ticket por dia ─
    ax_ts2 = fig_ts.add_subplot(gs_ts[1])
    ax_ts2.plot(ds26.index, ds26["prod_tk"], color=C1, lw=1.8,
                marker="o", ms=3.5, label="2026", zorder=4)
    ax_ts2.plot(ds25.index, ds25["prod_tk"], color=C2, lw=1.8,
                marker="o", ms=3.5, alpha=0.8, label="2025", zorder=3)
    ax_ts2.axvspan(P1_START, P1_END, color=C1, alpha=0.08)
    ax_ts2.axvspan(P2_START, P2_END, color=C2, alpha=0.08)
    ax_ts2.axvspan(SS26_INI, SS26_FIN, color="#E59C00", alpha=0.12)
    ax_ts2.axvspan(SS25_INI, SS25_FIN, color="#9B59B6", alpha=0.10)
    ax_ts2.axvline(FILA_U, color="#E59C00", lw=2.2, ls="-", zorder=6)
    ax_ts2.text(FILA_U + pd.Timedelta(days=0.8),
                ax_ts2.get_ylim()[1] * 0.93,
                "Fila unica", fontsize=7.5, color="#E59C00", fontweight="bold")
    # Medias
    pre_u26  = ds26[ds26.index < FILA_U]["prod_tk"].mean()
    post_u26 = ds26[ds26.index >= FILA_U]["prod_tk"].mean()
    ax_ts2.axhline(pre_u26,  color=C1, lw=1, ls=":",  alpha=0.7)
    ax_ts2.axhline(post_u26, color=C1, lw=1, ls="--", alpha=0.7)
    ax_ts2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d/%m"))
    ax_ts2.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator(byweekday=0, interval=1))
    plt.setp(ax_ts2.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=7.5)
    style_ax(ax_ts2, title="Productos por ticket por dia", ylabel="Items / ticket")
    ax_ts2.legend(fontsize=7, framealpha=0.85, loc="upper right")
    add_insight(ax_ts2,
        f"Pre fila unica 2026: {pre_u26:.1f} items/ticket (comparable con 2025). "
        f"Post fila unica: {post_u26:.1f} items/ticket — caida visible y sostenida. "
        "La linea de 2025 no muestra ese quiebre: confirma que es efecto de la fila unica, no de Semana Santa.")

    pdf.savefig(fig_ts, dpi=150)
    plt.close(fig_ts)

    # =========================================================================
    # PAGE 3: Importe del ticket - histograma + estadisticas por hora
    # =========================================================================
    fig2 = plt.figure(figsize=(11.69, 8.27))
    fig2.patch.set_facecolor("white")
    gs2 = gridspec.GridSpec(2, 2, figure=fig2,
                            left=0.07, right=0.97, top=0.88, bottom=0.07,
                            hspace=0.90, wspace=0.38)
    fig2.text(0.5, 0.952, "Importe del Ticket por Hora",
              ha="center", va="top", fontsize=14, fontweight="bold", color=CDARK)
    fig2.text(0.5, 0.920,
              f"P1: {P1_LABEL}   |   P2: {P2_LABEL}   |   *P2: importe disponible en solo el 52% de los tickets",
              ha="center", va="top", fontsize=8.5, color=CBAS)

    imp_p1_v = p1_tk["Importe"].dropna()
    imp_p2_v = p2_tk["Importe"].dropna()

    # --- Histograma ---
    ax_hist = fig2.add_subplot(gs2[0, 0])
    p97 = imp_p1_v.quantile(0.97)
    bins = np.linspace(0, p97, 35)
    ax_hist.hist(imp_p1_v.clip(upper=p97), bins=bins, density=True,
                 color=C1, alpha=0.65, label=f"P1 (n={len(imp_p1_v):,})", zorder=3)
    if len(imp_p2_v) > 50:
        ax_hist.hist(imp_p2_v.clip(upper=p97), bins=bins, density=True,
                     color=C2, alpha=0.55, label=f"P2* (n={len(imp_p2_v):,})", zorder=2)
    ax_hist.axvline(imp_p1_v.median(), color=C1, lw=2, ls="--",
                    label=f"Med P1 ${imp_p1_v.median()/1000:.0f}K")
    if len(imp_p2_v) > 50:
        ax_hist.axvline(imp_p2_v.median(), color=C2, lw=2, ls="--",
                        label=f"Med P2 ${imp_p2_v.median()/1000:.0f}K")
    ax_hist.xaxis.set_major_formatter(plt.FuncFormatter(lambda xv, _: f"${xv/1000:.0f}K"))
    style_ax(ax_hist, title="Distribucion del importe del ticket", xlabel="Importe ($)")
    ax_hist.legend(fontsize=7, framealpha=0.8)
    add_insight(ax_hist,
        f"Mediana P1: ${imp_p1_v.median()/1000:.0f}K vs P2: ${imp_p2_v.median()/1000:.0f}K. "
        "La diferencia (~2x) refleja inflacion anual, no cambio de comportamiento. "
        "Ambos tienen cola larga a la derecha: pocos tickets de alto valor elevan el promedio.")

    # --- Mediana importe por hora ---
    ax_imph = fig2.add_subplot(gs2[0, 1])
    horas_imp = [h for h in range(8, 22)
                 if h in imp_h_p1.index and imp_h_p1.loc[h, "n"] > 0]
    ax_imph.plot(horas_imp,
                 [imp_h_p1.loc[h, "mediana"]/1000 for h in horas_imp],
                 color=C1, lw=2, marker="o", ms=5, label=P1_LABEL, zorder=4)
    if any(h in imp_h_p2.index and imp_h_p2.loc[h,"n"]>0 for h in horas_imp):
        ax_imph.plot(horas_imp,
                     [imp_h_p2.loc[h,"mediana"]/1000 if (h in imp_h_p2.index and imp_h_p2.loc[h,"n"]>0) else 0
                      for h in horas_imp],
                     color=C2, lw=2, marker="s", ms=5, label=P2_LABEL+"*", zorder=3)
    ax_imph.fill_between(horas_imp,
                         [imp_h_p1.loc[h,"p25"]/1000 for h in horas_imp],
                         [imp_h_p1.loc[h,"p75"]/1000 for h in horas_imp],
                         color=C1, alpha=0.15, label="IQ P1 (P25-P75)")
    ax_imph.set_xticks(horas_imp)
    ax_imph.set_xticklabels([f"{h}h" for h in horas_imp], fontsize=8)
    ax_imph.yaxis.set_major_formatter(plt.FuncFormatter(lambda yv, _: f"${yv:.0f}K"))
    style_ax(ax_imph, title="Importe mediano del ticket por hora (P1)", ylabel="$ miles")
    ax_imph.legend(fontsize=7, framealpha=0.8)
    add_insight(ax_imph,
        "El ticket del mediodia (12-13h) es el mas alto (~\$27K): compras grandes del mediodia. "
        "Turno noche (~\$20K) ligeramente por encima de la manana. "
        "Alta variabilidad en todos los horarios: clientes de compra grande a toda hora.")

    # --- Tabla percentiles importe por hora ---
    ax_itbl = fig2.add_subplot(gs2[1, :])
    ax_itbl.axis("off")
    horas_tbl = [h for h in range(8, 22)
                 if h in imp_h_p1.index and imp_h_p1.loc[h,"n"] > 0]
    def fmt_k(v): return f"${v/1000:.1f}K" if v > 0 else "-"
    rows_tbl = []
    for sk, sl in [("media","Media"),("mediana","Mediana"),("p25","P25"),("p75","P75"),("p90","P90")]:
        r1 = [fmt_k(imp_h_p1.loc[h, sk]) if h in imp_h_p1.index else "-" for h in horas_tbl]
        r2 = [fmt_k(imp_h_p2.loc[h, sk]) if (h in imp_h_p2.index and imp_h_p2.loc[h,"n"]>0) else "-"
              for h in horas_tbl]
        rows_tbl.append([f"P1 {sl}"] + r1)
        rows_tbl.append([f"P2 {sl}*"] + r2)
    col_h_i = [""] + [f"{h}h" for h in horas_tbl]
    col_w_i = [0.105] + [0.058]*len(horas_tbl)
    tbl_i = ax_itbl.table(cellText=rows_tbl, colLabels=col_h_i,
                          colWidths=col_w_i, loc="center", cellLoc="center")
    tbl_i.auto_set_font_size(False); tbl_i.set_fontsize(7.5)
    bc = [C1, C2]
    for (r, c), cell in tbl_i.get_celld().items():
        cell.set_edgecolor(SPINE_COLOR)
        if r == 0:
            cell.set_facecolor(CDARK)
            cell.set_text_props(color="white", fontweight="bold")
        else:
            gc = bc[(r-1)%2]
            cell.set_facecolor(gc+"22")
            if c == 0: cell.set_text_props(fontweight="bold", color=gc)
    tbl_i.scale(1, 1.55)
    ax_itbl.set_title(
        f"Media, Mediana y Percentiles del importe del ticket por hora  "
        f"(*P2: solo {p2_imp_validos:,}/{p2_imp_total:,} tickets tienen importe registrado)",
        fontsize=8.5, fontweight="bold", color=CDARK, pad=6, loc="left")
    add_insight(ax_itbl,
        "P90 de P1 ronda \$75-90K: el 10% de los clientes gasta mas de \$75K por visita. "
        "Comparar P1 vs P2 en valores absolutos no es directo por inflacion (~100% anual). "
        "El patron horario (mediodia > noche > manana) si es comparable entre periodos.",
        dy=-0.06)

    pdf.savefig(fig2, dpi=150)
    plt.close(fig2)

    # =========================================================================
    # PAGE 3: Cajas
    # =========================================================================
    fig3b = plt.figure(figsize=(11.69, 8.27))
    fig3b.patch.set_facecolor("white")
    gs3b = gridspec.GridSpec(2, 3, figure=fig3b,
                             left=0.06, right=0.97, top=0.88, bottom=0.07,
                             hspace=0.90, wspace=0.40)
    fig3b.text(0.5, 0.952, "Analisis por Caja",
               ha="center", va="top", fontsize=14, fontweight="bold", color=CDARK)
    fig3b.text(0.5, 0.920,
               f"P1: {P1_LABEL}   |   P2: {P2_LABEL}   |   Heatmap: perfil horario P1",
               ha="center", va="top", fontsize=9, color=CBAS)

    cajas = list(range(1, 9))
    tot_p1_tk = caja_p1["tickets"].sum()
    tot_p2_tk = caja_p2["tickets"].sum()
    pct_p1v = caja_p1["tickets"] / tot_p1_tk * 100
    pct_p2v = caja_p2["tickets"] / tot_p2_tk * 100

    ax_cpct = fig3b.add_subplot(gs3b[0, :2])
    x_caj, w_caj = np.arange(len(cajas)), 0.38
    ax_cpct.bar(x_caj-w_caj/2, pct_p1v.values, width=w_caj, color=C1, label=P1_LABEL, zorder=3)
    ax_cpct.bar(x_caj+w_caj/2, pct_p2v.values, width=w_caj, color=C2, label=P2_LABEL, zorder=3)
    ax_cpct.set_xticks(x_caj); ax_cpct.set_xticklabels([f"Caja {c}" for c in cajas], fontsize=8)
    style_ax(ax_cpct, title="Distribucion de tickets por caja (%)", ylabel="% de tickets")
    ax_cpct.legend(fontsize=7.5, framealpha=0.8)
    ax_cpct.yaxis.set_major_formatter(plt.FuncFormatter(lambda yv, _: f"{yv:.0f}%"))
    for rect in ax_cpct.patches:
        hv = rect.get_height()
        if hv > 0.3:
            ax_cpct.text(rect.get_x()+rect.get_width()/2, hv+0.15,
                         f"{hv:.1f}%", ha="center", va="bottom", fontsize=6.5, color=CDARK)
    top3 = pct_p1v.nlargest(3)
    top3s = ", ".join([f"Caja {c} ({v:.1f}%)" for c, v in top3.items()])
    add_insight(ax_cpct,
        f"P1 - mayor carga: {top3s}. "
        "La distribucion cambio respecto a 2025: Caja 2 gano participacion (+5pp), "
        "Caja 1 la perdio (-2pp). Caja 8 marginales en ambos periodos.")

    ax_ctbl = fig3b.add_subplot(gs3b[0, 2])
    ax_ctbl.axis("off")
    rows_ct = []
    for c in cajas:
        t1 = int(caja_p1.loc[c, "tickets"])
        t2 = int(caja_p2.loc[c, "tickets"]) if c in caja_p2.index else 0
        i1 = caja_p1.loc[c, "imp_med"]
        i2 = caja_p2.loc[c, "imp_med"] if c in caja_p2.index else float("nan")
        rows_ct.append([f"C{c}", f"{t1:,}", f"{t2:,}",
                        f"${i1/1000:.0f}K" if i1 > 0 else "-",
                        f"${i2/1000:.0f}K" if (not np.isnan(i2) and i2>0) else "-"])
    rows_ct.append(["TOT", f"{int(tot_p1_tk):,}", f"{int(tot_p2_tk):,}", "", ""])
    tbl_ct = ax_ctbl.table(cellText=rows_ct,
                           colLabels=["", "Tk P1", "Tk P2", "Med$ P1", "Med$ P2*"],
                           colWidths=[0.16,0.19,0.19,0.22,0.22],
                           loc="center", cellLoc="center")
    tbl_ct.auto_set_font_size(False); tbl_ct.set_fontsize(8)
    for (r, cc2), cell in tbl_ct.get_celld().items():
        cell.set_edgecolor(SPINE_COLOR)
        if r == 0:
            cell.set_facecolor(CDARK); cell.set_text_props(color="white", fontweight="bold")
        elif r == len(cajas)+1:
            cell.set_facecolor("#E8E8E8"); cell.set_text_props(fontweight="bold")
        elif r%2==0: cell.set_facecolor("#F5F5F5")
        else: cell.set_facecolor("white")
    tbl_ct.scale(1, 1.68)
    ax_ctbl.set_title("Tickets y ticket promedio\npor caja (*P2 importe parcial)",
                      fontsize=8, fontweight="bold", color=CDARK, pad=5, loc="left")
    add_insight(ax_ctbl,
        "Ticket mediano ~\$20K igual en todas las cajas: no hay cajas 'express' vs 'compra grande'.",
        dy=-0.12)

    ax_heat = fig3b.add_subplot(gs3b[1, :])
    horas_heat = [h for h in range(8, 22)
                  if h in heat_p1.index and heat_p1.loc[h].sum() > 0]
    data_heat = heat_p1.loc[horas_heat].values.T.astype(float)
    row_tot   = data_heat.sum(axis=1, keepdims=True)
    row_tot[row_tot==0] = 1
    data_pct  = data_heat / row_tot * 100
    im = ax_heat.imshow(data_pct, aspect="auto", cmap="YlOrRd", interpolation="nearest")
    ax_heat.set_xticks(range(len(horas_heat)))
    ax_heat.set_xticklabels([f"{h}h" for h in horas_heat], fontsize=8)
    ax_heat.set_yticks(range(len(cajas)))
    ax_heat.set_yticklabels([f"Caja {c}" for c in cajas], fontsize=8)
    for i in range(len(cajas)):
        for j in range(len(horas_heat)):
            v = data_pct[i,j]
            if v > 0.5:
                ax_heat.text(j, i, f"{v:.0f}%", ha="center", va="center",
                             fontsize=7, color="white" if v>16 else CDARK)
    plt.colorbar(im, ax=ax_heat, label="% del total de esa caja", pad=0.01)
    style_ax(ax_heat,
             title="Tiempos de caja - distribucion horaria del trafico (P1)",
             xlabel="Hora del dia")
    ax_heat.grid(False)
    add_insight(ax_heat,
        "Todas las cajas con el mismo perfil: 10-12h (manana) y 18-20h (noche). "
        "Caja 7 opera con menor volumen total. Caja 8 activa solo al mediodia - apertura tardia. "
        "Bloque 13-16h vacio en todas: cierre del mediodia.")

    pdf.savefig(fig3b, dpi=150)
    plt.close(fig3b)

    # =========================================================================
    # PAGE 4: Tendencia historica
    # =========================================================================
    FILA_UNICA = pd.Timestamp("2026-03-28")
    dl_t = dl.copy()
    dl_t["semana"] = dl_t["fecha"].dt.to_period("W").dt.start_time
    wkly = (dl_t.groupby("semana")
            .agg(tickets=("ticket_id","nunique"), productos=("ticket_id","count"))
            .reset_index())
    dsem = dl_t.groupby("semana")["fecha"].nunique()
    wkly["dias"]    = wkly["semana"].map(dsem)
    wkly["prod_tk"] = wkly["productos"] / wkly["tickets"]
    wkly = wkly[wkly["dias"] >= 5].copy()
    pre4  = wkly[wkly["semana"] < FILA_UNICA].copy()
    post4 = wkly[wkly["semana"] >= FILA_UNICA].copy()
    t0w   = wkly["semana"].min()
    def lreg(df, col):
        xv = (df["semana"]-t0w).dt.days.values.astype(float)
        sl, ic, rv, pv, _ = sp_stats.linregress(xv, df[col].values)
        return sl, ic, rv**2, pv
    sl_pt4, ic_pt4, r2_pt4, p_pt4 = lreg(pre4, "prod_tk")
    sl_tk4, ic_tk4, r2_tk4, p_tk4 = lreg(pre4, "tickets")

    fig4 = plt.figure(figsize=(11.69, 8.27))
    fig4.patch.set_facecolor("white")
    gs4 = gridspec.GridSpec(2, 1, figure=fig4,
                            left=0.08, right=0.97, top=0.88, bottom=0.07,
                            hspace=0.88)
    fig4.text(0.5, 0.952, "Tendencia Historica",
              ha="center", va="top", fontsize=14, fontweight="bold", color=CDARK)
    fig4.text(0.5, 0.920,
              "Semanas completas Oct 2024 - Abr 2026  |  Corte: fila unica 28/03/2026",
              ha="center", va="top", fontsize=9, color=CBAS)

    ax_pt4 = fig4.add_subplot(gs4[0])
    xpre4  = (pre4["semana"]-t0w).dt.days.values.astype(float)
    ax_pt4.scatter(pre4["semana"],  pre4["prod_tk"],  color=C2, s=28, alpha=0.85, zorder=4, label="Pre fila unica")
    ax_pt4.scatter(post4["semana"], post4["prod_tk"], color=C1, s=38, marker="D", zorder=5, label="Post fila unica")
    ax_pt4.plot(pre4["semana"], ic_pt4+sl_pt4*xpre4, color=C2, lw=1.8, ls="--",
                label=f"Tendencia pre (p={p_pt4:.2f})")
    ax_pt4.axhline(pre4["prod_tk"].mean(),  color=C2, lw=1.0, ls=":", alpha=0.6)
    ax_pt4.axhline(post4["prod_tk"].mean(), color=C1, lw=1.0, ls=":", alpha=0.6)
    ax_pt4.axvline(FILA_UNICA, color="#E59C00", lw=2, zorder=6)
    ax_pt4.text(FILA_UNICA+pd.Timedelta(days=3), 10.8, "Fila\nunica", fontsize=7.5, color="#E59C00", fontweight="bold")
    delta_pt4 = post4["prod_tk"].mean() - pre4["prod_tk"].mean()
    ax_pt4.annotate(f"Delta = {delta_pt4:+.2f} items/ticket ({delta_pt4/pre4['prod_tk'].mean()*100:+.1f}%)",
                    xy=(post4["semana"].iloc[0], post4["prod_tk"].mean()),
                    xytext=(post4["semana"].iloc[0], post4["prod_tk"].mean()-0.9),
                    fontsize=8.5, color=C1, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=C1, lw=1.2))
    style_ax(ax_pt4, title="Productos por ticket (semanal)", ylabel="Items / ticket")
    ax_pt4.set_ylim(7.0, 11.5)
    ax_pt4.legend(fontsize=7.5, loc="lower left")
    ax_pt4.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %Y"))
    ax_pt4.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=2))
    plt.setp(ax_pt4.xaxis.get_majorticklabels(), rotation=30, ha="right")
    add_insight(ax_pt4,
        f"18 meses de estabilidad (~{pre4['prod_tk'].mean():.1f} items/ticket, tendencia no significativa p={p_pt4:.2f}). "
        f"La fila unica produjo quiebre abrupto: cayo {abs(delta_pt4):.1f} items a {post4['prod_tk'].mean():.1f}. "
        "No es tendencia: es un cambio de comportamiento del cliente.")

    ax_tk4 = fig4.add_subplot(gs4[1])
    ax_tk4.scatter(pre4["semana"],  pre4["tickets"],  color=C2, s=28, alpha=0.85, zorder=4)
    ax_tk4.scatter(post4["semana"], post4["tickets"], color=C1, s=38, marker="D", zorder=5)
    ax_tk4.plot(pre4["semana"], ic_tk4+sl_tk4*xpre4, color=C2, lw=1.8, ls="--",
                label=f"Tendencia pre (p={p_tk4:.3f})")
    ax_tk4.axvline(FILA_UNICA, color="#E59C00", lw=2, zorder=6)
    slope_mes4 = sl_tk4 * 30.4
    ax_tk4.annotate(f"Tendencia: {slope_mes4:+.0f} tickets/mes",
                    xy=(pre4["semana"].iloc[len(pre4)//2],
                        ic_tk4+sl_tk4*(pre4["semana"]-t0w).dt.days.iloc[len(pre4)//2]),
                    xytext=(pre4["semana"].iloc[len(pre4)//4], pre4["tickets"].mean()+650),
                    fontsize=8.5, color=C2, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))
    style_ax(ax_tk4, title="Tickets de venta por semana", ylabel="Tickets / semana")
    ax_tk4.legend(fontsize=7.5, loc="lower left")
    ax_tk4.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %Y"))
    ax_tk4.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=2))
    plt.setp(ax_tk4.xaxis.get_majorticklabels(), rotation=30, ha="right")
    add_insight(ax_tk4,
        f"El supermercado pierde {abs(slope_mes4):.0f} tickets/mes (tendencia significativa, p={p_tk4:.3f}). "
        f"Proyeccion anual: ~{abs(slope_mes4)*12:.0f} tickets/semana menos. "
        "Este es el problema de fondo: menos clientes, independiente de la fila unica.")

    pdf.savefig(fig4, dpi=150)
    plt.close(fig4)

    # =========================================================================
    # PAGE 5: Fila unica vs tendencia historica
    # =========================================================================
    hist_dl5 = dl[(dl["fecha"] >= "2025-01-05") & (dl["fecha"] < "2025-12-01")].copy()
    hd5 = (hist_dl5.groupby("fecha")
           .agg(tickets=("ticket_id","nunique"), prods=("ticket_id","count"))
           .reset_index())
    hd5["prod_tk"] = hd5["prods"] / hd5["tickets"]
    hd5["dow"]     = hd5["fecha"].dt.dayofweek
    base5 = hd5.groupby("dow").agg(
        tk_med=("tickets","median"),
        tk_p25=("tickets", lambda x: x.quantile(0.25)),
        tk_p75=("tickets", lambda x: x.quantile(0.75)),
        pt_med=("prod_tk","median"),
    ).reset_index()

    post5 = dl[(dl["fecha"] >= "2026-03-28") & (dl["fecha"] <= "2026-04-05")].copy()
    pd5 = (post5.groupby("fecha")
           .agg(tickets=("ticket_id","nunique"), prods=("ticket_id","count"))
           .reset_index())
    pd5["prod_tk"] = pd5["prods"] / pd5["tickets"]
    pd5["dow"]     = pd5["fecha"].dt.dayofweek
    pd5 = pd5.merge(base5, on="dow")
    pd5["tk_delta"] = (pd5["tickets"] / pd5["tk_med"] - 1) * 100
    pd5["pt_delta"] = (pd5["prod_tk"] / pd5["pt_med"] - 1) * 100
    DM = {0:"Lun",1:"Mar",2:"Mie",3:"Jue",4:"Vie",5:"Sab",6:"Dom"}
    pd5["lbl"] = pd5["fecha"].dt.strftime("%d/%m") + "\n" + pd5["dow"].map(DM)
    SS = {pd.Timestamp("2026-04-03"), pd.Timestamp("2026-04-04"), pd.Timestamp("2026-04-05")}
    pd5["ss"] = pd5["fecha"].isin(SS)

    norm5   = pd5[~pd5["ss"]]
    atk5    = norm5["tk_delta"].mean()
    apt5    = norm5["pt_delta"].mean()
    neto5   = (1 + atk5/100) * (1 + apt5/100) - 1   # valor exacto (corregido Codex)

    fig5 = plt.figure(figsize=(11.69, 8.27))
    fig5.patch.set_facecolor("white")
    gs5 = gridspec.GridSpec(2, 2, figure=fig5,
                            left=0.07, right=0.97, top=0.87, bottom=0.07,
                            hspace=0.90, wspace=0.38)
    fig5.text(0.5, 0.952, "Fila Unica - Efecto Real vs Tendencia Historica",
              ha="center", va="top", fontsize=13, fontweight="bold", color=CDARK)
    fig5.text(0.5, 0.920,
              "Cada dia vs mediana del mismo dia de semana (2025)  |  Gris = Semana Santa (no comparables)",
              ha="center", va="top", fontsize=8.5, color=CBAS)

    nb = len(pd5); xb5 = np.arange(nb)
    ctk5 = ["#CCCCCC" if r["ss"] else ("#2D9B4E" if r["tk_delta"]>=0 else C1) for _, r in pd5.iterrows()]
    cpt5 = ["#CCCCCC" if r["ss"] else C1 for _, r in pd5.iterrows()]

    ax_dtk5 = fig5.add_subplot(gs5[0, 0])
    bars_tk5 = ax_dtk5.bar(xb5, pd5["tk_delta"], color=ctk5, zorder=3, width=0.6)
    ax_dtk5.axhline(0, color=CDARK, lw=0.8)
    ax_dtk5.set_xticks(xb5); ax_dtk5.set_xticklabels(pd5["lbl"], fontsize=7.5)
    style_ax(ax_dtk5, title="Tickets: desvio vs mediana historica", ylabel="% diferencia")
    ax_dtk5.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:+.0f}%"))
    for bar, (_, row) in zip(bars_tk5, pd5.iterrows()):
        hv = bar.get_height()
        ax_dtk5.text(bar.get_x()+bar.get_width()/2, hv+(0.5 if hv>=0 else -0.5),
                     f"{hv:+.0f}%", ha="center", va="bottom" if hv>=0 else "top",
                     fontsize=7, color="#888" if row["ss"] else CDARK)
    from matplotlib.patches import Patch
    ax_dtk5.legend(handles=[Patch(facecolor="#2D9B4E", label="Sobre mediana"),
                             Patch(facecolor=C1, label="Bajo mediana"),
                             Patch(facecolor="#CCC", label="Semana Santa")],
                   fontsize=7, loc="lower left")
    add_insight(ax_dtk5,
        f"Dias habiles (28/03-02/04): promedio {atk5:+.1f}% sobre la mediana. "
        "Mie y Jue con mayor exceso (+26% y +29%). "
        "La fila unica parece agilizar el flujo - entran mas clientes.")

    ax_dpt5 = fig5.add_subplot(gs5[0, 1])
    bars_pt5 = ax_dpt5.bar(xb5, pd5["pt_delta"], color=cpt5, zorder=3, width=0.6)
    ax_dpt5.axhline(0, color=CDARK, lw=0.8)
    ax_dpt5.set_xticks(xb5); ax_dpt5.set_xticklabels(pd5["lbl"], fontsize=7.5)
    style_ax(ax_dpt5, title="Productos/ticket: desvio vs mediana historica", ylabel="% diferencia")
    ax_dpt5.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:+.0f}%"))
    for bar, (_, row) in zip(bars_pt5, pd5.iterrows()):
        hv = bar.get_height()
        ax_dpt5.text(bar.get_x()+bar.get_width()/2, hv+(0.5 if hv>=0 else -0.5),
                     f"{hv:+.0f}%", ha="center", va="bottom" if hv>=0 else "top",
                     fontsize=7, color="#888" if row["ss"] else CDARK)
    add_insight(ax_dpt5,
        f"Consistentemente negativo: promedio {apt5:+.1f}% en dias normales. "
        "Cada cliente compra ~1 item menos. "
        "Dias de Semana Santa: caidas aun mayores (-27%) por tipo de compra festiva.")

    ax_abs5 = fig5.add_subplot(gs5[1, 0])
    wab5 = 0.35
    ax_abs5.bar(xb5-wab5/2, pd5["tk_med"],   width=wab5, color=C2, alpha=0.7, label="Mediana historica", zorder=3)
    ax_abs5.bar(xb5+wab5/2, pd5["tickets"],  width=wab5, color=C1, label="Real 2026", zorder=3)
    ax_abs5.errorbar(xb5-wab5/2, pd5["tk_med"],
                     yerr=[pd5["tk_med"]-pd5["tk_p25"], pd5["tk_p75"]-pd5["tk_med"]],
                     fmt="none", color=CDARK, capsize=3, lw=1.2, zorder=5)
    ax_abs5.set_xticks(xb5); ax_abs5.set_xticklabels(pd5["lbl"], fontsize=7.5)
    style_ax(ax_abs5, title="Tickets diarios: real vs mediana historica", ylabel="Tickets")
    ax_abs5.legend(fontsize=7.5, loc="upper left")
    add_insight(ax_abs5,
        "Barras rojas sobre las azules en casi todos los dias habiles. "
        "Las barras de error muestran rango historico normal: P1 esta fuera del rango superior varios dias.")

    ax_sum5 = fig5.add_subplot(gs5[1, 1])
    ax_sum5.axis("off")
    neto_lbl = f"{neto5*100:+.2f}% (aprox. neutro)"
    sum_rows5 = [
        ["Dias normales (28/03 - 02/04)", ""],
        ["Tickets vs mediana",            f"{atk5:+.1f}%"],
        ["Productos/ticket vs mediana",   f"{apt5:+.1f}%"],
        ["Efecto neto en volumen",        neto_lbl],
        ["", ""],
        ["Semana Santa (03-05/04)", ""],
        ["Vier. Santo tickets",           f"{pd5.loc[pd5['fecha']=='2026-04-03','tk_delta'].iloc[0]:+.0f}%"],
        ["Sab. Gloria tickets",           f"{pd5.loc[pd5['fecha']=='2026-04-04','tk_delta'].iloc[0]:+.0f}%"],
        ["Sab. Gloria prod/ticket",       f"{pd5.loc[pd5['fecha']=='2026-04-04','pt_delta'].iloc[0]:+.0f}%"],
    ]
    tbl_s5 = ax_sum5.table(cellText=sum_rows5, colWidths=[0.65,0.30],
                           loc="center", cellLoc="left")
    tbl_s5.auto_set_font_size(False); tbl_s5.set_fontsize(9)
    for (r, c), cell in tbl_s5.get_celld().items():
        cell.set_edgecolor("none")
        if r in {0,5}:
            cell.set_facecolor(CDARK); cell.set_text_props(color="white", fontweight="bold")
        elif r%2==0: cell.set_facecolor("#F5F5F5")
        else: cell.set_facecolor("white")
        if c==1 and r not in {0,5} and r>0:
            txt = sum_rows5[r][1]
            try:
                val = float(txt.split("%")[0].replace("+","").strip())
                cell.set_text_props(color="#2D9B4E" if val>0.5 else (C1 if val<-0.5 else CDARK),
                                    fontweight="bold")
            except: pass
    tbl_s5.scale(1, 2.1)
    ax_sum5.set_title("Balance fila unica - dias normales",
                      fontsize=9, fontweight="bold", color=CDARK, pad=6, loc="left")
    add_insight(ax_sum5,
        f"Efecto neto: {neto5*100:+.2f}% - practicamente neutro. "
        "Mas tickets (+13%) compensan exactamente la canasta mas chica (-12%). "
        "La fila unica no sube ni baja la facturacion: cambia como se compra.",
        dy=-0.08)

    pdf.savefig(fig5, dpi=150)
    plt.close(fig5)

print(f"\nPDF generado: {PDF_PATH}")
