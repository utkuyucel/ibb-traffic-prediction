"""Database repository for traffic data operations."""

from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.database.models import TrafficData


class TrafficRepository:
    
    @staticmethod
    def create_traffic_data(db: Session, ti: int, ti_an: int, ti_av: int) -> TrafficData:
        traffic_data = TrafficData(ti=ti, ti_an=ti_an, ti_av=ti_av)
        db.add(traffic_data)
        db.commit()
        db.refresh(traffic_data)
        return traffic_data
    
    @staticmethod
    def get_latest_data(db: Session, limit: int = 10) -> List[TrafficData]:
        return db.query(TrafficData).order_by(desc(TrafficData.inserted_timestamp)).limit(limit).all()
    
    @staticmethod
    def get_data_count(db: Session) -> int:
        return db.query(TrafficData).count()
    
    @staticmethod
    def get_data_for_prediction(db: Session, limit: int = 100) -> List[TrafficData]:
        return db.query(TrafficData).order_by(desc(TrafficData.inserted_timestamp)).limit(limit).all()
    
    @staticmethod
    def get_data_for_prediction_with_timestamps(db: Session, limit: int = 100) -> List[Tuple[datetime, int, int, int]]:
        """Get traffic data with timestamps for consecutive validation."""
        data = db.query(TrafficData).order_by(desc(TrafficData.inserted_timestamp)).limit(limit).all()
        return [(row.inserted_timestamp, row.ti, row.ti_an, row.ti_av) for row in data]
