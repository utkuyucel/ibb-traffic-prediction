"""Istanbul Municipality Traffic Prediction System."""

from .api import app
from .api.schemas import MultiHorizonPredictionResponse, PredictionResponse, TrafficDataResponse
from .database import TrafficData, TrafficRepository, create_tables, get_db
from .ml import TrafficPredictor
from .services import DataCollector, SchedulerService, TrafficIndexData
from .utils import setup_logging


__version__ = "1.0.0"
__author__ = "Istanbul Municipality Traffic Prediction Team"

__all__ = [
    # Database
    "get_db",
    "TrafficRepository",
    "create_tables",
    "TrafficData",
    # Services
    "SchedulerService",
    "DataCollector",
    "TrafficIndexData",
    # Utils
    "setup_logging",
    # ML
    "TrafficPredictor",
    # API
    "app",
    "TrafficDataResponse",
    "PredictionResponse",
    "MultiHorizonPredictionResponse",
]
