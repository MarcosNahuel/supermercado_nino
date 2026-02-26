import pandas as pd
import numpy as np


def calcular_intervalo_promedio_tickets(df: pd.DataFrame) -> float:
    """
    Calcula el intervalo promedio entre tickets en minutos.

    Args:
        df: DataFrame con columna 'Hora' (datetime)

    Returns:
        float: Intervalo promedio en minutos
    """
    if len(df) < 2:
        return 0

    # Ordenar por hora
    df_sorted = df.sort_values('Hora')

    # Calcular diferencias entre tickets consecutivos en minutos
    intervalos = df_sorted['Hora'].diff().dt.total_seconds() / 60

    # Retornar promedio excluyendo el primer NaN
    return intervalos[1:].mean()
