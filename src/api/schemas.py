"""Pydantic models for API."""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class TrafficDataResponse(BaseModel):
    id: int
    inserted_timestamp: datetime
    ti: int
    ti_an: int
    ti_av: int
    
    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    prediction: int
    timestamp: datetime
    status: str


class MultiHorizonPredictionResponse(BaseModel):
    predictions: Dict[int, Optional[int]]  # horizon -> prediction
    timestamp: datetime
    status: str
    training_status: Dict[int, bool]  # horizon -> is_trained
