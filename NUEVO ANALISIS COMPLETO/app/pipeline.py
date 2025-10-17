import csv
import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


@dataclass
class Settings:
    raw_items: Path
    rentabilidad_por_departamento: Path
    processed_dir: Path
    reports_dir: Path
    currency: str
    date_column: str
    ticket_column: str
    department_column: str
    medio_pago_column: str
    emisor_column: str
    rentabilidad_default_pct: float
    medios_pago_start: pd.Timestamp
    medios_pago_end: pd.Timestamp


READ_ENCODES = ("utf-8", "latin1")
DATE_FEATURES = ("anio", "mes", "dia", "mes_str", "semana_iso", "weekday", "weekday_name", "hora")
WEEKDAY_LABELS = {
    0: "LUNES",
    1: "MARTES",
    2: "MIERCOLES",
    3: "JUEVES",
    4: "VIERNES",
    5: "SABADO",
    6: "DOMINGO",
}
MEDIO_MAP: Dict[str, str] = {
    "": "EFECTIVO",
    "EFECTIVO": "EFECTIVO",
    "EFECT": "EFECTIVO",
    "EFECTIVO REPUESTO": "EFECTIVO",
    "EFECTIVO DEVOLUCION": "EFECTIVO",
    "TARJETA": "CREDITO",
    "TARJETA DE CREDITO": "CREDITO",
    "TARJETA DE CREDITO VISA": "CREDITO",
    "TARJETA DE CREDITO MASTERCARD": "CREDITO",
    "TARJETA DE CREDITO AMERICAN EXPRESS": "CREDITO",
    "TARJETA DE CREDITO NARANJA": "CREDITO",
    "TARJETA DE CREDITO NARANJA VISA": "CREDITO",
    "TARJETA DE DEBITO": "DEBITO",
    "TARJETA DEBITO": "DEBITO",
    "TARJETA DEBITO VISA": "DEBITO",
    "TARJETA DEBITO MASTERCARD": "DEBITO",
    "VISA DEBITO": "DEBITO",
    "MASTERCARD DEBITO": "DEBITO",
    "DEBITO VISA": "DEBITO",
    "DEBITO MASTERCARD": "DEBITO",
    "BILLETERA": "BILLETERA",
    "BILLETERA VIRTUAL": "BILLETERA",
    "BILLETERA VITUAL": "BILLETERA",
    "MERCADO PAGO": "BILLETERA",
    "MP": "BILLETERA",
    "TRANSFERENCIA": "TRANSFERENCIA",
    "CHEQUE": "CHEQUE",
    "VALE": "VALE",
}


def load_settings(settings_path: Path) -> Settings:
    with settings_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    paths = raw.get("paths", {})
    settings = raw.get("settings", {})

    processed_dir = Path(paths["processed_dir"]).resolve()
    reports_dir = Path(paths.get("reports_dir", "reports")).resolve()

    medios_pago_period = settings.get("medios_pago_period", {})
    medios_pago_start = pd.Timestamp(medios_pago_period.get("start"))
    medios_pago_end = pd.Timestamp(medios_pago_period.get("end"))

    return Settings(
        raw_items=Path(paths["raw_items"]).resolve(),
        rentabilidad_por_departamento=Path(paths["rentabilidad_por_departamento"]).resolve(),
        processed_dir=processed_dir,
        reports_dir=reports_dir,
        currency=settings.get("currency", "ARS"),
        date_column=settings.get("date_column", "fecha"),
        ticket_column=settings.get("ticket_column", "ticket_id"),
        department_column=settings.get("department_column", "departamento"),
        medio_pago_column=settings.get("medio_pago_column", "medio_pago"),
        emisor_column=settings.get("emisor_column", "emisor"),
        rentabilidad_default_pct=float(settings.get("rentabilidad_default_pct", 0.12)),
        medios_pago_start=medios_pago_start,
        medios_pago_end=medios_pago_end,
    )


