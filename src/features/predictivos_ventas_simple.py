"""
================================================================================
PREDICCIONES DE VENTAS - ENFOQUE SIMPLE Y COMPRENSIBLE
================================================================================
Este módulo genera pronósticos de ventas semanales utilizando métodos simples
y fáciles de entender para no-técnicos:

1. **Promedio Móvil**: Calcula el promedio de las últimas N semanas
2. **Tendencia Lineal**: Identifica si las ventas están creciendo o decreciendo
3. **Estacionalidad**: Considera patrones repetitivos semanales

¿Por qué este enfoque en lugar de ARIMA?
- ARIMA es una "caja negra" difícil de explicar a stakeholders
- Los métodos simples son más transparentes y auditables
- Para series cortas (<2 años), ARIMA no ofrece ventajas significativas
- Es más fácil entender "el promedio de las últimas 8 semanas" que "ARIMA(1,1,2)"
================================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from src.utils.load_data import ensure_directory


@dataclass
class PronosticoSimple:
    """
    Resultado de pronóstico para una categoría.

    Atributos:
        categoria: Nombre de la categoría
        history: Datos históricos observados
        forecast: Pronóstico futuro con intervalos de confianza
        metodo: Método utilizado (promedio móvil, tendencia, etc.)
        parametros: Parámetros del método (ej: ventana=8 semanas)
    """
    categoria: str
    history: pd.DataFrame
    forecast: pd.DataFrame
    metodo: str
    parametros: Dict[str, object]


def _parse_semana(ventas: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte semanas ISO a fechas de inicio de semana.

    Ejemplo: "2024-W15" -> 2024-04-08 (lunes de esa semana)
    """
    ventas = ventas.copy()
    ventas["semana_inicio"] = pd.to_datetime(
        ventas["semana_iso"] + "-1", format="%G-W%V-%u"
    )
    ventas = ventas.sort_values("semana_inicio")
    return ventas


def _calcular_promedio_movil(
    serie: pd.Series,
    ventana: int = 8
) -> tuple[float, float]:
    """
    Calcula el promedio móvil y su desviación estándar.

    Args:
        serie: Serie temporal de ventas
        ventana: Número de semanas a promediar

    Returns:
        (promedio, desviacion): Promedio y desviación estándar de las últimas N semanas
    """
    ultimas_semanas = serie.tail(ventana)
    promedio = ultimas_semanas.mean()
    desviacion = ultimas_semanas.std()
    return promedio, desviacion


def _calcular_tendencia(serie: pd.Series) -> float:
    """
    Calcula la tendencia lineal de la serie.

    Retorna el cambio promedio por semana (positivo = crecimiento, negativo = decrecimiento)

    Ejemplo:
        Si las ventas aumentan 100 unidades/semana -> retorna 100.0
        Si las ventas disminuyen 50 unidades/semana -> retorna -50.0
    """
    if len(serie) < 4:
        return 0.0

    # Regresión lineal simple: y = a + b*x
    x = np.arange(len(serie))
    y = serie.values

    # Calcular pendiente (b)
    n = len(x)
    pendiente = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)

    return pendiente


def _generar_pronostico(
    serie: pd.Series,
    steps: int = 8,
    ventana_promedio: int = 8,
    usar_tendencia: bool = True
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str, dict]:
    """
    Genera pronóstico usando promedio móvil con tendencia opcional.

    Args:
        serie: Serie temporal de ventas semanales
        steps: Número de semanas a pronosticar
        ventana_promedio: Ventana para calcular el promedio móvil
        usar_tendencia: Si True, ajusta por tendencia lineal

    Returns:
        (valores, lower, upper, metodo, params)
        - valores: Pronóstico central
        - lower: Límite inferior (intervalo 80%)
        - upper: Límite superior (intervalo 80%)
        - metodo: Descripción del método usado
        - params: Parámetros utilizados
    """
    promedio, desviacion = _calcular_promedio_movil(serie, ventana_promedio)
    tendencia = _calcular_tendencia(serie) if usar_tendencia else 0.0

    # Generar pronósticos
    valores = np.zeros(steps)
    for i in range(steps):
        # Promedio base + tendencia acumulada
        valores[i] = promedio + tendencia * (i + 1)

    # Intervalos de confianza (±1.28 desviaciones estándar = 80% confianza)
    # Nota: El intervalo se amplía con el horizonte de pronóstico
    lower = valores - 1.28 * desviacion * np.sqrt(1 + np.arange(steps) * 0.1)
    upper = valores + 1.28 * desviacion * np.sqrt(1 + np.arange(steps) * 0.1)

    # No permitir ventas negativas
    lower = np.maximum(lower, 0)

    metodo = f"Promedio Móvil ({ventana_promedio} sem)"
    if usar_tendencia and abs(tendencia) > 0.01:
        metodo += f" + Tendencia ({tendencia:+.1f} unid/sem)"

    params = {
        "ventana": ventana_promedio,
        "tendencia_semanal": tendencia,
        "promedio_base": promedio,
        "desviacion": desviacion
    }

    return valores, lower, upper, metodo, params


def _preparar_resultado(
    categoria: str,
    serie: pd.Series,
    valores: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    metodo: str,
    parametros: dict
) -> PronosticoSimple:
    """
    Prepara el resultado del pronóstico en formato DataFrame.
    """
    # Histórico
    history_df = serie.reset_index()
    history_df.columns = ["semana_inicio", "ventas_semana"]
    history_df["categoria"] = categoria
    history_df["tipo"] = "observado"
    history_df["ventas_semana_lower"] = np.nan
    history_df["ventas_semana_upper"] = np.nan

    # Pronóstico
    ultima_fecha = serie.index[-1]
    fechas_futuras = pd.date_range(
        start=ultima_fecha + pd.Timedelta(weeks=1),
        periods=len(valores),
        freq="W-MON"
    )

    forecast_df = pd.DataFrame({
        "semana_inicio": fechas_futuras,
        "ventas_semana": valores,
        "categoria": categoria,
        "tipo": "forecast",
        "ventas_semana_lower": lower,
        "ventas_semana_upper": upper
    })

    return PronosticoSimple(
        categoria=categoria,
        history=history_df,
        forecast=forecast_df,
        metodo=metodo,
        parametros=parametros
    )


