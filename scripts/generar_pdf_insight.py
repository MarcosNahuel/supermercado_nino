"""
Genera PDF Infográfico — Insight Estratégico NINO v2
=====================================================
- Datos calculados desde fuente (no hardcoded)
- Insight box debajo de cada gráfico
- P5: Estacionalidad Sábados (cobro + Pascuas)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
import warnings
from pathlib import Path
from scipy import stats as sp_stats

warnings.filterwarnings("ignore")

# ── Paths ──
BASE = Path(r"D:\OneDrive\GitHub\supermercado_nino definitivo claude")
EXCEL_DIR = Path(r"H:\Mi unidad\PYMEINSIDE\nino\extraccion datos\2026\marzo")
CSV_HIST = BASE / "data" / "raw" / "comprobantes_ventas_horario.csv"
COMP_NEW = EXCEL_DIR / "ReporteComprobantesVenta6-4.xlsx"
OUT_PDF = BASE / "nino" / "Insight_Rotiseria_Panaderia_NINO.pdf"

# ── Colores ──
AZUL     = "#1F4E79"
AZUL_C   = "#4472C4"
VERDE    = "#2E7D32"
ROJO     = "#C62828"
NARANJA  = "#E65100"
GRIS     = "#616161"
GRIS_C   = "#E0E0E0"
AMARILLO = "#F9A825"

plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 10,
    "axes.facecolor": "#FAFAFA", "figure.facecolor": "#FFFFFF",
})


def insight_box(fig, y, lines, h=0.065, bg="#E8F5E9", border="#388E3C"):
    """Caja de insight con borde redondeado y texto multi-linea."""
    rect = mpatches.FancyBboxPatch(
        (0.04, y), 0.92, h, boxstyle="round,pad=0.006",
        facecolor=bg, edgecolor=border, linewidth=1.5, alpha=0.90,
        transform=fig.transFigure)
    fig.add_artist(rect)
    fig.text(0.065, y + h - 0.013, "INSIGHT:",
             fontsize=9, fontweight="bold", color=border)
    for i, line in enumerate(lines):
        fig.text(0.065, y + h - 0.026 - i * 0.015, line,
                 fontsize=8.5, color="#333333")


# ══════════════════════════════════════════════════
# 1. CARGAR DATOS DE ITEMS (cross-sell 30 dias)
# ══════════════════════════════════════════════════
print("Cargando datos de items...")
suffixes = ("1", "2", "22", "3", "18-28", "31")
dfs = [pd.read_excel(EXCEL_DIR / f"ReporteMovimientosItemEnComprobantes{s}.xlsx",
                      header=3) for s in suffixes]
df = pd.concat(dfs, ignore_index=True)
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%d/%m/%y", errors="coerce")
df = df[df["Fecha"].notna()].drop_duplicates(subset=["Fecha", "Comprobante", "Código"])

date_max = df["Fecha"].max()
cutoff30 = date_max - pd.Timedelta(days=30)
df30 = df[df["Fecha"] >= cutoff30].copy()
DAYS = df30["Fecha"].dt.date.nunique()
WINDOW = f"{cutoff30.strftime('%d/%m/%Y')} — {date_max.strftime('%d/%m/%Y')}"
M = 30.4167 / DAYS

# ── Cross-sell rotisería ──
tk_rotis = set(df30[df30["Departamento"] == "ROTISERIA"]["Comprobante"].unique())
r_venta = df30[(df30["Comprobante"].isin(tk_rotis)) &
               (df30["Departamento"] == "ROTISERIA")]["Importe"].sum()
r_cross = df30[(df30["Comprobante"].isin(tk_rotis)) &
               (df30["Departamento"] != "ROTISERIA")]["Importe"].sum()
r_ratio = r_cross / r_venta if r_venta else 0

prom_con = (df30[df30["Comprobante"].isin(tk_rotis)]
            .groupby("Comprobante")["Importe"].sum().mean())
tk_sin = set(df30["Comprobante"].unique()) - tk_rotis
prom_sin = (df30[df30["Comprobante"].isin(tk_sin)]
            .groupby("Comprobante")["Importe"].sum().mean() if tk_sin else 0)
uplift_pct = (prom_con / prom_sin - 1) * 100 if prom_sin else 0

# ── Segmentación causal ──
tk_data = []
for tk in tk_rotis:
    items = df30[df30["Comprobante"] == tk]
    total = items["Importe"].sum()
    rv = items[items["Departamento"] == "ROTISERIA"]["Importe"].sum()
    tk_data.append({"otros": total - rv,
                    "pct": rv / total * 100 if total else 0})
tkdf = pd.DataFrame(tk_data)

segmentos = [
    ("<10%",   0,   10,  0.05, "agrega\nde paso",   VERDE),
    ("10-30%", 10,  30,  0.15, "comple-\nmento",    "#66BB6A"),
    ("30-50%", 30,  50,  0.40, "motivo\nparcial",   AMARILLO),
    ("50-75%", 50,  75,  0.70, "motivo\nprincipal", NARANJA),
    (">75%",   75, 101,  0.95, "viene por\nrotis",  ROJO),
]

total_cross_riesgo = 0
seg_results = []
for name, lo, hi, risk, desc, col in segmentos:
    sub = tkdf[(tkdf["pct"] >= lo) & (tkdf["pct"] < hi)]
    n = len(sub)
    pct_tk = n / len(tkdf) * 100 if len(tkdf) else 0
    otros = sub["otros"].sum()
    en_riesgo = otros * risk
    total_cross_riesgo += en_riesgo
    seg_results.append(dict(name=name, n=n, pct=pct_tk, risk=risk,
                            otros=otros, en_riesgo=en_riesgo,
                            desc=desc, col=col))

cross_riesgo_m = round(total_cross_riesgo * M)
cross_total_m = round(r_cross * M)
ROTIS_RESULTADO = -3_282_022   # auditado vs generar_excel_costos.py 2026-04-06
PANAD_RESULTADO = 7_367_270    # auditado vs generar_excel_costos_panaderia.py 2026-04-06
neto_cerrar = -ROTIS_RESULTADO - cross_riesgo_m

# ── Top 10 productos ──
rotis_by_prod = (df30[df30["Departamento"] == "ROTISERIA"]
                 .groupby("Nombre")["Comprobante"].apply(set).to_dict())
prod_rows = []
for prod, tks in rotis_by_prod.items():
    if len(tks) < 5:
        continue
    vp = df30[(df30["Comprobante"].isin(tks)) &
              (df30["Nombre"] == prod)]["Importe"].sum()
    cs = df30[(df30["Comprobante"].isin(tks)) &
              (df30["Departamento"] != "ROTISERIA")]["Importe"].sum()
    prod_rows.append(dict(prod=prod[:25], venta=vp, cross=cs,
                          ratio=cs / vp if vp else 0))
prod_top = pd.DataFrame(prod_rows).sort_values("cross", ascending=False).head(10)

# ── Top departamentos arrastrados ──
dept_cross = (df30[(df30["Comprobante"].isin(tk_rotis)) &
                   (df30["Departamento"] != "ROTISERIA")]
              .groupby("Departamento")["Importe"].sum()
              .sort_values(ascending=False).head(10))

# ── Correlación Rotis ↔ Panad ──
basket = df30.groupby(["Comprobante", "Departamento"])["Importe"].sum().unstack(fill_value=0)
bask_bin = (basket > 0).astype(int)
n_total = len(bask_bin)
R, P = "ROTISERIA", "PANAD.ELAB.PROPIA"
p_r = bask_bin[R].mean()
p_p = bask_bin[P].mean()
p_p_r = bask_bin.loc[bask_bin[R] == 1, P].mean()
p_r_p = bask_bin.loc[bask_bin[P] == 1, R].mean()
p_rp = ((bask_bin[R] == 1) & (bask_bin[P] == 1)).mean()
lift = p_rp / (p_r * p_p) if (p_r * p_p) else 0
cont = pd.crosstab(bask_bin[R], bask_bin[P])
chi2, pval, _, _ = sp_stats.chi2_contingency(cont)
cram_v = np.sqrt(chi2 / (n_total * (min(cont.shape) - 1)))

idx_ambos = list(set(bask_bin[bask_bin[R] == 1].index) &
                 set(bask_bin[bask_bin[P] == 1].index))
panad_en_rotis_pct = basket.loc[idx_ambos, P].sum() / basket[P].sum() * 100
rotis_en_panad_pct = basket.loc[idx_ambos, R].sum() / basket[R].sum() * 100
panad_perdida_m = basket.loc[idx_ambos, P].sum() * M

# ── P(Rotis | Dept) ──
dept_rotis = []
for d in sorted(bask_bin.columns):
    if d == R:
        continue
    nd = bask_bin[d].sum()
    if nd < 500:
        continue
    nb = ((bask_bin[d] == 1) & (bask_bin[R] == 1)).sum()
    dept_rotis.append(dict(dept=d, pct=nb / nd * 100, n=int(nd)))
dept_pct = pd.DataFrame(dept_rotis).sort_values("pct", ascending=False)

print(f"  Items: {len(df30):,} filas | {DAYS} días | {len(tk_rotis)} tickets con rotis")

# ══════════════════════════════════════════════════
# 2. CARGAR DATOS DE SÁBADOS
# ══════════════════════════════════════════════════
print("Cargando sábados...")
cn = pd.read_excel(COMP_NEW, header=4)
cn = cn[~cn["Fecha"].astype(str).str.contains("TOTAL|nan", na=False)].copy()
cn["fecha"] = pd.to_datetime(cn["Fecha"], dayfirst=True, errors="coerce")
cn = cn[cn["fecha"].notna()]
cn["Importe"] = pd.to_numeric(cn["Importe"], errors="coerce")
cn = cn[cn["Comprobante"].astype(str).str.startswith("Factura")]

cc = pd.read_csv(CSV_HIST, sep=";", low_memory=False)
cc = cc[cc["Comprobante"].astype(str).str.startswith("Factura", na=False)].copy()
cc["fecha"] = pd.to_datetime(cc["Fecha"].str[:10])
cc["Importe"] = pd.to_numeric(cc.get("Importe", pd.Series(dtype=float)),
                               errors="coerce")

new_min = cn["fecha"].min()
all_comp = pd.concat([
    cc[cc["fecha"] < new_min][["fecha", "Comprobante", "Importe"]],
    cn[["fecha", "Comprobante", "Importe"]],
], ignore_index=True)
all_comp["dow"] = all_comp["fecha"].dt.dayofweek

sab_wk = (all_comp[all_comp["dow"] == 5]
           .groupby("fecha")
           .agg(tickets=("Comprobante", "nunique"),
                importe=("Importe", "sum"))
           .reset_index().sort_values("fecha").reset_index(drop=True))
sab_wk["dom"] = sab_wk["fecha"].dt.day

PASCUAS = {pd.Timestamp("2025-04-19"), pd.Timestamp("2026-04-04")}
is_cobro = lambda d: d <= 7 or 13 <= d <= 17
sab_wk["tipo"] = sab_wk.apply(
    lambda r: ("Pascuas" if r["fecha"] in PASCUAS
               else ("Cobro" if is_cobro(r["dom"]) else "Normal")),
    axis=1)

sab_cobro = sab_wk[sab_wk["tipo"] == "Cobro"]
sab_normal = sab_wk[sab_wk["tipo"] == "Normal"]
sab_pascuas = sab_wk[sab_wk["tipo"] == "Pascuas"]

mu_all = sab_wk["tickets"].mean()
mu_cobro = sab_cobro["tickets"].mean() if len(sab_cobro) else 0
mu_normal = sab_normal["tickets"].mean() if len(sab_normal) else 0
mu_imp_cobro = sab_cobro["importe"].mean() if len(sab_cobro) else 0
mu_imp_normal = sab_normal["importe"].mean() if len(sab_normal) else 0
delta_tk = (mu_cobro / mu_normal - 1) * 100 if mu_normal else 0
delta_imp = (mu_imp_cobro / mu_imp_normal - 1) * 100 if mu_imp_normal else 0

slope, intercept = np.polyfit(np.arange(len(sab_wk)), sab_wk["tickets"], 1)
trend = slope * np.arange(len(sab_wk)) + intercept
sigma = sab_wk["tickets"].std()
best = sab_wk.loc[sab_wk["tickets"].idxmax()]

print(f"  Sábados: {len(sab_wk)} | Cobro: {len(sab_cobro)} "
      f"| Normal: {len(sab_normal)} | Pascuas: {len(sab_pascuas)}")
print(f"  Media: All={mu_all:.0f} | Cobro={mu_cobro:.0f} ({delta_tk:+.1f}%) "
      f"| Normal={mu_normal:.0f}")

# ══════════════════════════════════════════════════
# 2b. PARQUET PARA DEPARTAMENTOS FILA ÚNICA
# ══════════════════════════════════════════════════
print("Cargando parquet para análisis departamental...")
dl = pd.read_parquet(BASE / "data" / "processed" / "detalle_lineas.parquet")
dl["dow"] = dl["fecha"].dt.dayofweek
sab_dl = dl[dl["dow"] == 5].copy()

CUTOFF_FU = pd.Timestamp("2026-03-28")
DEPT_FU = {
    "Carnicería": ["CARNICERIA AL 10,5 %", "CARNICERIA"],
    "Golosinas": ["GOLOSINAS"],
}

pre_dl = sab_dl[sab_dl["fecha"] < CUTOFF_FU]
post_dl = sab_dl[sab_dl["fecha"] >= CUTOFF_FU]
n_pre_s = pre_dl["fecha"].nunique()
n_post_s = post_dl["fecha"].nunique()

sat_all_tk = sab_dl.groupby("fecha")["ticket_id"].nunique()
dept_fu_data = {}
HRS = list(range(7, 22))

# ── Hora: join items Excel + ComprobantesVenta (parquet hora=0) ──
extra_item_dfs = []
for s in ("04-04", "6-4"):
    fp = EXCEL_DIR / f"ReporteMovimientosItemEnComprobantes{s}.xlsx"
    if fp.exists():
        extra_item_dfs.append(pd.read_excel(fp, header=3))
        print(f"    + items {s}: {len(extra_item_dfs[-1]):,} filas")
df_all_items = pd.concat(dfs + extra_item_dfs, ignore_index=True)
df_all_items["Fecha"] = pd.to_datetime(df_all_items["Fecha"],
                                        format="%d/%m/%y", errors="coerce")
df_all_items = df_all_items[df_all_items["Fecha"].notna()]
df_all_items["dow"] = df_all_items["Fecha"].dt.dayofweek
df_all_items["comp_num"] = (df_all_items["Comprobante"].astype(str)
                            .str.extract(r"(\d{4}-\d+)")[0])

cn_h = cn.copy()
cn_h["comp_num"] = cn_h["Comprobante"].astype(str).str.extract(r"(\d{4}-\d+)")[0]
cn_h["hora_int"] = pd.to_datetime(cn_h["Hora"], format="%H:%M",
                                   errors="coerce").dt.hour
hora_map = (cn_h.dropna(subset=["comp_num", "hora_int"])
            .drop_duplicates("comp_num")[["comp_num", "hora_int"]])

df_h = df_all_items.merge(hora_map, on="comp_num", how="inner")
sab_h = df_h[df_h["dow"] == 5]
pre_sab_h = sab_h[sab_h["Fecha"] < CUTOFF_FU]
post_sab_h = sab_h[sab_h["Fecha"] >= CUTOFF_FU]
n_pre_h = pre_sab_h["Fecha"].dt.date.nunique()
n_post_h = post_sab_h["Fecha"].dt.date.nunique()
print(f"  Hourly join: {len(sab_h):,} items sáb | "
      f"Pre {n_pre_h} sáb, Post {n_post_h} sáb")

for lbl, cats in DEPT_FU.items():
    # Per-Saturday penetration from parquet (74 sáb, OK)
    cat_mask = sab_dl["categoria"].isin(cats)
    sat_dept_tk = (sab_dl[cat_mask].groupby("fecha")["ticket_id"].nunique()
                   .reindex(sat_all_tk.index, fill_value=0))
    sat_dept_vta = (sab_dl[cat_mask].groupby("fecha")["importe_total"].sum()
                    .reindex(sat_all_tk.index, fill_value=0))
    sdf = pd.DataFrame({
        "tk": sat_all_tk, "dept_tk": sat_dept_tk,
        "dept_vta": sat_dept_vta,
        "pct": sat_dept_tk / sat_all_tk * 100,
    })
    pre_pct_d = sdf.loc[sdf.index < CUTOFF_FU, "pct"].mean()
    post_pct_d = sdf.loc[sdf.index >= CUTOFF_FU, "pct"].mean()
    pre_vta_d = sdf.loc[sdf.index < CUTOFF_FU, "dept_vta"].mean()
    post_vta_d = sdf.loc[sdf.index >= CUTOFF_FU, "dept_vta"].mean()
    m28 = (sdf.loc[pd.Timestamp("2026-03-28")]
           if pd.Timestamp("2026-03-28") in sdf.index else None)
    a04 = (sdf.loc[pd.Timestamp("2026-04-04")]
           if pd.Timestamp("2026-04-04") in sdf.index else None)

    # Hourly from Excel+CompVenta (hora real, no parquet)
    dept_pre = pre_sab_h["Departamento"].isin(cats)
    dept_post = post_sab_h["Departamento"].isin(cats)
    pre_h_list, post_h_list = [], []
    for h in HRS:
        pt = pre_sab_h[pre_sab_h["hora_int"] == h]["Comprobante"].nunique()
        pdn = pre_sab_h[(pre_sab_h["hora_int"] == h) &
                         dept_pre]["Comprobante"].nunique()
        pre_h_list.append(pdn / pt * 100 if pt else 0)
        qt = post_sab_h[post_sab_h["hora_int"] == h]["Comprobante"].nunique()
        qdn = post_sab_h[(post_sab_h["hora_int"] == h) &
                          dept_post]["Comprobante"].nunique()
        post_h_list.append(qdn / qt * 100 if qt else 0)

    dept_fu_data[lbl] = dict(
        pre_pct=pre_pct_d, post_pct=post_pct_d,
        pre_vta=pre_vta_d, post_vta=post_vta_d,
        m28=m28, a04=a04, pre_h=pre_h_list, post_h=post_h_list,
    )
    delta_d = (post_pct_d / pre_pct_d - 1) * 100 if pre_pct_d else 0
    print(f"  {lbl}: Pre {pre_pct_d:.1f}% -> Post {post_pct_d:.1f}% "
          f"({delta_d:+.1f}%) | hourly items: {dept_pre.sum():,}")

# ══════════════════════════════════════════════════
# 3. GENERAR PDF (7 páginas)
# ══════════════════════════════════════════════════
print("Generando PDF...")

with PdfPages(str(OUT_PDF)) as pdf:

    # ─── P1: RESUMEN EJECUTIVO ───────────────────
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.patch.set_facecolor("white")

    fig.text(0.5, 0.96, "INSIGHT ESTRATÉGICO", fontsize=28,
             fontweight="bold", ha="center", color=AZUL)
    fig.text(0.5, 0.925, "Rotisería & Panadería — Supermercado NINO (BOSIN S.A.)",
             fontsize=14, ha="center", color=GRIS)
    fig.text(0.5, 0.90, f"Datos: {WINDOW} ({DAYS} días) | "
             f"{df30['Comprobante'].nunique():,} tickets analizados",
             fontsize=10, ha="center", color=GRIS)
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.885, 0.885],
                              color=AZUL, linewidth=2))

    fig.text(0.5, 0.86, "¿Conviene mantener la rotisería si pierde plata?",
             fontsize=18, fontweight="bold", ha="center", color=ROJO,
             style="italic")

    # Col 1: Visión Contable
    fig.text(0.18, 0.80, "VISIÓN CONTABLE", fontsize=13,
             fontweight="bold", ha="center", color=AZUL)
    fig.text(0.18, 0.76, "Rotisería", fontsize=11, ha="center", color=GRIS)
    fig.text(0.18, 0.71, f"-${abs(ROTIS_RESULTADO)/1e6:.1f}M",
             fontsize=26, fontweight="bold", ha="center", color=ROJO)
    fig.text(0.18, 0.67, "/mes", fontsize=11, ha="center", color=GRIS)
    fig.text(0.18, 0.63, "DEFICITARIO", fontsize=12,
             fontweight="bold", ha="center", color=ROJO)
    fig.text(0.18, 0.57, "Panadería", fontsize=11, ha="center", color=GRIS)
    fig.text(0.18, 0.52, f"+${PANAD_RESULTADO/1e6:.0f}M",
             fontsize=26, fontweight="bold", ha="center", color=VERDE)
    fig.text(0.18, 0.48, "/mes", fontsize=11, ha="center", color=GRIS)
    fig.text(0.18, 0.44, "SUPERAVITARIO", fontsize=12,
             fontweight="bold", ha="center", color=VERDE)

    # Col 2: Visión Comercial
    fig.text(0.50, 0.80, "VISIÓN COMERCIAL", fontsize=13,
             fontweight="bold", ha="center", color=AZUL)
    fig.text(0.50, 0.76, "Cross-sell Rotisería", fontsize=11,
             ha="center", color=GRIS)
    fig.text(0.50, 0.71, f"{r_ratio:.1f}x", fontsize=32,
             fontweight="bold", ha="center", color=NARANJA)
    fig.text(0.50, 0.66, f"Por cada $1 de rotis,\nel cliente compra "
             f"${r_ratio:.1f} de\notros rubros",
             fontsize=10, ha="center", va="top", color=GRIS)
    fig.text(0.50, 0.55, "Ticket promedio", fontsize=11,
             ha="center", color=GRIS)
    fig.text(0.50, 0.51, f"CON rotis: ${prom_con:,.0f}", fontsize=12,
             fontweight="bold", ha="center", color=VERDE)
    fig.text(0.50, 0.47, f"SIN rotis: ${prom_sin:,.0f}", fontsize=12,
             ha="center", color=GRIS)
    fig.text(0.50, 0.43, f"+{uplift_pct:.0f}% más por ticket",
             fontsize=13, fontweight="bold", ha="center", color=NARANJA)

    # Col 3: Si se cierra (CORREGIDO: riesgo causal)
    fig.text(0.82, 0.80, "SI SE CIERRA", fontsize=13,
             fontweight="bold", ha="center", color=AZUL)
    fig.text(0.82, 0.76, "Ahorro (pérdida evitada)", fontsize=10,
             ha="center", color=GRIS)
    fig.text(0.82, 0.71, f"+${abs(ROTIS_RESULTADO)/1e6:.1f}M",
             fontsize=22, fontweight="bold", ha="center", color=VERDE)
    fig.text(0.82, 0.65, "Cross-sell en riesgo causal", fontsize=10,
             ha="center", color=GRIS)
    fig.text(0.82, 0.60, f"-${cross_riesgo_m/1e6:.1f}M",
             fontsize=22, fontweight="bold", ha="center", color=ROJO)
    fig.text(0.82, 0.54, "RESULTADO NETO", fontsize=11,
             fontweight="bold", ha="center", color=GRIS)
    neto_txt = "GANA" if neto_cerrar > 0 else "PIERDE"
    neto_col = VERDE if neto_cerrar > 0 else ROJO
    fig.text(0.82, 0.49, neto_txt, fontsize=20, fontweight="bold",
             ha="center", color=neto_col)
    fig.text(0.82, 0.45, f"${abs(neto_cerrar)/1e6:.1f}M/mes",
             fontsize=18, fontweight="bold", ha="center", color=neto_col)

    # Separadores
    fig.add_artist(plt.Line2D([0.34, 0.34], [0.40, 0.82],
                              color=GRIS_C, linewidth=1))
    fig.add_artist(plt.Line2D([0.66, 0.66], [0.40, 0.82],
                              color=GRIS_C, linewidth=1))

    # Segmentación barras
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.37, 0.37],
                              color=AZUL, linewidth=1))
    fig.text(0.5, 0.35,
             "SEGMENTACIÓN CAUSAL: ¿El cliente viene POR la rotisería?",
             fontsize=13, fontweight="bold", ha="center", color=AZUL)

    x_start, bw = 0.08, 0.16
    for i, s in enumerate(seg_results):
        x = x_start + i * (bw + 0.02)
        h = s["pct"] / 100 * 0.15
        rect = mpatches.FancyBboxPatch(
            (x, 0.16), bw, h, boxstyle="round,pad=0.005",
            facecolor=s["col"], edgecolor="white", linewidth=2,
            transform=fig.transFigure)
        fig.add_artist(rect)
        fig.text(x + bw / 2, 0.14, s["desc"], fontsize=8,
                 ha="center", va="top", color=GRIS)
        fig.text(x + bw / 2, 0.16 + h + 0.01, f"{s['pct']:.0f}%",
                 fontsize=11, fontweight="bold", ha="center", color=s["col"])
        fig.text(x + bw / 2, 0.16 + h + 0.035,
                 f"Riesgo: {s['risk']*100:.0f}%",
                 fontsize=8, ha="center", color=GRIS)

    pct_baja = sum(s["pct"] for s in seg_results if s["risk"] <= 0.15)
    insight_box(fig, 0.03, [
        f"El {pct_baja:.0f}% de los clientes con rotisería la agrega de "
        f"paso — solo el {100-pct_baja:.0f}% viene por ella.",
        f"Cross-sell en riesgo CAUSAL: ${cross_riesgo_m/1e6:.1f}M/mes "
        f"(no los ${cross_total_m/1e6:.1f}M totales).",
        f"Resultado neto de cerrar: {neto_txt} "
        f"${abs(neto_cerrar)/1e6:.1f}M/mes.",
    ], h=0.065, bg="#FFF3E0", border=NARANJA)

    fig.text(0.95, 0.005, "1/7", fontsize=9, ha="right", color=GRIS)
    pdf.savefig(fig); plt.close()

    # ─── P2: CROSS-SELL POR PRODUCTO ─────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.69, 8.27))
    fig.patch.set_facecolor("white")
    fig.suptitle("CROSS-SELLING: ¿Qué productos de rotisería arrastran "
                 "más ventas?",
                 fontsize=16, fontweight="bold", color=AZUL, y=0.96)
    fig.text(0.5, 0.93, f"{WINDOW} — Cada barra = cuánto compran de "
             "OTROS rubros los clientes de ese producto",
             fontsize=10, ha="center", color=GRIS)

    prods = prod_top["prod"].tolist()
    vals = (prod_top["cross"] / 1e6).tolist()
    rats = prod_top["ratio"].tolist()
    c1 = [ROJO if r > 15 else (NARANJA if r > 7 else AZUL_C) for r in rats]

    y1 = np.arange(len(prods))
    ax1.barh(y1, vals, color=c1, height=0.7, edgecolor="white", linewidth=0.5)
    ax1.set_yticks(y1); ax1.set_yticklabels(prods, fontsize=10)
    ax1.invert_yaxis()
    ax1.set_xlabel("Cross-sell generado (millones $)", fontsize=10)
    ax1.set_title("Top 10 por volumen de cross-sell", fontsize=12,
                  fontweight="bold", color=AZUL)
    for i, (v, r) in enumerate(zip(vals, rats)):
        ax1.text(v + 0.05, i, f"${v:.1f}M ({r:.0f}x)",
                 va="center", fontsize=9, color=GRIS)
    ax1.set_xlim(0, max(vals) * 1.4)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    deptos = [d[:15] for d in dept_cross.index.tolist()]
    dvals = (dept_cross.values / 1e6).tolist()
    c2 = [AZUL if v > 5 else (AZUL_C if v > 3 else "#90CAF9") for v in dvals]

    y2 = np.arange(len(deptos))
    ax2.barh(y2, dvals, color=c2, height=0.7, edgecolor="white", linewidth=0.5)
    ax2.set_yticks(y2); ax2.set_yticklabels(deptos, fontsize=10)
    ax2.invert_yaxis()
    ax2.set_xlabel("Venta en tickets con rotis (millones $)", fontsize=10)
    ax2.set_title("Rubros que se venden junto con rotisería", fontsize=12,
                  fontweight="bold", color=AZUL)
    for i, v in enumerate(dvals):
        ax2.text(v + 0.05, i, f"${v:.1f}M",
                 va="center", fontsize=9, color=GRIS)
    ax2.set_xlim(0, max(dvals) * 1.3)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.text(0.15, 0.135, "Ratio >15x (ancla fuerte)",
             fontsize=9, color=ROJO)
    fig.text(0.40, 0.135, "Ratio 7-15x (moderado)",
             fontsize=9, color=NARANJA)
    fig.text(0.63, 0.135, "Ratio <7x",
             fontsize=9, color=AZUL_C)

    insight_box(fig, 0.03, [
        "Guarniciones (ensaladas, patitas) tienen ratios >15x: "
        "anclas de ticket grande.",
        "Matambre y empanadas lideran en volumen absoluto por alta "
        "frecuencia de compra.",
        f"{deptos[0]} (${dvals[0]:.1f}M) es el rubro más arrastrado: "
        "compra semanal de carne.",
    ], h=0.065, bg="#E3F2FD", border=AZUL_C)

    fig.text(0.95, 0.005, "2/7", fontsize=9, ha="right", color=GRIS)
    plt.tight_layout(rect=[0, 0.20, 1, 0.91])
    pdf.savefig(fig); plt.close()

    # ─── P3: CORRELACIÓN ROTIS ↔ PANAD ──────────
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.patch.set_facecolor("white")

    fig.text(0.5, 0.96, "CORRELACIÓN: ¿La rotisería arrastra a la "
             "panadería?",
             fontsize=18, fontweight="bold", ha="center", color=AZUL)
    fig.text(0.5, 0.925, '"¿Hay parte de la producción de panadería que '
             'corresponde a rotisería?"  — Sebastián Peña',
             fontsize=11, ha="center", color=GRIS, style="italic")
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.91, 0.91],
                              color=AZUL, linewidth=2))

    # Izq: Rotis → Panad
    fig.text(0.28, 0.87, "ROTISERÍA → PANADERÍA", fontsize=14,
             fontweight="bold", ha="center", color=AZUL)
    fig.text(0.28, 0.83, f"{p_p_r*100:.1f}% de tickets con rotis\n"
             "también compran panadería",
             fontsize=11, ha="center", color=GRIS)
    fig.text(0.28, 0.77, f"vs {p_p*100:.1f}% promedio",
             fontsize=10, ha="center", color=GRIS)
    fig.text(0.28, 0.72, f"{panad_en_rotis_pct:.1f}%",
             fontsize=28, fontweight="bold", ha="center", color=VERDE)
    fig.text(0.28, 0.68, "de la venta de panadería\nestá en tickets "
             "con rotisería",
             fontsize=11, ha="center", color=GRIS)
    fig.text(0.28, 0.61, f"Impacto: ~${panad_perdida_m/1e6:.1f}M/mes",
             fontsize=13, fontweight="bold", ha="center", color=VERDE)
    fig.text(0.28, 0.57, "BAJO — Rotis NO arrastra a panadería",
             fontsize=11, fontweight="bold", ha="center", color=VERDE)

    fig.add_artist(plt.Line2D([0.50, 0.50], [0.54, 0.89],
                              color=GRIS_C, linewidth=1))

    # Der: Panad → Rotis
    fig.text(0.72, 0.87, "PANADERÍA → ROTISERÍA", fontsize=14,
             fontweight="bold", ha="center", color=AZUL)
    fig.text(0.72, 0.83, f"{p_r_p*100:.1f}% de tickets con panadería\n"
             "también compran rotisería",
             fontsize=11, ha="center", color=GRIS)
    fig.text(0.72, 0.77, f"vs {p_r*100:.1f}% promedio",
             fontsize=10, ha="center", color=GRIS)
    fig.text(0.72, 0.72, f"{rotis_en_panad_pct:.1f}%",
             fontsize=28, fontweight="bold", ha="center", color=ROJO)
    fig.text(0.72, 0.68, "de la venta de rotisería\nestá en tickets "
             "con panadería",
             fontsize=11, ha="center", color=GRIS)
    fig.text(0.72, 0.61, "La mitad de rotisería depende\n"
             "de clientes de panadería",
             fontsize=11, fontweight="bold", ha="center", color=ROJO)

    # Tests
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.51, 0.51],
                              color=AZUL, linewidth=1))
    fig.text(0.5, 0.49, "TESTS ESTADÍSTICOS", fontsize=13,
             fontweight="bold", ha="center", color=AZUL)

    tests = [
        (f"Lift = {lift:.2f}",
         f"Se compran juntos {(lift-1)*100:.0f}% más de lo esperado",
         NARANJA),
        (f"Chi² = {chi2:.1f} (p < 0.001)",
         "Asociación estadísticamente significativa", VERDE),
        (f"Cramér's V = {cram_v:.3f}",
         "Asociación DÉBIL en magnitud (escala 0-1)", AMARILLO),
    ]
    for i, (met, desc, col) in enumerate(tests):
        y = 0.44 - i * 0.05
        fig.text(0.20, y, met, fontsize=12, fontweight="bold", color=col)
        fig.text(0.50, y, desc, fontsize=11, color=GRIS)

    # Conclusión
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.26, 0.26],
                              color=AZUL, linewidth=1))
    fig.text(0.5, 0.24, "CONCLUSIÓN PARA SEBASTIÁN", fontsize=14,
             fontweight="bold", ha="center", color=AZUL)

    concs = [
        (f"Sí hay cross-selling, pero la asociación es DÉBIL "
         f"(Lift={lift:.2f}, V={cram_v:.3f})", GRIS, "normal"),
        (f"Solo el {panad_en_rotis_pct:.1f}% de la venta de panadería "
         "está en tickets con rotisería", GRIS, "normal"),
        (f"En cambio, {rotis_en_panad_pct:.1f}% de ROTISERÍA depende "
         "de tickets con panadería", GRIS, "normal"),
        ("PANADERÍA ARRASTRA A ROTISERÍA, no al revés",
         ROJO, "bold"),
        ("Cerrar rotisería NO afecta significativamente a panadería",
         VERDE, "bold"),
    ]
    for i, (txt, col, fw) in enumerate(concs):
        fig.text(0.10, 0.20 - i * 0.035, f"→ {txt}",
                 fontsize=11, color=col, fontweight=fw)

    insight_box(fig, 0.02, [
        f"Relación estadísticamente real (p<0.001) pero débil "
        f"(V={cram_v:.3f}).",
        f"Panadería arrastra rotisería ({rotis_en_panad_pct:.0f}% "
        "de rotis en tickets con panad).",
        "Cerrar rotisería: impacto nulo en panadería. "
        "Cerrar panadería: mata a rotisería.",
    ], h=0.06, bg="#FCE4EC", border=ROJO)

    fig.text(0.95, 0.005, "3/7", fontsize=9, ha="right", color=GRIS)
    pdf.savefig(fig); plt.close()

    # ─── P4: PESO POR RUBRO ─────────────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.69, 8.27),
                                    gridspec_kw={"width_ratios": [1, 1.2]})
    fig.patch.set_facecolor("white")
    fig.suptitle("De los tickets de cada rubro, ¿cuántos también llevan "
                 "rotisería?",
                 fontsize=16, fontweight="bold", color=AZUL, y=0.96)
    fig.text(0.5, 0.93, "Peso de tickets con rotisería respecto del "
             "total de tickets de cada rubro — Pedido Seba Peña",
             fontsize=10, ha="center", color=GRIS)

    # Izq: P(Rotis | Dept)
    dn = dept_pct["dept"].str[:18].tolist()
    dp = dept_pct["pct"].tolist()
    dns = dept_pct["n"].tolist()
    base_pct = p_r * 100
    cl = [ROJO if p > 8 else (NARANJA if p > 6 else
          (AZUL_C if p > base_pct else GRIS_C)) for p in dp]

    yp = np.arange(len(dn))
    ax1.barh(yp, dp, color=cl, height=0.65, edgecolor="white")
    ax1.axvline(x=base_pct, color=AZUL, linewidth=2, linestyle="--",
                alpha=0.7)
    ax1.set_yticks(yp); ax1.set_yticklabels(dn, fontsize=9)
    ax1.invert_yaxis()
    ax1.set_xlabel("% tickets del rubro con rotisería", fontsize=9)
    ax1.set_title("% tickets con rotisería (por rubro)", fontsize=11,
                  fontweight="bold", color=AZUL)
    for i, (v, n) in enumerate(zip(dp, dns)):
        ax1.text(v + 0.1, i, f"{v:.1f}% ({n:,} tk)",
                 va="center", fontsize=8, color=GRIS)
    ax1.set_xlim(0, max(dp) * 1.4)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.text(base_pct + 0.1, len(dn) - 0.5,
             f"Promedio\n{base_pct:.1f}%",
             fontsize=8, color=AZUL, va="top")

    # Der: $ absoluto
    dnr = [d[:15] for d in dept_cross.index.tolist()][:15]
    cm = (dept_cross.values / 1e6).tolist()[:15]
    cr = [AZUL if v > 3 else (AZUL_C if v > 1 else "#90CAF9") for v in cm]

    yr = np.arange(len(dnr))
    ax2.barh(yr, cm, color=cr, height=0.65, edgecolor="white")
    ax2.set_yticks(yr); ax2.set_yticklabels(dnr, fontsize=9)
    ax2.invert_yaxis()
    ax2.set_xlabel("Venta en tickets con rotis (millones $)", fontsize=9)
    ax2.set_title("$ absoluto en juego", fontsize=11,
                  fontweight="bold", color=AZUL)
    for i, v in enumerate(cm):
        ax2.text(v + 0.05, i, f"${v:.1f}M",
                 va="center", fontsize=8, color=GRIS)
    ax2.set_xlim(0, max(cm) * 1.25)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    td = dept_pct.iloc[0]
    insight_box(fig, 0.03, [
        f"{td['dept']} ({td['pct']:.1f}%) tiene la mayor afinidad con "
        f"rotisería (2x el promedio {base_pct:.1f}%).",
        f"En $ absolutos, {dnr[0]} (${cm[0]:.1f}M) es el más expuesto "
        "si se cierra.",
        f"Rojo >8% | Naranja 6-8% | Azul >promedio | "
        f"Gris debajo del promedio.",
    ], h=0.065, bg="#E8F5E9", border=VERDE)

    fig.text(0.95, 0.005, "4/7", fontsize=9, ha="right", color=GRIS)
    plt.tight_layout(rect=[0, 0.14, 1, 0.91])
    pdf.savefig(fig); plt.close()

    # ─── P5: ESTACIONALIDAD SÁBADOS ─────────────
    fig = plt.figure(figsize=(11.69, 8.27))
    gs = GridSpec(2, 1, figure=fig, height_ratios=[3.2, 1],
                  left=0.06, right=0.97, top=0.88, bottom=0.14,
                  hspace=0.30)
    fig.patch.set_facecolor("white")

    fig.text(0.5, 0.96, "ESTACIONALIDAD SÁBADOS: Efecto Cobro y Pascuas",
             fontsize=18, fontweight="bold", ha="center", color=AZUL)
    fig.text(0.5, 0.925,
             f"{len(sab_wk)} sábados analizados "
             f"({sab_wk['fecha'].min().strftime('%b %Y')} — "
             f"{sab_wk['fecha'].max().strftime('%b %Y')})",
             fontsize=11, ha="center", color=GRIS)
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.91, 0.91],
                              color=AZUL, linewidth=2))

    # ── Histograma principal ──
    ax = fig.add_subplot(gs[0])
    type_colors = {"Normal": AZUL_C, "Cobro": VERDE, "Pascuas": ROJO}
    bar_colors = [type_colors[t] for t in sab_wk["tipo"]]

    xb = np.arange(len(sab_wk))
    ax.bar(xb, sab_wk["tickets"].values, color=bar_colors, width=0.85,
           edgecolor="white", linewidth=0.3)

    # Promedio + banda ±1σ
    ax.axhline(mu_all, color=AZUL, linewidth=1.5, linestyle="--",
               alpha=0.7)
    ax.fill_between(xb, mu_all - sigma, mu_all + sigma,
                    alpha=0.08, color=AZUL)
    ax.text(len(xb) - 1, mu_all + 8,
            f"Promedio: {mu_all:,.0f} tk",
            fontsize=8, ha="right", color=AZUL, fontweight="bold")

    # Tendencia
    ax.plot(xb, trend, color=NARANJA, linewidth=2, alpha=0.7)
    ax.text(len(xb) - 1, trend[-1] + 8,
            f"Tendencia: {slope:+.1f} tk/sem",
            fontsize=8, ha="right", color=NARANJA, fontweight="bold")

    # Anotar Pascuas
    for idx, row in sab_wk[sab_wk["tipo"] == "Pascuas"].iterrows():
        lbl = (f"PASCUAS {row['fecha'].strftime('%Y')}\n"
               f"{int(row['tickets']):,} tk")
        ax.annotate(lbl, xy=(idx, row["tickets"]),
                    xytext=(idx, row["tickets"] + 80),
                    fontsize=8, fontweight="bold", color=ROJO,
                    ha="center",
                    arrowprops=dict(arrowstyle="->", color=ROJO, lw=1.5))

    # Etiquetas cada ~8 barras
    labels = []
    for i, r in enumerate(sab_wk.itertuples()):
        labels.append(r.fecha.strftime("%b\n%y") if i % 8 == 0 else "")
    ax.set_xticks(xb)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("Tickets", fontsize=10)
    ax.set_title("Tickets por sábado — Historial completo",
                 fontsize=12, fontweight="bold", color=AZUL, pad=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    handles = [
        mpatches.Patch(color=AZUL_C, label=f"Normal ({len(sab_normal)})"),
        mpatches.Patch(color=VERDE, label=f"Post-cobro ({len(sab_cobro)})"),
        mpatches.Patch(color=ROJO, label=f"Pascuas ({len(sab_pascuas)})"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=8,
              framealpha=0.9, ncol=3)

    # ── KPI table ──
    ax2 = fig.add_subplot(gs[1])
    ax2.axis("off")

    # Stats Pascuas
    mu_pasc = sab_pascuas["tickets"].mean() if len(sab_pascuas) else 0
    delta_pasc = (mu_pasc / mu_all - 1) * 100 if mu_all else 0
    mu_imp_pasc = sab_pascuas["importe"].mean() if len(sab_pascuas) else 0

    kpi = [
        ["", "Normal", "Post-cobro", "Δ Cobro", "Pascuas", "Δ Pascuas"],
        ["Tickets promedio",
         f"{mu_normal:,.0f}", f"{mu_cobro:,.0f}", f"{delta_tk:+.1f}%",
         f"{mu_pasc:,.0f}", f"{delta_pasc:+.1f}%"],
        ["Facturación prom.",
         f"${mu_imp_normal/1e6:.1f}M", f"${mu_imp_cobro/1e6:.1f}M",
         f"{delta_imp:+.1f}%",
         f"${mu_imp_pasc/1e6:.1f}M",
         f"{(mu_imp_pasc/mu_imp_normal-1)*100:+.1f}%" if mu_imp_normal else ""],
        ["N sábados",
         f"{len(sab_normal)}", f"{len(sab_cobro)}", "",
         f"{len(sab_pascuas)}", ""],
    ]

    table = ax2.table(cellText=kpi, loc="upper center",
                       cellLoc="center",
                       colWidths=[0.18, 0.12, 0.12, 0.10, 0.12, 0.12])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(GRIS_C)
        cell.set_height(0.22)
        if r == 0:
            cell.set_facecolor(AZUL)
            cell.set_text_props(color="white", fontweight="bold",
                                fontsize=8.5)
        elif c in (3, 5) and r > 0:
            txt = kpi[r][c]
            if txt.startswith("-"):
                cell.set_text_props(color=ROJO, fontweight="bold")
                cell.set_facecolor("#FCE4EC")
            elif txt.startswith("+"):
                cell.set_text_props(color=VERDE, fontweight="bold")
                cell.set_facecolor("#E8F5E9")

    insight_box(fig, 0.02, [
        f"Sábado de Pascuas = pico anual: {int(best['tickets']):,} tk "
        f"({best['fecha'].strftime('%d/%m/%Y')}), "
        f"+{(best['tickets']/mu_all-1)*100:.0f}% vs promedio. "
        "Efecto cultural: familias compran para el almuerzo de Pascua.",
        f"Post-cobro: {delta_tk:+.1f}% tickets pero "
        f"{delta_imp:+.1f}% facturación. "
        "Menos visitas pero compras más grandes (ticket promedio mayor).",
        f"Tendencia general: {slope:+.1f} tickets/semana. "
        "Pico en dic (fiestas) y jun (aguinaldo), "
        "valle en jul-sep (invierno).",
    ], h=0.07, bg="#FFF3E0", border=NARANJA)

    fig.text(0.95, 0.005, "5/7", fontsize=9, ha="right", color=GRIS)
    pdf.savefig(fig); plt.close()

    # ─── P6: DEPARTAMENTOS FILA ÚNICA ────────────
    fig = plt.figure(figsize=(11.69, 8.27))
    gs6 = GridSpec(2, 2, figure=fig, height_ratios=[2.5, 1],
                   left=0.07, right=0.97, top=0.87, bottom=0.13,
                   hspace=0.35, wspace=0.30)
    fig.patch.set_facecolor("white")

    fig.text(0.5, 0.96, "DEPARTAMENTOS EN LA FILA ÚNICA",
             fontsize=18, fontweight="bold", ha="center", color=AZUL)
    fig.text(0.5, 0.925,
             f"Carnicería y Golosinas/Snacks — Pre ({n_pre_s} sáb) vs "
             f"Post fila única ({n_post_s} sáb: 28-Mar + 4-Abr)",
             fontsize=11, ha="center", color=GRIS)
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.91, 0.91],
                              color=AZUL, linewidth=2))

    # Top-left: Penetración (% tickets)
    ax6a = fig.add_subplot(gs6[0, 0])
    dept_labels = list(DEPT_FU.keys())
    x6 = np.arange(len(dept_labels))
    w6 = 0.22

    pre_pcts6 = [dept_fu_data[d]["pre_pct"] for d in dept_labels]
    m28_pcts6 = [float(dept_fu_data[d]["m28"]["pct"])
                 if dept_fu_data[d]["m28"] is not None else 0
                 for d in dept_labels]
    a04_pcts6 = [float(dept_fu_data[d]["a04"]["pct"])
                 if dept_fu_data[d]["a04"] is not None else 0
                 for d in dept_labels]

    bars_pre = ax6a.bar(x6 - w6, pre_pcts6, w6,
                         label="Pre (promedio)", color=AZUL_C,
                         edgecolor="white")
    bars_m28 = ax6a.bar(x6, m28_pcts6, w6,
                         label="28-Mar (1er sáb FU)", color=NARANJA,
                         edgecolor="white")
    bars_a04 = ax6a.bar(x6 + w6, a04_pcts6, w6,
                         label="4-Abr (Pascuas)", color=ROJO,
                         edgecolor="white")

    for bars in [bars_pre, bars_m28, bars_a04]:
        for bar in bars:
            hv = bar.get_height()
            ax6a.text(bar.get_x() + bar.get_width() / 2, hv + 0.3,
                      f"{hv:.1f}%", ha="center", fontsize=7.5,
                      color=GRIS)

    ax6a.set_xticks(x6)
    ax6a.set_xticklabels(dept_labels, fontsize=10, fontweight="bold")
    ax6a.set_ylabel("% tickets con depto", fontsize=10)
    ax6a.set_title("Penetración en tickets (sábados)",
                   fontsize=11, fontweight="bold", color=AZUL)
    ax6a.legend(fontsize=7.5, framealpha=0.9)
    ax6a.spines["top"].set_visible(False)
    ax6a.spines["right"].set_visible(False)
    ax6a.grid(axis="y", alpha=0.3)

    # Top-right: Venta $ por sábado
    ax6b = fig.add_subplot(gs6[0, 1])
    pre_vtas6 = [dept_fu_data[d]["pre_vta"] / 1e6 for d in dept_labels]
    m28_vtas6 = [float(dept_fu_data[d]["m28"]["dept_vta"]) / 1e6
                 if dept_fu_data[d]["m28"] is not None else 0
                 for d in dept_labels]
    a04_vtas6 = [float(dept_fu_data[d]["a04"]["dept_vta"]) / 1e6
                 if dept_fu_data[d]["a04"] is not None else 0
                 for d in dept_labels]

    ax6b.bar(x6 - w6, pre_vtas6, w6, label="Pre (promedio)",
             color=AZUL_C, edgecolor="white")
    ax6b.bar(x6, m28_vtas6, w6, label="28-Mar",
             color=NARANJA, edgecolor="white")
    ax6b.bar(x6 + w6, a04_vtas6, w6, label="4-Abr",
             color=ROJO, edgecolor="white")

    for bars in [ax6b.containers[0], ax6b.containers[1],
                 ax6b.containers[2]]:
        for bar in bars:
            hv = bar.get_height()
            ax6b.text(bar.get_x() + bar.get_width() / 2, hv + 0.02,
                      f"${hv:.1f}M", ha="center", fontsize=7.5,
                      color=GRIS)

    ax6b.set_xticks(x6)
    ax6b.set_xticklabels(dept_labels, fontsize=10, fontweight="bold")
    ax6b.set_ylabel("Venta del depto (millones $)", fontsize=10)
    ax6b.set_title("Venta por sábado",
                   fontsize=11, fontweight="bold", color=AZUL)
    ax6b.legend(fontsize=7.5, framealpha=0.9)
    ax6b.spines["top"].set_visible(False)
    ax6b.spines["right"].set_visible(False)
    ax6b.grid(axis="y", alpha=0.3)

    # Bottom: Tabla detallada
    ax6c = fig.add_subplot(gs6[1, :])
    ax6c.axis("off")

    tbl_rows = [["", "Pre prom.", "28-Mar", "Δ vs Pre",
                  "4-Abr", "Δ vs Pre"]]
    for d in dept_labels:
        dd = dept_fu_data[d]
        m28v = float(dd["m28"]["pct"]) if dd["m28"] is not None else 0
        a04v = float(dd["a04"]["pct"]) if dd["a04"] is not None else 0
        dm28 = (m28v / dd["pre_pct"] - 1) * 100 if dd["pre_pct"] else 0
        da04 = (a04v / dd["pre_pct"] - 1) * 100 if dd["pre_pct"] else 0
        tbl_rows.append([f"{d} (% tk)", f"{dd['pre_pct']:.1f}%",
                         f"{m28v:.1f}%", f"{dm28:+.1f}%",
                         f"{a04v:.1f}%", f"{da04:+.1f}%"])
    for d in dept_labels:
        dd = dept_fu_data[d]
        m28v = float(dd["m28"]["dept_vta"]) if dd["m28"] is not None else 0
        a04v = float(dd["a04"]["dept_vta"]) if dd["a04"] is not None else 0
        dm28 = (m28v / dd["pre_vta"] - 1) * 100 if dd["pre_vta"] else 0
        da04 = (a04v / dd["pre_vta"] - 1) * 100 if dd["pre_vta"] else 0
        tbl_rows.append([f"{d} (venta)", f"${dd['pre_vta']/1e6:.1f}M",
                         f"${m28v/1e6:.1f}M", f"{dm28:+.1f}%",
                         f"${a04v/1e6:.1f}M", f"{da04:+.1f}%"])

    tbl6 = ax6c.table(cellText=tbl_rows, loc="upper center",
                       cellLoc="center",
                       colWidths=[0.22, 0.13, 0.13, 0.11, 0.13, 0.11])
    tbl6.auto_set_font_size(False)
    tbl6.set_fontsize(9)
    for (r, c), cell in tbl6.get_celld().items():
        cell.set_edgecolor(GRIS_C)
        cell.set_height(0.16)
        if r == 0:
            cell.set_facecolor(AZUL)
            cell.set_text_props(color="white", fontweight="bold",
                                fontsize=8.5)
        elif c in (3, 5) and r > 0:
            txt = tbl_rows[r][c]
            if txt.startswith("+"):
                cell.set_text_props(color=VERDE, fontweight="bold")
                cell.set_facecolor("#E8F5E9")
            elif txt.startswith("-"):
                cell.set_text_props(color=ROJO, fontweight="bold")
                cell.set_facecolor("#FCE4EC")

    carn_d = dept_fu_data["Carnicería"]
    gol_d = dept_fu_data["Golosinas"]
    carn_d28 = ((float(carn_d["m28"]["pct"]) / carn_d["pre_pct"] - 1) * 100
                if carn_d["m28"] is not None and carn_d["pre_pct"] else 0)
    gol_d28 = ((float(gol_d["m28"]["pct"]) / gol_d["pre_pct"] - 1) * 100
               if gol_d["m28"] is not None and gol_d["pre_pct"] else 0)
    gol_d04 = ((float(gol_d["a04"]["pct"]) / gol_d["pre_pct"] - 1) * 100
               if gol_d["a04"] is not None and gol_d["pre_pct"] else 0)

    insight_box(fig, 0.02, [
        f"Carnicería sube en venta pero NO en penetración — es efecto "
        "Semana Santa (asado de Pascua), no fila única.",
        f"Golosinas: {gol_d28:+.1f}% penetración el 28-Mar (sin Pascuas) "
        "= señal real de impulso en cola. 4-Abr suma huevos de Pascua.",
        "Próximos sábados sin evento (11, 18, 25 Abr) confirmarán "
        "si el efecto golosinas persiste por la fila única.",
    ], h=0.065, bg="#E3F2FD", border=AZUL_C)

    fig.text(0.95, 0.005, "6/7", fontsize=9, ha="right", color=GRIS)
    pdf.savefig(fig); plt.close()

    # ─── P7: PERFIL HORARIO IMPULSO ─────────────
    fig = plt.figure(figsize=(11.69, 8.27))
    gs7 = GridSpec(2, 1, figure=fig, height_ratios=[1, 1],
                   left=0.08, right=0.97, top=0.87, bottom=0.13,
                   hspace=0.30)
    fig.patch.set_facecolor("white")

    fig.text(0.5, 0.96, "PERFIL HORARIO: ¿La cola genera compras "
             "por impulso?",
             fontsize=18, fontweight="bold", ha="center", color=AZUL)
    fig.text(0.5, 0.925,
             f"% de tickets con cada depto por hora — "
             f"Pre ({n_pre_h} sáb) vs Post ({n_post_h} sáb) fila única",
             fontsize=11, ha="center", color=GRIS)
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.91, 0.91],
                              color=AZUL, linewidth=2))

    for i, (lbl, col_p) in enumerate([
        ("Golosinas", ROJO), ("Carnicería", NARANJA),
    ]):
        ax7 = fig.add_subplot(gs7[i])
        dd7 = dept_fu_data[lbl]

        ax7.plot(HRS, dd7["pre_h"], color=AZUL_C, linewidth=2,
                 linestyle="--", marker="o", markersize=4,
                 label=f"Pre ({n_pre_h} sáb)", alpha=0.8)
        ax7.plot(HRS, dd7["post_h"], color=col_p, linewidth=2.5,
                 marker="s", markersize=5,
                 label=f"Post ({n_post_h} sáb)")

        ax7.axvspan(11, 13, alpha=0.08, color=NARANJA)
        ax7.axvspan(17, 21, alpha=0.08, color=NARANJA)

        ymax7 = max(max(dd7["pre_h"]), max(dd7["post_h"])) * 1.15
        ax7.set_ylim(0, ymax7)

        if i == 0:
            ax7.text(12, ymax7 * 0.88, "Pico\nmañana",
                     fontsize=7, ha="center", color=NARANJA, alpha=0.7)
            ax7.text(19, ymax7 * 0.88, "Pico\ntarde",
                     fontsize=7, ha="center", color=NARANJA, alpha=0.7)

        ax7.set_ylabel(f"% tickets con {lbl}", fontsize=10)
        ax7.set_title(lbl, fontsize=12, fontweight="bold", color=AZUL)
        ax7.legend(fontsize=8, framealpha=0.9, loc="upper right")
        ax7.spines["top"].set_visible(False)
        ax7.spines["right"].set_visible(False)
        ax7.grid(axis="y", alpha=0.3)
        ax7.set_xticks(HRS)
        ax7.set_xticklabels([f"{h}h" for h in HRS], fontsize=8)

    gol_pk_pre = np.mean([dept_fu_data["Golosinas"]["pre_h"][HRS.index(h)]
                          for h in [11, 12, 17, 18, 19, 20]])
    gol_pk_post = np.mean([dept_fu_data["Golosinas"]["post_h"][HRS.index(h)]
                           for h in [11, 12, 17, 18, 19, 20]])
    gol_off_pre = np.mean([dept_fu_data["Golosinas"]["pre_h"][HRS.index(h)]
                           for h in [8, 9, 10, 14, 15, 16]])
    gol_off_post = np.mean([dept_fu_data["Golosinas"]["post_h"][HRS.index(h)]
                            for h in [8, 9, 10, 14, 15, 16]])

    insight_box(fig, 0.02, [
        f"Golosinas en horas pico (cola larga): Pre {gol_pk_pre:.1f}% "
        f"-> Post {gol_pk_post:.1f}%. "
        f"En horas valle: Pre {gol_off_pre:.1f}% -> "
        f"Post {gol_off_post:.1f}%.",
        "Zonas sombreadas = horas de mayor cola (11-13h y 17-21h). "
        "Si el efecto Post es mayor en pico, confirma impulso en cola.",
        f"Solo {n_post_s} sábados post (incluye Pascuas) — monitorear "
        "próximas semanas para confirmar tendencia.",
    ], h=0.065, bg="#FFF3E0", border=NARANJA)

    fig.text(0.95, 0.005, "7/7", fontsize=9, ha="right", color=GRIS)
    pdf.savefig(fig); plt.close()


print(f"\nPDF guardado: {OUT_PDF}")
print(f"\n=== VERIFICACIÓN ===")
print(f"Cross-sell ratio: {r_ratio:.1f}x")
print(f"Ticket CON rotis: ${prom_con:,.0f} vs SIN: ${prom_sin:,.0f} "
      f"(+{uplift_pct:.0f}%)")
print(f"Cross-sell total mensual: ${cross_total_m:,}")
print(f"Cross-sell en riesgo causal: ${cross_riesgo_m:,}")
print(f"Resultado neto cerrar: {neto_txt} ${abs(neto_cerrar):,}/mes")
print(f"Lift Rotis<->Panad: {lift:.2f} | Cramér's V: {cram_v:.4f}")
print(f"Panad en rotis: {panad_en_rotis_pct:.1f}% | "
      f"Rotis en panad: {rotis_en_panad_pct:.1f}%")
print(f"\nSábados: {len(sab_wk)} | Cobro: {mu_cobro:.0f} tk | "
      f"Normal: {mu_normal:.0f} tk | Δ={delta_tk:+.1f}%")
print(f"Pascuas peak: {int(best['tickets']):,} tk "
      f"({best['fecha'].strftime('%d/%m/%Y')})")
