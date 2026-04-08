"""
Análisis acotado al pedido de Sebastián (WhatsApp 06/04/2026):

  - Semana P1: 30/03/2026 → 05/04/2026
  - Semana P2: 14/04/2025 → 20/04/2025

  Métricas pedidas (y solo estas):
    1. Cantidad de tickets y cantidad de productos (P1 vs P2)
    2. Promedio de tickets (por día) y productos por ticket
    3. Media, mediana y percentiles del importe del ticket POR HORA
    4. Distribución de tickets por caja

Cada bloque va en una página propia con su gráfico y la explicación debajo.
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

warnings.filterwarnings("ignore")

# ── Rutas ──────────────────────────────────────────────────────────────────
BASE       = Path(__file__).resolve().parents[1]
OUT_DIR    = BASE / "abril"
CSV_HIST   = BASE / "data" / "raw" / "comprobantes_ventas_horario.csv"
PARQUET_DL = BASE / "data" / "processed" / "detalle_lineas.parquet"
EXCEL_2026 = Path(r"D:/GoogleDrive/PYMEINSIDE/nino/extraccion datos/2026/marzo/ReporteComprobantesVenta6-4.xlsx")

PDF_PATH   = OUT_DIR / "analisis_solo_pedido_sebastian.pdf"

# ── Períodos ───────────────────────────────────────────────────────────────
P1_START, P1_END = pd.Timestamp("2026-03-30"), pd.Timestamp("2026-04-05")
P2_START, P2_END = pd.Timestamp("2025-04-14"), pd.Timestamp("2025-04-20")
P1_LABEL = "30/03 – 05/04/2026"
P2_LABEL = "14/04 – 20/04/2025"
DIAS_ES  = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

# ── Mapa cajas ──────────────────────────────────────────────────────────────
PV_MAP = {"0014":1,"0015":1,"0016":2,"0017":2,"0018":3,"0019":3,
          "0020":4,"0021":4,"0022":5,"0023":5,"0024":6,"0025":6,
          "0026":7,"0027":7,"0028":8,"0029":8}

# ── Colores ─────────────────────────────────────────────────────────────────
C1   = "#E63946"   # rojo  → P1 2026
C2   = "#4A90D9"   # azul  → P2 2025
CDARK = "#1A1A2E"
SPINE = "#CCCCCC"
C_INSIGHT, C_INS_BORDER = "#EEF4FF", "#AABBDD"

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

def extract_pv(comp):
    """'Factura B 0020-00183892' → '0020'"""
    m = re.search(r'(\d{4})-\d+', str(comp))
    return m.group(1) if m else None


print("Cargando CSV histórico (2025)...")
csv = pd.read_csv(CSV_HIST, sep=";", low_memory=False)
csv = csv[csv["Comprobante"].astype(str).str.startswith("Factura", na=False)].copy()
csv["fecha"] = pd.to_datetime(csv["Fecha"].astype(str).str[:10])
csv["hora"]  = csv["Hora"].apply(parse_hora_csv)
csv["pv"]    = csv["Comprobante"].apply(extract_pv)
csv["caja"]  = csv["pv"].map(PV_MAP).fillna(0).astype(int)
csv["Importe"] = pd.to_numeric(csv["Importe"], errors="coerce")
csv = csv[csv["hora"].notna() & (csv["hora"] >= 7) & (csv["hora"] <= 22)]

print("Cargando Excel 2026...")
xl = pd.read_excel(EXCEL_2026, header=4)
xl = xl[~xl["Fecha"].astype(str).str.contains("TOTAL|nan", na=False)].copy()
xl["fecha"] = pd.to_datetime(xl["Fecha"], dayfirst=True, errors="coerce")
xl = xl[xl["fecha"].notna() & xl["Comprobante"].astype(str).str.startswith("Factura")].copy()
xl["hora"] = xl["Hora"].apply(parse_hora_excel)
xl["pv"]   = xl["Comprobante"].apply(extract_pv)
xl["caja"] = xl["pv"].map(PV_MAP).fillna(0).astype(int)
xl["Importe"] = pd.to_numeric(xl["Importe"], errors="coerce")
xl = xl[xl["hora"].notna() & (xl["hora"] >= 7) & (xl["hora"] <= 22)]

print("Cargando líneas (parquet) para conteo de productos...")
dl = pd.read_parquet(PARQUET_DL)

# ── Filtrar a los dos períodos ──────────────────────────────────────────────
p1_tk = xl[(xl["fecha"] >= P1_START) & (xl["fecha"] <= P1_END)].copy()
p2_tk = csv[(csv["fecha"] >= P2_START) & (csv["fecha"] <= P2_END)].copy()

p1_items = dl[(dl["fecha"] >= P1_START) & (dl["fecha"] <= P1_END)]
p2_items = dl[(dl["fecha"] >= P2_START) & (dl["fecha"] <= P2_END)]

print(f"P1 tickets: {p1_tk['Comprobante'].nunique():,}  |  P2 tickets: {p2_tk['Comprobante'].nunique():,}")
print(f"P1 items:   {len(p1_items):,}                |  P2 items:   {len(p2_items):,}")

p2_imp_validos = int(p2_tk["Importe"].notna().sum())
p2_imp_total   = len(p2_tk)
print(f"P2 importes disponibles: {p2_imp_validos:,}/{p2_imp_total:,} "
      f"({p2_imp_validos/p2_imp_total*100:.0f}%)")


# ═══════════════════════════════════════════════════════════════════════════
# 2. KPIs Y MÉTRICAS
# ═══════════════════════════════════════════════════════════════════════════

def kpis(tk_df, items_df):
    n_tk    = tk_df["Comprobante"].nunique()
    n_items = len(items_df)
    # Ticket promedio = importe total / cantidad tickets (solo importes válidos)
    imp_validos = tk_df[tk_df["Importe"].notna() & (tk_df["Importe"] > 0)]
    tk_prom = imp_validos["Importe"].mean() if len(imp_validos) else 0
    return {
        "tickets":    n_tk,
        "productos":  n_items,
        "tk_promedio": tk_prom,
    }

kp1 = kpis(p1_tk, p1_items)
kp2 = kpis(p2_tk, p2_items)

# Stats del importe del ticket POR HORA
def importe_hora_stats(tk_df):
    tk_df = tk_df[tk_df["Importe"].notna() & (tk_df["Importe"] > 0)].copy()
    out = {}
    for h in range(7, 23):
        sub = tk_df[tk_df["hora"] == h]["Importe"]
        if len(sub) < 3:
            out[h] = {"n": 0, "media": 0, "mediana": 0, "p25": 0, "p75": 0, "p90": 0}
        else:
            out[h] = {
                "n":       len(sub),
                "media":   sub.mean(),
                "mediana": sub.median(),
                "p25":     sub.quantile(0.25),
                "p75":     sub.quantile(0.75),
                "p90":     sub.quantile(0.90),
            }
    return pd.DataFrame(out).T

imp_h_p1 = importe_hora_stats(p1_tk)
imp_h_p2 = importe_hora_stats(p2_tk)

# Distribución por caja
def caja_stats(tk_df):
    df = tk_df[tk_df["caja"] > 0]
    g = df.groupby("caja").agg(
        tickets=("Comprobante", "nunique"),
        imp_med=("Importe", "median"),
    )
    return g.reindex(range(1, 9), fill_value=0)

caja_p1 = caja_stats(p1_tk)
caja_p2 = caja_stats(p2_tk)


# ═══════════════════════════════════════════════════════════════════════════
# 3. PDF
# ═══════════════════════════════════════════════════════════════════════════

OUT_DIR.mkdir(exist_ok=True)

def style_ax(ax, title=None, xlabel=None, ylabel=None):
    ax.set_facecolor("white")
    for sp in ax.spines.values():
        sp.set_color(SPINE); sp.set_linewidth(0.7)
    ax.tick_params(labelsize=8, color=CDARK)
    ax.grid(axis="y", color="#EEEEEE", linewidth=0.6, zorder=0)
    if title:  ax.set_title(title, fontsize=10, fontweight="bold", color=CDARK, pad=6)
    if xlabel: ax.set_xlabel(xlabel, fontsize=8.5, color=CDARK)
    if ylabel: ax.set_ylabel(ylabel, fontsize=8.5, color=CDARK)

def fmt_d(d):
    return f"+{d:.1f}%" if d >= 0 else f"{d:.1f}%"

def explica(ax, lines, ax_title="Lectura"):
    """Coloca una caja de texto con la explicación debajo del gráfico."""
    ax.axis("off")
    txt = "\n".join(["• " + l for l in lines])
    ax.text(0.0, 0.97, ax_title, transform=ax.transAxes,
            ha="left", va="top", fontsize=10, fontweight="bold", color=CDARK)
    ax.text(0.0, 0.84, txt, transform=ax.transAxes,
            ha="left", va="top", fontsize=9, color="#1A1A2E",
            linespacing=1.45,
            bbox=dict(boxstyle="round,pad=0.55", facecolor=C_INSIGHT,
                      edgecolor=C_INS_BORDER, alpha=0.95))


with PdfPages(PDF_PATH) as pdf:

    # =========================================================================
    # PÁGINA 1: Cantidad de tickets, productos y ticket promedio
    # =========================================================================
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.patch.set_facecolor("white")
    gs = gridspec.GridSpec(2, 1, figure=fig,
                           left=0.10, right=0.90, top=0.88, bottom=0.08,
                           height_ratios=[1.4, 1.0], hspace=0.40)

    fig.text(0.5, 0.955, "Cantidad de tickets, productos y ticket promedio",
             ha="center", va="top", fontsize=16, fontweight="bold", color=CDARK)
    fig.text(0.5, 0.920, f"P1: {P1_LABEL}     vs     P2: {P2_LABEL}",
             ha="center", va="top", fontsize=11, color="#555")

    # ── Tabla resumen ──────────────────────────────────────────────────────
    ax_tbl = fig.add_subplot(gs[0]); ax_tbl.axis("off")
    vd  = (kp1["tickets"]    / kp2["tickets"]    - 1) * 100
    pdv = (kp1["productos"]  / kp2["productos"]  - 1) * 100
    vtp = (kp1["tk_promedio"]/ kp2["tk_promedio"]- 1) * 100 if kp2["tk_promedio"] else 0

    tbl_data = [
        ["", P1_LABEL, P2_LABEL, "Variación"],
        ["Cantidad de tickets",   f"{kp1['tickets']:,.0f}",   f"{kp2['tickets']:,.0f}",   fmt_d(vd)],
        ["Cantidad de productos", f"{kp1['productos']:,.0f}", f"{kp2['productos']:,.0f}", fmt_d(pdv)],
        ["Ticket promedio",       f"${kp1['tk_promedio']:,.0f}", f"${kp2['tk_promedio']:,.0f}", fmt_d(vtp)],
    ]
    col_w = [0.30, 0.22, 0.22, 0.16]
    tbl = ax_tbl.table(cellText=tbl_data[1:], colLabels=tbl_data[0],
                       colWidths=col_w, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(11)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(SPINE)
        if r == 0:
            cell.set_facecolor(CDARK); cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0: cell.set_facecolor("#F5F5F5")
        else:            cell.set_facecolor("white")
        if c == 0 and r > 0:
            cell.set_text_props(ha="left", fontweight="bold")
        if c == 3 and r > 0:
            v = tbl_data[r][3]
            cell.set_text_props(
                color="#2D9B4E" if v.startswith("+") else C1,
                fontweight="bold")
    tbl.scale(1, 3.2)

    # ── Explicación ───────────────────────────────────────────────────────
    ax_exp = fig.add_subplot(gs[1])
    explica(ax_exp, [
        f"P1 tuvo {kp1['tickets']:,} tickets vs {kp2['tickets']:,} en P2 ({fmt_d(vd)}).",
        f"P1 movió {kp1['productos']:,} productos vs {kp2['productos']:,} en P2 ({fmt_d(pdv)}).",
        f"Ticket promedio P1: ${kp1['tk_promedio']:,.0f}  |  P2: ${kp2['tk_promedio']:,.0f} "
        f"({fmt_d(vtp)} — la diferencia refleja inflación interanual, no es comparable directa).",
        f"En P2 (2025) el importe está disponible solo en el {p2_imp_validos/p2_imp_total*100:.0f}% "
        f"de los tickets — el ticket promedio P2 se calcula sobre esa muestra.",
    ])

    pdf.savefig(fig, dpi=150)
    plt.close(fig)

    # =========================================================================
    # PÁGINA 2: Importe del ticket por hora — media, mediana, percentiles
    # =========================================================================
    fig2 = plt.figure(figsize=(11.69, 8.27))
    fig2.patch.set_facecolor("white")
    gs2 = gridspec.GridSpec(3, 1, figure=fig2,
                            left=0.07, right=0.97, top=0.91, bottom=0.05,
                            height_ratios=[1.7, 1.4, 1.1], hspace=0.55)

    fig2.text(0.5, 0.965, "Importe del ticket por hora — media, mediana y percentiles",
              ha="center", va="top", fontsize=15, fontweight="bold", color=CDARK)
    fig2.text(0.5, 0.935,
              f"P1: {P1_LABEL}     vs     P2: {P2_LABEL}     "
              f"(*P2: importe disponible en {p2_imp_validos/p2_imp_total*100:.0f}% de los tickets)",
              ha="center", va="top", fontsize=9, color="#555")

    horas_act = [h for h in range(8, 22)
                 if (h in imp_h_p1.index and imp_h_p1.loc[h, "n"] > 0)]

    # ── Gráfico de líneas ────────────────────────────────────────────────
    ax_line = fig2.add_subplot(gs2[0])
    p1_med = [imp_h_p1.loc[h, "mediana"]/1000 for h in horas_act]
    p1_avg = [imp_h_p1.loc[h, "media"]/1000   for h in horas_act]
    p1_p25 = [imp_h_p1.loc[h, "p25"]/1000     for h in horas_act]
    p1_p75 = [imp_h_p1.loc[h, "p75"]/1000     for h in horas_act]
    p2_med = [imp_h_p2.loc[h, "mediana"]/1000 if (h in imp_h_p2.index and imp_h_p2.loc[h,"n"]>0) else None
              for h in horas_act]

    ax_line.fill_between(horas_act, p1_p25, p1_p75, color=C1, alpha=0.18,
                         label="P1: rango P25-P75")
    ax_line.plot(horas_act, p1_med, color=C1, lw=2.2, marker="o", ms=5,
                 label=f"P1 mediana ({P1_LABEL})", zorder=5)
    ax_line.plot(horas_act, p1_avg, color=C1, lw=1.4, ls=":", marker="^", ms=4,
                 alpha=0.85, label="P1 media", zorder=4)
    if any(v is not None for v in p2_med):
        ax_line.plot(horas_act, [v if v is not None else np.nan for v in p2_med],
                     color=C2, lw=2, marker="s", ms=5,
                     label=f"P2 mediana ({P2_LABEL})*", zorder=4)
    ax_line.set_xticks(horas_act)
    ax_line.set_xticklabels([f"{h}h" for h in horas_act], fontsize=9)
    ax_line.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:.0f}K"))
    style_ax(ax_line, title="Importe del ticket por hora",
             ylabel="$ miles", xlabel="Hora del día")
    ax_line.legend(fontsize=8, framealpha=0.88, ncol=2)

    # ── Tabla con TODAS las stats por hora (P1) ──────────────────────────
    ax_t = fig2.add_subplot(gs2[1]); ax_t.axis("off")
    def fmt_k(v): return f"${v/1000:.1f}K" if v > 0 else "-"
    rows = []
    for h in horas_act:
        row = [f"{h}h",
               f"{int(imp_h_p1.loc[h,'n']):,}",
               fmt_k(imp_h_p1.loc[h,'media']),
               fmt_k(imp_h_p1.loc[h,'mediana']),
               fmt_k(imp_h_p1.loc[h,'p25']),
               fmt_k(imp_h_p1.loc[h,'p75']),
               fmt_k(imp_h_p1.loc[h,'p90'])]
        rows.append(row)
    cols = ["Hora", "Tickets", "Media", "Mediana", "P25", "P75", "P90"]
    tbl_h = ax_t.table(cellText=rows, colLabels=cols,
                       colWidths=[0.07, 0.10, 0.13, 0.13, 0.13, 0.13, 0.13],
                       loc="center", cellLoc="center")
    tbl_h.auto_set_font_size(False); tbl_h.set_fontsize(8.5)
    for (r, c), cell in tbl_h.get_celld().items():
        cell.set_edgecolor(SPINE)
        if r == 0:
            cell.set_facecolor(CDARK); cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#F5F5F5")
        else:
            cell.set_facecolor("white")
        if c == 0 and r > 0:
            cell.set_text_props(fontweight="bold", color=C1)
    tbl_h.scale(1, 1.45)

    # ── Explicación ──────────────────────────────────────────────────────
    ax_exp2 = fig2.add_subplot(gs2[2])
    h_pico_med = max(horas_act, key=lambda h: imp_h_p1.loc[h, "mediana"])
    valor_pico = imp_h_p1.loc[h_pico_med, "mediana"]
    p90_max    = imp_h_p1["p90"].max()
    h_p90_max  = imp_h_p1["p90"].idxmax()
    explica(ax_exp2, [
        f"En P1 la mediana de importe más alta cae a las {h_pico_med}h "
        f"(${valor_pico/1000:.1f}K). Es el momento del día con tickets más grandes.",
        f"La banda sombreada muestra el rango P25–P75 (la mitad central de los tickets de cada hora). "
        f"Más ancha = mayor variabilidad de gasto.",
        f"El P90 más alto se da a las {h_p90_max}h con ${p90_max/1000:.0f}K: "
        f"el 10% de los clientes de esa hora gasta por encima de ese valor.",
        f"La mediana de P2 está abajo en términos absolutos (~½) por la inflación interanual "
        f"(no es comparable directamente, sí lo es la forma de la curva por hora).",
    ])

    pdf.savefig(fig2, dpi=150)
    plt.close(fig2)

    # =========================================================================
    # PÁGINA 3: Distribución de tickets por caja
    # =========================================================================
    fig3 = plt.figure(figsize=(11.69, 8.27))
    fig3.patch.set_facecolor("white")
    gs3 = gridspec.GridSpec(3, 1, figure=fig3,
                            left=0.07, right=0.97, top=0.91, bottom=0.05,
                            height_ratios=[1.6, 1.3, 1.0], hspace=0.55)

    fig3.text(0.5, 0.965, "Distribución de tickets por caja",
              ha="center", va="top", fontsize=15, fontweight="bold", color=CDARK)
    fig3.text(0.5, 0.935, f"P1: {P1_LABEL}     vs     P2: {P2_LABEL}",
              ha="center", va="top", fontsize=10, color="#555")

    cajas = list(range(1, 9))
    tot_p1 = caja_p1["tickets"].sum()
    tot_p2 = caja_p2["tickets"].sum()
    pct_p1 = caja_p1["tickets"] / tot_p1 * 100
    pct_p2 = caja_p2["tickets"] / tot_p2 * 100

    # ── Gráfico de barras ────────────────────────────────────────────────
    ax_c = fig3.add_subplot(gs3[0])
    x, w = np.arange(8), 0.38
    ax_c.bar(x - w/2, pct_p1.values, width=w, color=C1, label=P1_LABEL, zorder=3)
    ax_c.bar(x + w/2, pct_p2.values, width=w, color=C2, label=P2_LABEL, zorder=3)
    ax_c.set_xticks(x); ax_c.set_xticklabels([f"Caja {c}" for c in cajas], fontsize=9)
    ax_c.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    style_ax(ax_c, title="% de tickets por caja", ylabel="% del total semanal")
    ax_c.legend(fontsize=9, framealpha=0.85, loc="upper right")
    for rect in ax_c.patches:
        hv = rect.get_height()
        if hv > 0.3:
            ax_c.text(rect.get_x() + rect.get_width()/2, hv + 0.18,
                      f"{hv:.1f}%", ha="center", va="bottom", fontsize=7.5, color=CDARK)

    # ── Tabla con tickets absolutos ───────────────────────────────────────
    ax_ct = fig3.add_subplot(gs3[1]); ax_ct.axis("off")
    rows = []
    for c in cajas:
        t1 = int(caja_p1.loc[c, "tickets"])
        t2 = int(caja_p2.loc[c, "tickets"]) if c in caja_p2.index else 0
        pp1 = pct_p1.loc[c]
        pp2 = pct_p2.loc[c]
        var = (t1/t2 - 1)*100 if t2 > 0 else float("nan")
        rows.append([f"Caja {c}", f"{t1:,}", f"{pp1:.1f}%",
                     f"{t2:,}", f"{pp2:.1f}%",
                     fmt_d(var) if not np.isnan(var) else "-"])
    rows.append(["Total", f"{int(tot_p1):,}", "100%",
                 f"{int(tot_p2):,}", "100%", fmt_d((tot_p1/tot_p2-1)*100)])
    cols = ["", f"Tickets {P1_LABEL}", "% P1",
            f"Tickets {P2_LABEL}", "% P2", "Variación"]
    tbl_c = ax_ct.table(cellText=rows, colLabels=cols,
                        colWidths=[0.10, 0.20, 0.10, 0.20, 0.10, 0.15],
                        loc="center", cellLoc="center")
    tbl_c.auto_set_font_size(False); tbl_c.set_fontsize(9)
    for (r, c), cell in tbl_c.get_celld().items():
        cell.set_edgecolor(SPINE)
        if r == 0:
            cell.set_facecolor(CDARK); cell.set_text_props(color="white", fontweight="bold")
        elif r == len(cajas) + 1:
            cell.set_facecolor("#E8E8E8"); cell.set_text_props(fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#F5F5F5")
        else:
            cell.set_facecolor("white")
        if c == 0 and r > 0:
            cell.set_text_props(fontweight="bold")
        if c == 5 and 0 < r <= len(cajas):
            v = rows[r-1][5]
            if v != "-":
                cell.set_text_props(
                    color="#2D9B4E" if v.startswith("+") else C1,
                    fontweight="bold")
    tbl_c.scale(1, 1.55)

    # ── Explicación ──────────────────────────────────────────────────────
    ax_exp3 = fig3.add_subplot(gs3[2])
    top1_p1 = pct_p1.idxmax()
    top1_p2 = pct_p2.idxmax()
    cajas_op_p1 = int((caja_p1["tickets"] > 0).sum())
    cajas_op_p2 = int((caja_p2["tickets"] > 0).sum())
    explica(ax_exp3, [
        f"En P1 la caja con más tickets fue la Caja {top1_p1} ({pct_p1.loc[top1_p1]:.1f}% del total). "
        f"En P2 fue la Caja {top1_p2} ({pct_p2.loc[top1_p2]:.1f}%).",
        f"Cajas con actividad: {cajas_op_p1} en P1 vs {cajas_op_p2} en P2 (de 8 disponibles).",
        f"Comparando P1 vs P2 caja por caja, la columna 'Variación' muestra cuáles cajas "
        f"crecieron y cuáles cayeron en volumen absoluto de tickets.",
    ])

    pdf.savefig(fig3, dpi=150)
    plt.close(fig3)


print(f"\nPDF generado: {PDF_PATH}")
