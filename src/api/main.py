"""FastAPI application for Istanbul traffic prediction."""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db, TrafficRepository, create_tables
from src.services import SchedulerService
from src.utils import setup_logging
from src.api.schemas import TrafficDataResponse, PredictionResponse, MultiHorizonPredictionResponse

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Istanbul Traffic Prediction API",
    description="API for Istanbul Municipality traffic data collection and prediction",
    version="1.0.0"
)

scheduler_service: Optional[SchedulerService] = None


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global scheduler_service
    
    logger.info("🚀 Istanbul Traffic Prediction API starting up...")
    
    create_tables()
    logger.info("✅ Database tables created/verified")
    
    scheduler_service = SchedulerService()
    logger.info("✅ Scheduler service initialized")
    
    import asyncio
    asyncio.create_task(scheduler_service.start_scheduler())
    logger.info("✅ Background data collection task started")
    
    logger.info("🎉 Application startup completed successfully!")
    logger.info("📊 API Documentation available at: /docs")
    logger.info("🔍 Health check available at: /health")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    global scheduler_service
    
    logger.info("🛑 Application shutdown initiated...")
    
    if scheduler_service:
        await scheduler_service.cleanup()
        logger.info("✅ Scheduler service cleaned up")
    
    logger.info("👋 Application shutdown completed successfully")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Istanbul Traffic Prediction API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.get("/traffic/latest", response_model=List[TrafficDataResponse])
async def get_latest_traffic_data(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get latest traffic data."""
    try:
        data = TrafficRepository.get_latest_data(db, limit=limit)
        return data
    except Exception as e:
        logger.error(f"Error fetching latest traffic data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/traffic/stats")
async def get_traffic_stats(db: Session = Depends(get_db)):
    """Get traffic data statistics."""
    try:
        total_count = TrafficRepository.get_data_count(db)
        latest_data = TrafficRepository.get_latest_data(db, limit=1)
        
        return {
            "total_records": total_count,
            "latest_timestamp": latest_data[0].inserted_timestamp if latest_data else None,
            "latest_ti": latest_data[0].ti if latest_data else None
        }
    except Exception as e:
        logger.error(f"Error fetching traffic stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/prediction", response_model=PredictionResponse)
async def get_traffic_prediction():
    """Get latest traffic prediction (15-minute horizon for backward compatibility)."""
    global scheduler_service
    
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service not available")
    
    prediction = scheduler_service.get_latest_prediction()
    
    if prediction is None:
        return PredictionResponse(
            prediction=0,
            timestamp=datetime.utcnow(),
            status="no_prediction_available"
        )
    
    return PredictionResponse(
        prediction=prediction,
        timestamp=datetime.utcnow(),
        status="success"
    )


@app.get("/predictions", response_model=MultiHorizonPredictionResponse)
async def get_multi_horizon_predictions():
    """Get multi-horizon traffic predictions for 15, 30, 60, and 120 minutes."""
    global scheduler_service
    
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service not available")
    
    predictions = scheduler_service.get_multi_horizon_predictions()
    training_status = scheduler_service.get_training_status()
    
    # Determine overall status
    if not any(predictions.values()):
        status = "no_predictions_available"
    elif all(p is not None for p in predictions.values()):
        status = "all_predictions_available"
    else:
        status = "partial_predictions_available"
    
    return MultiHorizonPredictionResponse(
        predictions=predictions,
        timestamp=datetime.utcnow(),
        status=status,
        training_status=training_status
    )
