"""Database models for traffic data."""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config

Base = declarative_base()


class TrafficData(Base):
    __tablename__ = "traffic_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    inserted_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ti = Column(Integer, nullable=False)
    ti_an = Column(Integer, nullable=False)
    ti_av = Column(Integer, nullable=False)


# Database connection
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