def read_csv_with_fallback(path: Path, **kwargs) -> pd.DataFrame:
    last_exception: Optional[Exception] = None
    for encoding in READ_ENCODES:
        try:
            df = pd.read_csv(path, encoding=encoding, **kwargs)
            logging.info("Loaded %s with encoding=%s (%s rows)", path.name, encoding, len(df))
            return df
        except UnicodeDecodeError as exc:
            last_exception = exc
            logging.warning("Failed to read %s with encoding=%s", path.name, encoding)
        except pd.errors.ParserError as exc:
            logging.warning("ParserError with encoding=%s using C engine. Retrying with python engine.", encoding)
            try:
                python_kwargs = dict(kwargs)
                python_kwargs.pop("low_memory", None)
                python_kwargs.setdefault("on_bad_lines", "warn")
                python_kwargs.setdefault("quoting", csv.QUOTE_NONE)
                df = pd.read_csv(path, encoding=encoding, engine="python", **python_kwargs)
                logging.info(
                    "Loaded %s with encoding=%s using python engine (%s rows)",
                    path.name,
                    encoding,
                    len(df),
                )
                return df
            except Exception as inner_exc:  # pragma: no cover - edge fallback
                last_exception = inner_exc
                logging.error(
                    "Failed to read %s with python engine (encoding=%s): %s",
                    path.name,
                    encoding,
                    inner_exc,
                )
        except Exception as exc:  # pragma: no cover - defensive
            last_exception = exc
            logging.error("Unexpected error reading %s: %s", path.name, exc)
    raise last_exception or RuntimeError(f"No se pudo leer {path}")


def normalize_column_name(name: str) -> str:
    name = str(name).strip()
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_").lower()


def normalize_text_value(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in value if not unicodedata.combining(ch))


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    column_map = {col: normalize_column_name(col) for col in df.columns}
    df = df.rename(columns=column_map)

    preferred_names = {
        "fecha": "fecha",
        "comprobante": "ticket_id",
        "codigo": "producto_id",
        "codigo_barras": "codigo_barras",
        "codigo_barra": "codigo_barras",
        "marca": "marca",
        "departamento": "departamento",
        "nombre": "producto",
        "cantidad": "cantidad",
        "importe": "importe_total",
        "unitario": "precio_unitario",
        "tipo_factura": "tipo_factura",
        "tipo_medio_de_pago": "medio_pago",
        "medio_de_pago": "medio_pago",
        "emisor_tarjeta": "emisor",
    }

    df = df.rename(columns={old: new for old, new in preferred_names.items() if old in df.columns})
    return df


