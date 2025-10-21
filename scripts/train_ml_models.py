"""Train and execute ML-based ROI simulators for Supermercado NINO."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ml_models import StrategyValidator  # noqa: E402


def _load_dataset(path: Path, description: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró {description}: {path}")
    return pd.read_parquet(path)


def run_training(base_dir: Path) -> None:
    processed_dir = base_dir / "data" / "processed"

    print("ENTRENAMIENTO DE MODELOS ML - ROI DE ESTRATEGIAS")
    print("=================================================\n")
    print(f"Directorio base: {base_dir}")

    tickets_path = processed_dir / "clusters_tickets.parquet"
    detalle_path = processed_dir / "detalle_lineas.parquet"
    reglas_path = processed_dir / "reglas.parquet"
    pareto_path = processed_dir / "pareto_categoria.parquet"

    print("1. Cargando datasets procesados...")
    tickets = _load_dataset(tickets_path, "clusters de tickets")
    detalle = _load_dataset(detalle_path, "detalle de líneas")
    reglas = _load_dataset(reglas_path, "reglas de asociación")
    pareto = _load_dataset(pareto_path, "pareto de categorías")
    print(f"   ✓ Tickets: {len(tickets):,} registros")
    print(f"   ✓ Detalle líneas: {len(detalle):,} registros")
    print(f"   ✓ Reglas de asociación: {len(reglas):,} reglas")
    print(f"   ✓ Pareto categorías: {len(pareto):,} filas\n")

    validator = StrategyValidator()

    print("2. Ejecutando modelos ML...")
    summary_df, details = validator.run_all_strategies(tickets, detalle, reglas, pareto)
    baseline_metrics = summary_df.attrs.get("baseline_metrics", {})
    print("   ✓ Modelos ejecutados exitosamente\n")

    output_dir = base_dir / "data" / "ml_results"
    print(f"3. Exportando resultados a {output_dir} ...")
    validator.export_results(summary_df, details, output_dir=output_dir)
    print("   ✓ Archivos generados:")
    print("     - strategy_roi_summary.parquet")
    print("     - strategy_roi_details.json\n")

    print("4. Resumen consolidado de ROI:\n")
    display_df = summary_df.copy()
    display_df["ROI %"] = display_df["ROI %"].map(lambda v: f"{v:,.0f}%")
    display_df["Payback (meses)"] = display_df["Payback (meses)"].map(lambda v: f"{v:.2f}")
    display_df["Confianza"] = display_df["Confianza"].map(lambda v: f"{v:.0f}%")
    print(display_df.to_string(index=False))

    if baseline_metrics:
        print("\n5. Diagnóstico modelo base (TicketPredictor):")
        for metric, value in baseline_metrics.items():
            print(f"   - {metric}: {value:.4f}")

    print("\nProceso finalizado. Los resultados ya pueden consumirse en el dashboard (pestaña ML).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Entrena los modelos ML y actualiza los resultados de ROI de estrategias."
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=PROJECT_ROOT,
        help="Directorio raíz del proyecto (default: repo actual).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_training(args.base_dir.resolve())
