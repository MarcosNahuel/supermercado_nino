import sys
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from pipeline import Settings, load_settings  # type: ignore


APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent  # Go up one level from app/ to project root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


st.set_page_config(
    page_title="Supermercado NINO - Rentabilidad del Ticket",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("Supermercado NINO - Rentabilidad del Ticket")
st.caption("Pipeline reproducible + dashboard para monitorear KPIs de rentabilidad en POS")


@st.cache_data(show_spinner=False, ttl=60)  # Reduced TTL to force reload
def get_settings() -> Settings:
    return load_settings(PROJECT_ROOT / "config" / "settings.yaml")


def load_tickets(path: Path) -> pd.DataFrame:  # Cache disabled temporarily
    df = pd.read_csv(
        path,
        parse_dates=["fecha"],
        dtype={
            "ticket_id": str,
            "departamentos": str,
            "medios_pago": str,
            "emisores": str,
        },
    )
    df["fecha_date"] = pd.to_datetime(df["fecha_date"])
    return df


@st.cache_data(show_spinner=True, ttl=3600)
def load_items(path: Path, usecols: Iterable[str]) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        usecols=list(usecols),
        parse_dates=["fecha"],
        dtype={"ticket_id": str, "departamento": str, "producto": str, "producto_id": str},
    )
    df["medio_pago"] = df["medio_pago"].fillna("SIN_DATOS")
    df["emisor"] = df["emisor"].fillna("SIN_EMISOR")
    return df


