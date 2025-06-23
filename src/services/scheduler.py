"""Scheduler service for periodic data collection and ML training with multi-horizon predictions."""

import asyncio
import logging
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from src.services.data_collector import DataCollector
from src.database import get_db, TrafficRepository
from src.ml import TrafficPredictor
from config import config

logger = logging.getLogger(__name__)
ml_logger = logging.getLogger("ml")
data_logger = logging.getLogger("data_collector")


class SchedulerService:
    
    def __init__(self):
        self.data_collector = DataCollector()
        self.predictor = TrafficPredictor()
        self.prediction_results: Dict[int, Optional[int]] = {}
        self.data_count = 0
    
    async def collect_and_store_data(self):
        """Collect traffic data and store in database."""
        collection_start = datetime.utcnow()
        
        try:
            logger.info("🔄 Starting data collection cycle")
            
            traffic_data = await self.data_collector.fetch_traffic_data()
            if traffic_data is None:
                logger.warning("⚠️  Data collection failed - no traffic data received")
                return
            
            db: Session = next(get_db())
            try:
                stored_data = TrafficRepository.create_traffic_data(
                    db, traffic_data.ti, traffic_data.ti_an, traffic_data.ti_av
                )
                self.data_count += 1
                
                collection_time = (datetime.utcnow() - collection_start).total_seconds()
                
                logger.info(f"✅ Data stored successfully (ID: {stored_data.id})")
                logger.info(f"📊 Total data points collected: {self.data_count}")
                logger.info(f"⏱️  Collection cycle completed in {collection_time:.2f} seconds")
                
                data_logger.info("💾 Data stored to database:")
                data_logger.info(f"   - Record ID: {stored_data.id}")
                data_logger.info(f"   - Timestamp: {stored_data.inserted_timestamp}")
                data_logger.info(f"   - Total Records: {self.data_count}")
                
                if self.data_count % config.ML_TRIGGER_THRESHOLD == 0:
                    logger.info(f"🎯 ML trigger threshold reached ({config.ML_TRIGGER_THRESHOLD} data points)")
                    ml_logger.info(f"🚨 Training trigger activated - {self.data_count} total data points collected")
                    await self.train_and_predict(db)
                
            finally:
                db.close()
                
        except Exception as e:
            collection_time = (datetime.utcnow() - collection_start).total_seconds()
            logger.error(f"❌ Data collection failed after {collection_time:.2f} seconds: {e}")
            data_logger.error(f"Collection cycle error: {e}")
    
    async def train_and_predict(self, db: Session):
        """Train ML models and make multi-horizon predictions."""
        training_cycle_start = datetime.utcnow()
        
        try:
            ml_logger.info("Starting ML training and prediction cycle")
            logger.info("ML training cycle initiated")
            
            recent_data_with_timestamps = TrafficRepository.get_data_for_prediction_with_timestamps(db, limit=200)
            if len(recent_data_with_timestamps) < 20:
                ml_logger.warning(f"Insufficient data for ML training: {len(recent_data_with_timestamps)} records (minimum: 20)")
                logger.warning("ML training skipped: insufficient data")
                return
            
            ml_logger.info(f"Retrieved {len(recent_data_with_timestamps)} records for training")
            
            if not self.predictor._validate_consecutive_timestamps(recent_data_with_timestamps):
                ml_logger.error("Training aborted: Non-consecutive data detected")
                logger.error("ML training skipped due to non-consecutive data")
                return
            
            training_data = [(ti, ti_an, ti_av) for _, ti, ti_an, ti_av in recent_data_with_timestamps]
            training_data.reverse()
            
            ml_logger.info("Data prepared for time series analysis")
            training_results = self.predictor.train_models(training_data)
            successful_models = sum(training_results.values())
            
            if successful_models > 0:
                ml_logger.info(f"Proceeding with predictions using {successful_models} trained models")
                
                prediction_data = training_data[-50:]
                predictions = self.predictor.predict_multi_horizon(prediction_data)
                
                self.prediction_results = predictions
                
                cycle_time = (datetime.utcnow() - training_cycle_start).total_seconds()
                
                successful_predictions = sum(1 for p in predictions.values() if p is not None)
                ml_logger.info("Training and prediction cycle completed successfully!")
                ml_logger.info("Multi-horizon prediction results:")
                for horizon, prediction in predictions.items():
                    if prediction is not None:
                        ml_logger.info(f"  {horizon}min: {prediction}")
                    else:
                        ml_logger.info(f"  {horizon}min: N/A (model not trained)")
                
                ml_logger.info(f"Total cycle time: {cycle_time:.2f} seconds")
                logger.info(f"ML cycle completed - {successful_predictions} predictions generated (cycle time: {cycle_time:.2f}s)")
            else:
                ml_logger.error("All model training failed - prediction cycle aborted")
                logger.error("ML training failed for all horizons")
            
        except Exception as e:
            cycle_time = (datetime.utcnow() - training_cycle_start).total_seconds()
            ml_logger.error(f"ML training/prediction cycle failed after {cycle_time:.2f} seconds: {e}")
            logger.error(f"ML cycle error: {e}")
    
    async def start_scheduler(self):
        """Start the periodic data collection."""
        logger.info("Starting scheduler service")
        
        while True:
            try:
                await self.collect_and_store_data()
                await asyncio.sleep(config.DATA_FETCH_INTERVAL)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(config.DATA_FETCH_INTERVAL)
    
    def get_latest_prediction(self) -> Optional[int]:
        """Get the latest ML prediction (15-minute horizon for legacy compatibility)."""
        return self.prediction_results.get(15)
    
    def get_multi_horizon_predictions(self) -> Dict[int, Optional[int]]:
        """Get all multi-horizon predictions."""
        return self.prediction_results.copy()
    
    def get_training_status(self) -> Dict[int, bool]:
        """Get training status for all horizons."""
        return self.predictor.get_training_status()
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.data_collector.close()
