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
