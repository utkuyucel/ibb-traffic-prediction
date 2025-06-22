"""Istanbul Municipality Traffic Prediction System."""

from .database import get_db, TrafficRepository, create_tables, TrafficData
from .services import SchedulerService, DataCollector, TrafficIndexData
from .utils import setup_logging
from .ml import TrafficPredictor
from .api import app
from .api.schemas import TrafficDataResponse, PredictionResponse, MultiHorizonPredictionResponse

__version__ = "1.0.0"
__author__ = "Istanbul Municipality Traffic Prediction Team"

__all__ = [
    # Database
    "get_db", "TrafficRepository", "create_tables", "TrafficData",
    # Services
    "SchedulerService", "DataCollector", "TrafficIndexData",
    # Utils
    "setup_logging",
    # ML
    "TrafficPredictor",
    # API
    "app", "TrafficDataResponse", "PredictionResponse", "MultiHorizonPredictionResponse"
]
