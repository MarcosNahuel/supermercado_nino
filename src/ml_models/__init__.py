"""
Machine learning strategy simulators for the Supermercado NINO project.

Each module exposes a specialized class to emulate the economic impact
of a commercial initiative using historical ticket-level behavior.
"""

from .ticket_predictor import TicketPredictor
from .combo_simulator import ComboSimulator
from .marca_propia_estimator import MarcaPropiaEstimator
from .cross_sell_optimizer import CrossSellOptimizer
from .upselling_detector import UpsellingDetector
from .fidelizacion_simulator import FidelizacionSimulator
from .strategy_validator import StrategyValidator

__all__ = [
    "TicketPredictor",
    "ComboSimulator",
    "MarcaPropiaEstimator",
    "CrossSellOptimizer",
    "UpsellingDetector",
    "FidelizacionSimulator",
    "StrategyValidator",
]