def clean_items(df: pd.DataFrame, settings: Settings) -> Tuple[pd.DataFrame, Dict[str, float], int]:
    ticket_col = settings.ticket_column
    medio_col = settings.medio_pago_column
    emisor_col = settings.emisor_column

    df = df.copy()
    df[ticket_col] = (
        df.get(ticket_col, "")
        .astype(str)
        .str.replace('"', "", regex=False)
        .str.strip()
    )

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    numeric_cols = ["cantidad", "importe_total", "precio_unitario"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["cantidad"] = df["cantidad"].fillna(0.0)
    df["importe_total"] = df["importe_total"].fillna(0.0)
    df["precio_unitario"] = df["precio_unitario"].fillna(
        df["importe_total"].div(df["cantidad"].replace(0, np.nan))
    )

    for text_col in ["producto_id", "codigo_barras", "marca", "departamento", "producto", medio_col, emisor_col, "tipo_factura"]:
        if text_col in df.columns:
            df[text_col] = (
                df[text_col]
                .fillna("")
                .astype(str)
                .str.replace('"', "", regex=False)
                .str.replace("'", "", regex=False)
                .str.strip()
                .str.upper()
                .map(normalize_text_value)
            )

    df["departamento"] = df["departamento"].replace("", np.nan)
    df["producto"] = df["producto"].replace("", np.nan)
    df[medio_col] = df[medio_col].replace("", np.nan)
    df[emisor_col] = df[emisor_col].replace("", np.nan)

    df[medio_col] = df[medio_col].fillna("EFECTIVO")
    df[medio_col] = df[medio_col].apply(lambda x: MEDIO_MAP.get(x, x))
    df[medio_col] = df[medio_col].replace("", "EFECTIVO")

    df[emisor_col] = df[emisor_col].fillna("SIN_EMISOR")
    df.loc[df[medio_col] == "EFECTIVO", emisor_col] = "SIN_EMISOR"

    diff = (df["cantidad"] * df["precio_unitario"]) - df["importe_total"]
    df["importe_diff"] = diff.round(2)

    duplicates = df.duplicated(subset=["fecha", ticket_col, "producto_id", "codigo_barras", "importe_total"], keep=False).sum()

    null_pct = (
        df[["fecha", ticket_col, "producto_id", "departamento", "importe_total"]]
        .isna()
        .mean()
        .to_dict()
    )

    return df, null_pct, int(duplicates)


def enrich_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fecha_date"] = df["fecha"].dt.date
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["dia"] = df["fecha"].dt.day
    df["mes_str"] = df["fecha"].dt.to_period("M").astype(str)
    df["hora"] = df["fecha"].dt.hour.fillna(0).astype(int)

    iso = df["fecha"].dt.isocalendar()
    df["semana_iso"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    df["weekday"] = df["fecha"].dt.dayofweek
    df["weekday_name"] = df["weekday"].map(WEEKDAY_LABELS)

    return df


def load_rentabilidad(path: Path) -> pd.DataFrame:
    rent = read_csv_with_fallback(path, sep=",", decimal=".", dtype=str)
    rent = standardize_columns(rent)
    if "%_rentabilidad" in rent.columns:
        rent_col = "%_rentabilidad"
    elif "rentabilidad" in rent.columns:
        rent_col = "rentabilidad"
    else:
        rent_col = "rentabilidad_pct"

    rent[rent_col] = (
        rent[rent_col]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    rent["rentabilidad_pct"] = pd.to_numeric(rent[rent_col], errors="coerce") / 100
    rent = rent.rename(columns={"departamento": "departamento"})
    rent["departamento"] = rent["departamento"].fillna("").str.upper().str.strip()
    return rent[["departamento", "rentabilidad_pct"]]


def apply_rentabilidad(items: pd.DataFrame, rent: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    items = items.copy()
    items = items.merge(rent, on="departamento", how="left")
    items["rentabilidad_fuente"] = np.where(items["rentabilidad_pct"].isna(), "DEFAULT", "MAPA")
    items["rentabilidad_pct"] = items["rentabilidad_pct"].fillna(settings.rentabilidad_default_pct)
    items["margen_est_linea"] = items["importe_total"] * items["rentabilidad_pct"]
    items["margen_unitario_est"] = items["margen_est_linea"] / items["cantidad"].replace(0, np.nan)
    items["margen_unitario_est"] = items["margen_unitario_est"].fillna(items["precio_unitario"] * items["rentabilidad_pct"])
    return items


def build_tickets(items: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    grp_cols = [settings.ticket_column]
    agg = items.groupby(grp_cols).agg(
        fecha=("fecha", "min"),
        fecha_date=("fecha_date", "min"),
        ventas=("importe_total", "sum"),
        margen_est=("margen_est_linea", "sum"),
        unidades=("cantidad", "sum"),
        departamentos=("departamento", lambda x: ",".join(sorted({val for val in x if isinstance(val, str) and val})) or "SIN_DATOS"),
        medios_pago=(settings.medio_pago_column, lambda x: ",".join(sorted({val for val in x if isinstance(val, str) and val})) or "SIN_DATOS"),
        emisores=(settings.emisor_column, lambda x: ",".join(sorted({val for val in x if isinstance(val, str) and val})) or "SIN_DATOS"),
        lineas=("producto_id", "count"),
    )
    agg["ticket_promedio_unidades"] = agg["unidades"] / agg["lineas"].replace(0, np.nan)
    agg["margen_pct_ticket"] = np.where(
        agg["ventas"] > 0,
        agg["margen_est"] / agg["ventas"],
        np.nan,
    )

    agg = enrich_time_features(agg.reset_index())
    return agg


def _cycle_template() -> Dict[str, Tuple[str, str]]:
    return {
        "anio": ("anio", "kpi_ciclos_anual.csv"),
        "mes_str": ("mes_str", "kpi_ciclos_mensual.csv"),
        "semana_iso": ("semana_iso", "kpi_ciclos_semanal.csv"),
        "fecha_date": ("fecha_date", "kpi_ciclos_diario.csv"),
    }


def build_cycle_kpis(tickets: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    cycles = {}
    template = _cycle_template()
    for label, (column, filename) in template.items():
        grouped = (
            tickets.groupby(column)
            .agg(
                tickets=("ticket_id", "nunique"),
                ventas=("ventas", "sum"),
                margen_est=("margen_est", "sum"),
                unidades=("unidades", "sum"),
            )
            .reset_index()
        )
        grouped["ticket_promedio"] = np.where(grouped["tickets"] > 0, grouped["ventas"] / grouped["tickets"], np.nan)
        grouped["margen_promedio_ticket"] = np.where(
            grouped["tickets"] > 0,
            grouped["margen_est"] / grouped["tickets"],
            np.nan,
        )

        merged = tickets.merge(grouped[[column, "ticket_promedio"]], on=column, how="left")
        desvio = merged.groupby(column)["ventas"].std(ddof=0).reset_index(name="desvio_ticket")
        desvio_margen = merged.groupby(column)["margen_est"].std(ddof=0).reset_index(name="desvio_margen")
        grouped = grouped.merge(desvio, on=column, how="left").merge(desvio_margen, on=column, how="left")

        cycles[filename] = grouped
    return cycles


def pareto_global(items: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        items.groupby(["producto_id", "producto", "departamento"], dropna=False)
        .agg(
            ventas=("importe_total", "sum"),
            margen_est=("margen_est_linea", "sum"),
            unidades=("cantidad", "sum"),
            tickets=("ticket_id", "nunique"),
        )
        .reset_index()
    )
    grouped = grouped.sort_values("margen_est", ascending=False)
    total_margen = grouped["margen_est"].sum()
    total_ventas = grouped["ventas"].sum()
    grouped["participacion_margen"] = np.where(total_margen > 0, grouped["margen_est"] / total_margen, 0)
    grouped["participacion_venta"] = np.where(total_ventas > 0, grouped["ventas"] / total_ventas, 0)
    grouped["acumulado_margen"] = grouped["participacion_margen"].cumsum()
    grouped["abc_margen"] = np.select(
        [
            grouped["acumulado_margen"] <= 0.8,
            grouped["acumulado_margen"] <= 0.95,
        ],
        ["A", "B"],
        default="C",
    )
    return grouped


def pareto_by_period(items: pd.DataFrame, period_col: str) -> pd.DataFrame:
    grouped = (
        items.groupby([period_col, "producto_id", "producto", "departamento"], dropna=False)
        .agg(
            ventas=("importe_total", "sum"),
            margen_est=("margen_est_linea", "sum"),
            unidades=("cantidad", "sum"),
            tickets=("ticket_id", "nunique"),
        )
        .reset_index()
    )

    def compute_rank(df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values("margen_est", ascending=False)
        total = df["margen_est"].sum()
        total_ventas = df["ventas"].sum()
        df["participacion_margen"] = np.where(total > 0, df["margen_est"] / total, 0)
        df["participacion_venta"] = np.where(total_ventas > 0, df["ventas"] / total_ventas, 0)
        df["acumulado_margen"] = df["participacion_margen"].cumsum()
        df["abc_margen"] = np.select(
            [
                df["acumulado_margen"] <= 0.8,
                df["acumulado_margen"] <= 0.95,
            ],
            ["A", "B"],
            default="C",
        )
        return df

    group_obj = grouped.groupby(period_col, group_keys=False)
    try:
        grouped = group_obj.apply(compute_rank, include_groups=False)
    except TypeError:
        grouped = group_obj.apply(compute_rank)
    return grouped.reset_index(drop=True)


def medios_pago_kpis(items: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    mask = items["fecha"].between(settings.medios_pago_start, settings.medios_pago_end, inclusive="both")
    scoped = items.loc[mask].copy()
    if scoped.empty:
        return pd.DataFrame(columns=["medio_pago", "emisor", "tickets", "ventas", "margen_est"])

    medio_col = settings.medio_pago_column
    emisor_col = settings.emisor_column
    grouped = (
        scoped.groupby([medio_col, emisor_col])
        .agg(
            tickets=("ticket_id", "nunique"),
            ventas=("importe_total", "sum"),
            margen_est=("margen_est_linea", "sum"),
            unidades=("cantidad", "sum"),
        )
        .reset_index()
    )
    totals = grouped["ventas"].sum()
    total_tickets = grouped["tickets"].sum()
    grouped["ticket_promedio"] = np.where(grouped["tickets"] > 0, grouped["ventas"] / grouped["tickets"], np.nan)
    grouped["margen_promedio_ticket"] = np.where(
        grouped["tickets"] > 0,
        grouped["margen_est"] / grouped["tickets"],
        np.nan,
    )
    grouped["participacion_ventas"] = np.where(totals > 0, grouped["ventas"] / totals, 0)
    grouped["participacion_tickets"] = np.where(total_tickets > 0, grouped["tickets"] / total_tickets, 0)
    return grouped.sort_values(["medio_pago", "ventas"], ascending=[True, False])


def build_data_dictionary(items: pd.DataFrame, tickets: pd.DataFrame) -> pd.DataFrame:
    entries: List[Dict[str, str]] = []

    items_dict = {
        "fecha": "Marca temporal completa de la transaccion en POS.",
        "fecha_date": "Fecha (sin hora) de la transaccion.",
        "ticket_id": "Identificador del comprobante / ticket.",
        "producto_id": "Codigo interno del producto.",
        "codigo_barras": "Codigo de barras reportado.",
        "producto": "Nombre descriptivo del producto.",
        "marca": "Marca del producto (si aplica).",
        "departamento": "Departamento/categoria comercial.",
        "cantidad": "Unidades vendidas en la linea.",
        "precio_unitario": "Precio unitario informado.",
        "importe_total": "Importe de la linea en moneda local.",
        "rentabilidad_pct": "Porcentaje estimado de rentabilidad aplicado.",
        "margen_est_linea": "Margen estimado de la linea (importe_total * rentabilidad_pct).",
        "medio_pago": "Medio de pago normalizado.",
        "emisor": "Entidad emisora normalizada (si corresponde).",
        "semana_iso": "Semana ISO (ano-W##) de la operacion.",
        "weekday_name": "Nombre del dia de la semana en espanol.",
        "margen_unitario_est": "Margen estimado por unidad.",
    }
    for column, description in items_dict.items():
        if column in items.columns:
            entries.append({"dataset": "items", "column": column, "description": description})

    tickets_dict = {
        "ticket_id": "Identificador unico del ticket/agregado.",
        "fecha": "Fecha completa del ticket.",
        "ventas": "Ventas totales del ticket.",
        "margen_est": "Margen estimado total del ticket.",
        "unidades": "Unidades totales vendidas en el ticket.",
        "departamentos": "Departamentos presentes en el ticket (concatenados).",
        "medios_pago": "Medios de pago utilizados (concatenados).",
        "emisores": "Emisores de tarjeta utilizados (concatenados).",
        "anio": "Ano calendario del ticket.",
        "mes_str": "Mes en formato YYYY-MM.",
        "semana_iso": "Semana ISO asociada al ticket.",
        "ticket_promedio_unidades": "Promedio de unidades por linea dentro del ticket.",
        "margen_pct_ticket": "Margen estimado como % de las ventas del ticket.",
    }
    for column, description in tickets_dict.items():
        if column in tickets.columns:
            entries.append({"dataset": "tickets", "column": column, "description": description})

    return pd.DataFrame(entries)


def ensure_output_dirs(settings: Settings) -> None:
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
    logging.info("Wrote %s (%s rows)", path.name, len(df))


def main(config_path: Path = Path("config/settings.yaml")) -> None:
    settings = load_settings(config_path)
    ensure_output_dirs(settings)

    raw_items = read_csv_with_fallback(
        settings.raw_items,
        sep=";",
        decimal=",",
        dtype=str,
        low_memory=False,
    )
    raw_items = standardize_columns(raw_items)
    clean_df, null_pct, duplicates = clean_items(raw_items, settings)
    clean_df = enrich_time_features(clean_df)

    rent = load_rentabilidad(settings.rentabilidad_por_departamento)
    items = apply_rentabilidad(clean_df, rent, settings)

    tickets = build_tickets(items, settings)
    cycles = build_cycle_kpis(tickets)
    pareto_g = pareto_global(items)
    pareto_mensual = pareto_by_period(items, "mes_str")
    pareto_semanal = pareto_by_period(items, "semana_iso")
    medios_pago = medios_pago_kpis(items, settings)
    data_dict = build_data_dictionary(items, tickets)

    processed = settings.processed_dir
    write_csv(items, processed / "items.csv")
    write_csv(tickets, processed / "tickets.csv")
    for filename, df in cycles.items():
        write_csv(df, processed / filename)
    write_csv(pareto_g, processed / "pareto_global.csv")
    write_csv(pareto_mensual, processed / "pareto_mensual.csv")
    write_csv(pareto_semanal, processed / "pareto_semana.csv")

    if not medios_pago.empty:
        write_csv(medios_pago, processed / "kpi_medios_pago.csv")
    else:
        (processed / "kpi_medios_pago.csv").write_text("", encoding="utf-8")

    write_csv(data_dict, processed / "data_dictionary.csv")

    quality_summary = {
        "null_percentage": {k: float(v) for k, v in null_pct.items()},
        "duplicate_rows": duplicates,
        "importe_diff_outliers_pct": float((items["importe_diff"].abs() > 0.05).mean()),
        "rentabilidad_default_pct": settings.rentabilidad_default_pct,
    }
    quality_path = settings.reports_dir / "data_quality.json"
    quality_path.write_text(json.dumps(quality_summary, indent=2), encoding="utf-8")
    logging.info("Saved data quality summary to %s", quality_path.name)


if __name__ == "__main__":
    main()
