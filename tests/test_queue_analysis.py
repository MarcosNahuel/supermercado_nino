import sys
from pathlib import Path

# Agregar el directorio raíz al path para permitir importaciones relativas
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.queue_analysis import calcular_intervalo_promedio_tickets, calcular_cajas_necesarias

def test_calcular_intervalo_promedio_tickets():
    """Test que calcula el intervalo promedio entre tickets en minutos"""
    # Crear datos de prueba con 3 tickets en 3 minutos
    df = pd.DataFrame({
        'Hora': pd.to_datetime([
            '2025-01-15 10:00:00',
            '2025-01-15 10:01:00',
            '2025-01-15 10:03:00'
        ])
    })

    resultado = calcular_intervalo_promedio_tickets(df)
    # Intervalo: (1-0) + (3-1) = 1 + 2 = 3 minutos en total, promedio = 3/2 = 1.5 minutos
    assert abs(resultado - 1.5) < 0.01, f"Expected ~1.5, got {resultado}"


def test_calcular_cajas_necesarias():
    """
    Test modelo M/M/c
    - Lambda (llegada): 20 tickets/min
    - Mu (servicio): 1/3 min = 20 tickets/min por caja
    - Cajas necesarias: ceil(20/20) = 1 caja (mínimo)
    """
    tickets_por_minuto = 20
    tiempo_atencion_minutos = 3  # promedio calculado de datos

    cajas = calcular_cajas_necesarias(tickets_por_minuto, tiempo_atencion_minutos)

    # Mínimo 1 caja
    assert cajas >= 1, f"Mínimo 1 caja, got {cajas}"
