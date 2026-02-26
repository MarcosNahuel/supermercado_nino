import pandas as pd
import numpy as np
import math


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


def calcular_cajas_necesarias(
    tickets_por_minuto: float,
    tiempo_atencion_minutos: float,
    factor_seguridad: float = 0.8
) -> int:
    """
    Calcula cajas necesarias usando modelo M/M/c (teoría de colas).

    Fuente: Erlang C, modelo para sistemas de múltiples servidores
    ISO 18030: Gestión operativa de servicios

    Formula:
    - λ (lambda): tasa de llegada (tickets/minuto)
    - μ (mu): tasa de servicio (1/tiempo_atencion_minutos)
    - ρ (rho): intensidad de tráfico = λ / μ
    - c: número de servidores (cajas) = ceil(ρ / factor_seguridad)

    Args:
        tickets_por_minuto: Tasa de llegada (λ)
        tiempo_atencion_minutos: Tiempo promedio por cliente (1/μ)
        factor_seguridad: Factor de utilización máxima (default 0.8 = 80%)

    Returns:
        int: Número mínimo de cajas necesarias
    """
    if tickets_por_minuto == 0:
        return 1

    # Tasa de servicio (clientes/minuto por caja)
    mu = 1 / tiempo_atencion_minutos

    # Intensidad de tráfico (ρ)
    rho = tickets_por_minuto / mu

    # Cajas mínimas: ceil(ρ) con factor de seguridad
    cajas_minimas = math.ceil(rho / factor_seguridad)

    # Mínimo 1 caja, máximo garantizado disponible
    return max(1, cajas_minimas)


def calcular_estadisticas_distribucion(
    df_horarios: pd.DataFrame,
    tiempo_atencion_calculado: float
) -> pd.DataFrame:
    """
    Calcula estadísticas completas de distribución de cajas.

    Agrupa datos en intervalos de 10 minutos y calcula cajas necesarias
    para cada intervalo usando modelo M/M/c.

    Args:
        df_horarios: DataFrame con columna 'Hora' (datetime)
        tiempo_atencion_calculado: Tiempo promedio de atención (minutos)

    Returns:
        DataFrame con columnas:
        - intervalo_10min: datetime del inicio del intervalo
        - tickets: cantidad de tickets en el intervalo
        - tickets_por_minuto: tasa de llegada (tickets/minuto)
        - cajas_necesarias: cajas requeridas para ese intervalo
        - hora: string con hora (HH:MM)
        - dia: nombre del día
    """
    # Agrupar por intervalos de 10 minutos
    df = df_horarios.copy()
    df['intervalo_10min'] = df['Hora'].dt.floor('10min')

    # Agregar tickets por intervalo
    tickets_por_intervalo = df.groupby('intervalo_10min').size().reset_index(name='tickets')

    # Calcular tasa por minuto en ese intervalo
    tickets_por_intervalo['tickets_por_minuto'] = tickets_por_intervalo['tickets'] / 10

    # Calcular cajas necesarias
    tickets_por_intervalo['cajas_necesarias'] = tickets_por_intervalo['tickets_por_minuto'].apply(
        lambda x: calcular_cajas_necesarias(x, tiempo_atencion_calculado)
    )

    # Extraer hora para visualización
    tickets_por_intervalo['hora'] = tickets_por_intervalo['intervalo_10min'].dt.strftime('%H:%M')
    tickets_por_intervalo['dia'] = tickets_por_intervalo['intervalo_10min'].dt.day_name()

    return tickets_por_intervalo


def procesar_datos_analisis_cajas(horario_df: pd.DataFrame) -> dict:
    """
    Procesa datos de comprobantes para análisis de cajas.

    Calcula el intervalo promedio entre tickets, estadísticas de intervalos,
    y distribución de cajas necesarias por intervalo de 10 minutos.

    Args:
        horario_df: DataFrame con columna 'Hora' (datetime)

    Returns:
        dict con:
        - tiempo_atencion: minutos (intervalo promedio entre tickets)
        - tickets_por_intervalo: DataFrame con análisis por 10 minutos
        - estadisticas_intervalos: dict con media, mediana, desviación, percentiles
        - total_tickets: int (cantidad de comprobantes)
    """
    # Manejo de DataFrames vacías
    if horario_df is None or len(horario_df) == 0:
        return {
            'tiempo_atencion': 3.0,
            'tickets_por_intervalo': pd.DataFrame(),
            'estadisticas_intervalos': {
                'media': 0,
                'mediana': 0,
                'desviacion': 0,
                'percentil_25': 0,
                'percentil_75': 0,
                'min': 0,
                'max': 0,
            },
            'total_tickets': 0,
        }

    # 1. Calcular intervalo promedio entre tickets (en minutos)
    intervalo_promedio = calcular_intervalo_promedio_tickets(horario_df)

    # El tiempo de atención es el intervalo promedio entre tickets
    # Con fallback a 3.0 minutos si no hay datos válidos
    tiempo_atencion = intervalo_promedio if intervalo_promedio > 0 else 3.0

    # 2. Calcular estadísticas de intervalos
    df_sorted = horario_df.sort_values('Hora')
    intervalos = df_sorted['Hora'].diff().dt.total_seconds() / 60
    intervalos = intervalos[intervalos > 0]  # Excluir NaN y ceros

    # Calcular estadísticas, manejo de Series vacía
    if len(intervalos) > 0:
        estadisticas = {
            'media': intervalos.mean(),
            'mediana': intervalos.median(),
            'desviacion': intervalos.std(),
            'percentil_25': intervalos.quantile(0.25),
            'percentil_75': intervalos.quantile(0.75),
            'min': intervalos.min(),
            'max': intervalos.max(),
        }
    else:
        estadisticas = {
            'media': 0,
            'mediana': 0,
            'desviacion': 0,
            'percentil_25': 0,
            'percentil_75': 0,
            'min': 0,
            'max': 0,
        }

    # 3. Calcular distribución por intervalo de 10 minutos
    tickets_por_intervalo = calcular_estadisticas_distribucion(
        horario_df,
        tiempo_atencion
    )

    return {
        'tiempo_atencion': tiempo_atencion,
        'tickets_por_intervalo': tickets_por_intervalo,
        'estadisticas_intervalos': estadisticas,
        'total_tickets': len(horario_df),
    }