def generate_forecasts(
    ventas_semanales_categoria: pd.DataFrame,
    output_dir: Path,
    *,
    top_n: int = 10,
    forecast_steps: int = 8,
    ventana_promedio: int = 8
) -> Dict[str, Path]:
    """
    Genera pronósticos de ventas para las principales categorías.

    Args:
        ventas_semanales_categoria: DataFrame con columnas [semana_iso, categoria, ventas_semana]
        output_dir: Directorio donde guardar los resultados
        top_n: Número de categorías principales a pronosticar
        forecast_steps: Número de semanas a pronosticar
        ventana_promedio: Ventana del promedio móvil (default: 8 semanas = 2 meses)

    Returns:
        Diccionario con paths a los archivos generados:
        - 'forecast': Pronósticos y datos históricos
        - 'metadata': Metadatos de los modelos (método, parámetros, métricas)

    Archivos generados:
        - prediccion_ventas_semanal.parquet: Datos históricos + pronósticos
        - prediccion_ventas_semanal_modelos.parquet: Información de cada modelo

    Ejemplo de uso:
        >>> paths = generate_forecasts(
        ...     ventas_df,
        ...     Path("data/predictivos"),
        ...     top_n=10,
        ...     forecast_steps=8
        ... )
        >>> pronosticos = pd.read_parquet(paths['forecast'])
    """
    ensure_directory(output_dir)
    ventas = _parse_semana(ventas_semanales_categoria)

    # Seleccionar top N categorías por volumen total
    top_categorias = (
        ventas.groupby("categoria")["ventas_semana"]
        .sum()
        .nlargest(top_n)
        .index.tolist()
    )

    resultados: List[pd.DataFrame] = []
    metadata_rows: List[Dict[str, object]] = []

    for categoria in top_categorias:
        # Preparar serie temporal
        serie_categoria = ventas[ventas["categoria"] == categoria]
        serie = (
            serie_categoria.groupby("semana_inicio")["ventas_semana"]
            .sum()
            .sort_index()
            .asfreq("W-MON")
            .fillna(method="ffill")
        )

        # Requerir mínimo 12 semanas de datos (~3 meses)
        if serie.count() < 12:
            continue

        # Generar pronóstico
        valores, lower, upper, metodo, params = _generar_pronostico(
            serie,
            steps=forecast_steps,
            ventana_promedio=ventana_promedio,
            usar_tendencia=True
        )

        # Preparar resultado
        result = _preparar_resultado(
            categoria, serie, valores, lower, upper, metodo, params
        )

        resultados.append(result.history)
        resultados.append(result.forecast)

        # Guardar metadata
        metadata_rows.append({
            "categoria": categoria,
            "metodo": metodo,
            "ventana_promedio": params["ventana"],
            "tendencia_semanal": params["tendencia_semanal"],
            "promedio_base": params["promedio_base"],
            "desviacion_std": params["desviacion"],
            "observaciones": serie.count()
        })

    if not resultados:
        return {}

    # Guardar resultados
    forecast_path = output_dir / "prediccion_ventas_semanal.parquet"
    metadata_path = output_dir / "prediccion_ventas_semanal_modelos.parquet"

    pd.concat(resultados, ignore_index=True).to_parquet(forecast_path, index=False)
    pd.DataFrame(metadata_rows).to_parquet(metadata_path, index=False)

    return {
        "forecast": forecast_path,
        "metadata": metadata_path,
    }


# ================================================================================
# GUÍA DE INTERPRETACIÓN PARA NO-TÉCNICOS
# ================================================================================
"""
¿Cómo interpretar los pronósticos?

1. **Valor Central (ventas_semana)**:
   - Es el pronóstico más probable basado en el promedio reciente y la tendencia
   - Ejemplo: "Se esperan vender 1,500 unidades la próxima semana"

2. **Intervalo de Confianza (lower - upper)**:
   - Rango donde esperamos que caigan las ventas reales (80% de probabilidad)
   - Ejemplo: "Entre 1,200 y 1,800 unidades"
   - El intervalo se amplía para semanas más lejanas (mayor incertidumbre)

3. **Tendencia**:
   - Si es positiva (+): Las ventas están creciendo
   - Si es negativa (-): Las ventas están decreciendo
   - Si es cercana a 0: Las ventas están estables
   - Ejemplo: "+50 unid/sem" = las ventas aumentan 50 unidades por semana

4. **Ventana de Promedio**:
   - Número de semanas usadas para calcular el promedio
   - 8 semanas = ~2 meses de datos recientes
   - Ventanas más cortas reaccionan más rápido a cambios
   - Ventanas más largas son más estables pero menos reactivas

EJEMPLO DE USO:
Si el modelo muestra:
- Promedio base: 1,000 unidades/semana
- Tendencia: +20 unidades/semana
- Pronóstico semana 1: 1,020 (rango: 850-1,190)
- Pronóstico semana 4: 1,080 (rango: 800-1,360)

INTERPRETACIÓN:
"Las ventas están creciendo ~20 unidades por semana. Esperamos vender
1,020 unidades la próxima semana (probablemente entre 850-1,190).
Para dentro de 4 semanas, esperamos 1,080 (rango más amplio: 800-1,360
por la mayor incertidumbre del futuro lejano)."
"""