@st.cache_data(show_spinner=False, ttl=3600)
def load_data_dictionary(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def explode_unique(values: pd.Series) -> List[str]:
    unique: set[str] = set()
    for entry in values.fillna(""):
        for token in str(entry).split(","):
            token = token.strip()
            if token and token not in {"SIN_DATOS", "SIN_EMISOR"}:
                unique.add(token)
    return sorted(unique)


def apply_ticket_filters(
    df: pd.DataFrame,
    date_range: Tuple[pd.Timestamp, pd.Timestamp],
    departamentos: List[str],
    medios_pago: List[str],
    emisores: List[str],
) -> pd.DataFrame:
    mask = (df["fecha_date"] >= date_range[0]) & (df["fecha_date"] <= date_range[1])

    if departamentos:
        mask &= df["departamentos"].fillna("").apply(
            lambda x: any(
                dep in {token.strip() for token in x.split(",") if token.strip()}
                for dep in departamentos
            )
        )

    if medios_pago:
        mask &= df["medios_pago"].fillna("").apply(
            lambda x: any(
                med in {token.strip() for token in x.split(",") if token.strip()}
                for med in medios_pago
            )
        )

    if emisores:
        mask &= df["emisores"].fillna("").apply(
            lambda x: any(
                emi in {token.strip() for token in x.split(",") if token.strip()}
                for emi in emisores
            )
        )

    return df.loc[mask].copy()


def filter_items(
    items: pd.DataFrame,
    tickets: pd.DataFrame,
    departamentos: List[str],
    medios: List[str],
    emisores: List[str],
) -> pd.DataFrame:
    if tickets.empty:
        return items.iloc[0:0]

    ticket_ids = tickets["ticket_id"].unique()
    filtered = items[items["ticket_id"].isin(ticket_ids)].copy()

    if departamentos:
        filtered = filtered[filtered["departamento"].isin(departamentos)]
    if medios:
        filtered = filtered[filtered["medio_pago"].isin(medios)]
    if emisores:
        filtered = filtered[filtered["emisor"].isin(emisores) | (filtered["medio_pago"] == "EFECTIVO")]

    return filtered


def kpi_cards(df: pd.DataFrame) -> None:
    total_ventas = df["ventas"].sum()
    total_margen = df["margen_est"].sum()
    total_tickets = len(df)
    ticket_promedio = total_ventas / total_tickets if total_tickets else 0
    margen_promedio_ticket = total_margen / total_tickets if total_tickets else 0
    margen_pct = (total_margen / total_ventas) if total_ventas else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Ventas totales", f"${total_ventas:,.0f}")
    col2.metric("Margen estimado", f"${total_margen:,.0f}", f"{margen_pct*100:,.1f}%")
    col3.metric("Tickets", f"{total_tickets:,}")
    col4.metric("Ticket promedio", f"${ticket_promedio:,.0f}")
    col5.metric("Margen por ticket", f"${margen_promedio_ticket:,.0f}")


def timeseries_plot(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = px.line(df, x=x, y=y, markers=True, title=title)
    fig.update_traces(mode="lines+markers")
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def build_cycle_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    grouped = (
        df.groupby(group_col)
        .agg(
            ventas=("ventas", "sum"),
            margen_est=("margen_est", "sum"),
            tickets=("ticket_id", "nunique"),
        )
        .reset_index()
    )
    grouped["ticket_promedio"] = np.where(grouped["tickets"] > 0, grouped["ventas"] / grouped["tickets"], np.nan)
    grouped["margen_promedio_ticket"] = np.where(
        grouped["tickets"] > 0,
        grouped["margen_est"] / grouped["tickets"],
        np.nan,
    )
    return grouped


def compute_pareto(df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
    if df.empty:
        return df
    grouped = (
        df.groupby(group_cols)
        .agg(
            ventas=("importe_total", "sum"),
            margen_est=("margen_est_linea", "sum"),
            unidades=("cantidad", "sum"),
        )
        .reset_index()
        .sort_values("margen_est", ascending=False)
    )
    total_margen = grouped["margen_est"].sum()
    grouped["participacion_margen"] = np.where(total_margen > 0, grouped["margen_est"] / total_margen, 0)
    grouped["acumulado_margen"] = grouped["participacion_margen"].cumsum()
    grouped["abc"] = np.select(
        [
            grouped["acumulado_margen"] <= 0.8,
            grouped["acumulado_margen"] <= 0.95,
        ],
        ["A", "B"],
        default="C",
    )
    return grouped


def pareto_chart(df: pd.DataFrame, title: str, top_n: int = 20) -> go.Figure:
    df_top = df.head(top_n)
    fig = go.Figure()
    fig.add_bar(
        x=df_top["producto"],
        y=df_top["margen_est"],
        name="Margen estimado",
        marker_color="#1f77b4",
    )
    fig.add_scatter(
        x=df_top["producto"],
        y=df_top["acumulado_margen"],
        name="Acumulado margen",
        yaxis="y2",
        mode="lines+markers",
        marker_color="#ff7f0e",
    )
    fig.update_layout(
        title=title,
        yaxis=dict(title="Margen estimado"),
        yaxis2=dict(title="Acumulado", overlaying="y", side="right", range=[0, 1]),
        xaxis_tickangle=-45,
        margin=dict(l=20, r=40, t=60, b=120),
    )
    return fig


def medios_pago_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    fig = px.bar(
        df,
        x="medio_pago",
        y="ventas",
        color="medio_pago",
        hover_data=["margen_est", "ticket_promedio"],
        title="Ventas por medio de pago (rango seleccionado)",
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=60, b=10))
    return fig


def main() -> None:
    settings = get_settings()
    processed_dir = settings.processed_dir

    tickets = load_tickets(processed_dir / "tickets.csv")
    items = load_items(
        processed_dir / "items.csv",
        usecols=[
            "ticket_id",
            "fecha",
            "producto_id",
            "producto",
            "departamento",
            "importe_total",
            "margen_est_linea",
            "cantidad",
            "medio_pago",
            "emisor",
            "mes_str",
            "semana_iso",
            "weekday_name",
        ],
    )
    data_dict = load_data_dictionary(processed_dir / "data_dictionary.csv")

    date_min = tickets["fecha_date"].min()
    date_max = tickets["fecha_date"].max()

    departamentos = explode_unique(tickets["departamentos"])
    medios_pago = explode_unique(tickets["medios_pago"])
    emisores = explode_unique(tickets["emisores"])

    st.sidebar.header("Filtros")
    selected_dates = st.sidebar.date_input(
        "Rango de fechas",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )
    if isinstance(selected_dates, tuple):
        start_date, end_date = selected_dates
    else:
        start_date = selected_dates
        end_date = selected_dates

    selected_departamentos = st.sidebar.multiselect(
        "Departamentos",
        options=departamentos,
        default=departamentos,
    )
    selected_medios = st.sidebar.multiselect(
        "Medios de pago",
        options=medios_pago,
        default=medios_pago,
    )
    selected_emisores = st.sidebar.multiselect(
        "Emisores",
        options=emisores,
        default=emisores,
    )

    filtered_tickets = apply_ticket_filters(
        tickets,
        (pd.Timestamp(start_date), pd.Timestamp(end_date)),
        selected_departamentos,
        selected_medios,
        selected_emisores,
    )
    filtered_items = filter_items(items, filtered_tickets, selected_departamentos, selected_medios, selected_emisores)

    if filtered_tickets.empty:
        st.warning("No hay tickets para los filtros seleccionados. Ajusta los filtros en el panel lateral.")
        return

    st.subheader("KPIs de Rentabilidad")
    kpi_cards(filtered_tickets)

    col_ticket, col_margen = st.columns(2)
    with col_ticket:
        st.metric(
            "Desvio estandar del ticket",
            f"${filtered_tickets['ventas'].std(ddof=0):,.0f}",
        )
    with col_margen:
        st.metric(
            "Desvio estandar del margen",
            f"${filtered_tickets['margen_est'].std(ddof=0):,.0f}",
        )

    tab_overview, tab_pareto, tab_medios, tab_descargas = st.tabs(
        ["Vision general", "Pareto de productos", "Medios de pago", "Descargas & diccionario"]
    )

    with tab_overview:
        st.markdown("### Ciclos temporales")
        monthly = build_cycle_summary(filtered_tickets, "mes_str").sort_values("mes_str")
        weekly = build_cycle_summary(filtered_tickets, "semana_iso").sort_values("semana_iso")
        daily = build_cycle_summary(filtered_tickets, "fecha_date").sort_values("fecha_date")

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(timeseries_plot(monthly, "mes_str", "ticket_promedio", "Ticket promedio por mes"), use_container_width=True)
        with col2:
            st.plotly_chart(timeseries_plot(monthly, "mes_str", "margen_promedio_ticket", "Margen por ticket (mensual)"), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(timeseries_plot(weekly, "semana_iso", "ticket_promedio", "Ticket promedio por semana ISO"), use_container_width=True)
        with col4:
            st.plotly_chart(timeseries_plot(daily, "fecha_date", "ventas", "Ventas diarias"), use_container_width=True)

        st.markdown("### Distribucion de tickets")
        hist_fig = px.histogram(
            filtered_tickets,
            x="ventas",
            nbins=30,
            title="Distribucion del importe por ticket",
            labels={"ventas": "Importe del ticket"},
        )
        hist_fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(hist_fig, use_container_width=True)

    with tab_pareto:
        st.markdown("### Pareto global (margen estimado)")
        pareto_global = compute_pareto(filtered_items, ["producto_id", "producto", "departamento"])
        if pareto_global.empty:
            st.info("No hay datos para calcular el Pareto con los filtros aplicados.")
        else:
            st.plotly_chart(
                pareto_chart(pareto_global, "Pareto global de margen (Top 20)"),
                use_container_width=True,
            )
            st.dataframe(pareto_global.head(20), use_container_width=True)

        st.markdown("### Pareto por mes")
        pareto_month = compute_pareto(filtered_items, ["mes_str", "producto_id", "producto", "departamento"])
        if not pareto_month.empty:
            selected_mes = st.selectbox(
                "Selecciona un mes",
                options=sorted(pareto_month["mes_str"].unique()),
            )
            para_mes_df = pareto_month[pareto_month["mes_str"] == selected_mes]
            st.plotly_chart(
                pareto_chart(para_mes_df, f"Pareto {selected_mes} (Top 20)"),
                use_container_width=True,
            )
            st.dataframe(para_mes_df.head(20), use_container_width=True)

        st.markdown("### Pareto por semana ISO")
        pareto_week = compute_pareto(filtered_items, ["semana_iso", "producto_id", "producto", "departamento"])
        if not pareto_week.empty:
            selected_week = st.selectbox(
                "Selecciona una semana ISO",
                options=sorted(pareto_week["semana_iso"].unique()),
            )
            para_week_df = pareto_week[pareto_week["semana_iso"] == selected_week]
            st.plotly_chart(
                pareto_chart(para_week_df, f"Pareto semana {selected_week} (Top 20)"),
                use_container_width=True,
            )
            st.dataframe(para_week_df.head(20), use_container_width=True)

    with tab_medios:
        medios_df = (
            filtered_items.groupby(["medio_pago", "emisor"])
            .agg(
                tickets=("ticket_id", "nunique"),
                ventas=("importe_total", "sum"),
                margen_est=("margen_est_linea", "sum"),
            )
            .reset_index()
        )
        if medios_df.empty:
            st.info("No hay operaciones con los filtros seleccionados.")
        else:
            medios_df["ticket_promedio"] = np.where(
                medios_df["tickets"] > 0,
                medios_df["ventas"] / medios_df["tickets"],
                np.nan,
            )
            st.plotly_chart(medios_pago_chart(medios_df), use_container_width=True)
            st.dataframe(medios_df.sort_values("ventas", ascending=False), use_container_width=True)

    with tab_descargas:
        st.markdown("### Descargas")
        st.download_button(
            "Descargar tickets filtrados (.csv)",
            filtered_tickets.to_csv(index=False).encode("utf-8"),
            file_name="tickets_filtrados.csv",
        )
        st.download_button(
            "Descargar lineas filtradas (.csv)",
            filtered_items.to_csv(index=False).encode("utf-8"),
            file_name="items_filtrados.csv",
        )
        st.markdown("### Diccionario de datos")
        st.dataframe(data_dict, use_container_width=True)


if __name__ == "__main__":
    main()
