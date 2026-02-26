import plotly.graph_objects as go
import pandas as pd


def crear_grafico_tickets_vs_cajas(tickets_por_intervalo: pd.DataFrame) -> go.Figure:
    """
    Crea gráfico de línea dual: tickets vs cajas necesarias.

    Visualiza la distribución de tickets emitidos (línea azul sólida) y las cajas
    necesarias para atenderlos (línea roja punteada) en intervalos de 10 minutos.

    Args:
        tickets_por_intervalo: DataFrame con columnas:
            - intervalo_10min: datetime del inicio del intervalo
            - tickets: cantidad de tickets emitidos
            - cajas_necesarias: int con cajas requeridas (calculado según modelo M/M/c)

    Returns:
        go.Figure: Figura de Plotly con dos líneas en ejes Y diferentes
            - Eje Y izquierdo: Tickets emitidos (azul)
            - Eje Y derecho: Cajas necesarias (rojo punteado)
    """
    df = tickets_por_intervalo.copy()

    fig = go.Figure()

    # Línea de tickets (eje Y izquierdo)
    fig.add_trace(go.Scatter(
        x=df['intervalo_10min'],
        y=df['tickets'],
        name='Tickets emitidos',
        line=dict(color='#1f77b4', width=2),
        yaxis='y1',
        hovertemplate='<b>%{x|%H:%M}</b><br>Tickets: %{y}<extra></extra>',
    ))

    # Línea de cajas necesarias (eje Y derecho)
    fig.add_trace(go.Scatter(
        x=df['intervalo_10min'],
        y=df['cajas_necesarias'],
        name='Cajas necesarias',
        line=dict(color='#d62728', width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>%{x|%H:%M}</b><br>Cajas: %{y}<extra></extra>',
    ))

    fig.update_layout(
        title='Distribución de Tickets y Cajas Necesarias (cada 10 minutos)',
        xaxis=dict(
            title='Hora del día',
            titlefont=dict(size=12),
        ),
        yaxis=dict(
            title='Tickets emitidos',
            titlefont=dict(color='#1f77b4', size=12),
            tickfont=dict(color='#1f77b4'),
            side='left',
        ),
        yaxis2=dict(
            title='Cajas necesarias',
            titlefont=dict(color='#d62728', size=12),
            tickfont=dict(color='#d62728'),
            overlaying='y',
            side='right',
        ),
        hovermode='x unified',
        height=500,
        template='plotly_white',
        legend=dict(
            x=0.5,
            y=1.15,
            xanchor='center',
            yanchor='top',
            orientation='h',
        ),
        margin=dict(t=100, b=80, l=80, r=80),
    )

    return fig


def crear_tabla_metricas(
    estadisticas: dict,
    tickets_por_intervalo: pd.DataFrame,
    tiempo_atencion: float,
    total_cajas_disponibles: int = 8
) -> pd.DataFrame:
    """
    Crea tabla con métricas de distribución de cajas por hora.

    Agrupa los datos de intervalos de 10 minutos por hora y presenta:
    - Franja Horaria
    - Total Tickets
    - Cajas Necesarias (máximo en esa hora)
    - Cajas Recomendadas (ajustado al máximo disponible)
    - Utilización (%)
    - Tickets/Minuto

    Args:
        estadisticas: Dict con estadísticas de intervalos (no usado en lógica actual)
        tickets_por_intervalo: DataFrame con columnas intervalo_10min, tickets, cajas_necesarias
        tiempo_atencion: Tiempo promedio de atención (no usado en lógica actual)
        total_cajas_disponibles: Total de cajas disponibles (default: 8)

    Returns:
        pd.DataFrame con métricas horarias
    """
    df = tickets_por_intervalo.copy()

    # Agrupar por hora (no 10 min) para tabla resumen
    df['hora'] = df['intervalo_10min'].dt.floor('h').dt.strftime('%H:00')
    df_resumen = df.groupby('hora').agg({
        'tickets': 'sum',
        'cajas_necesarias': 'max',  # Max en esa hora
    }).reset_index()

    # Cajas recomendadas (ajustar al máximo disponible)
    df_resumen['cajas_recomendadas'] = df_resumen['cajas_necesarias'].apply(
        lambda x: min(x, total_cajas_disponibles)
    )

    # Utilización (%)
    df_resumen['utilizacion_pct'] = (
        df_resumen['cajas_recomendadas'] / total_cajas_disponibles * 100
    ).round(1)

    # Tickets por minuto
    df_resumen['tickets_por_minuto'] = (df_resumen['tickets'] / 60).round(2)

    # Renombrar columnas para presentación
    df_resumen.columns = [
        'Franja Horaria',
        'Total Tickets',
        'Cajas Necesarias',
        'Cajas Recomendadas',
        'Utilización (%)',
        'Tickets/Minuto'
    ]

    return df_resumen


def crear_tabla_estadisticas_intervalo(estadisticas: dict) -> pd.DataFrame:
    """
    Crea tabla con estadísticas de intervalos entre tickets.

    Presenta las métricas estadísticas principales en formato tabular,
    con valores formateados a 2 decimales.

    Columnas: Métrica, Valor (en minutos)

    Args:
        estadisticas: Dict con keys: media, mediana, desviacion, percentil_25,
                     percentil_75, min, max (todos en minutos)

    Returns:
        pd.DataFrame con 7 filas de estadísticas
    """
    datos = {
        'Métrica': [
            'Media (minutos)',
            'Mediana (minutos)',
            'Desviación Estándar',
            'Percentil 25 (minutos)',
            'Percentil 75 (minutos)',
            'Mínimo (minutos)',
            'Máximo (minutos)',
        ],
        'Valor': [
            f"{estadisticas['media']:.2f}",
            f"{estadisticas['mediana']:.2f}",
            f"{estadisticas['desviacion']:.2f}",
            f"{estadisticas['percentil_25']:.2f}",
            f"{estadisticas['percentil_75']:.2f}",
            f"{estadisticas['min']:.2f}",
            f"{estadisticas['max']:.2f}",
        ]
    }

    return pd.DataFrame(datos)
