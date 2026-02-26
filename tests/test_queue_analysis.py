import sys
from pathlib import Path

# Agregar el directorio raíz al path para permitir importaciones relativas
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.queue_analysis import calcular_intervalo_promedio_tickets

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
