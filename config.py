"""Configuration settings for Istanbul Municipality Traffic Prediction System."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # API Configuration
    TRAFFIC_API_URL: str = "https://tkmservices.ibb.gov.tr/web/api/TrafficData/v1/TrafficIndex_Sc1_Cont"
    DATA_FETCH_INTERVAL: int = 60  # seconds
    ML_TRIGGER_THRESHOLD: int = 10  # data points
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/ibb_traffic"
    )
    
    # FastAPI Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


config = Config()
