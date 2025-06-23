"""Machine learning service for multi-horizon traffic prediction with model persistence."""

import pickle
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ml_logger = logging.getLogger("ml")
logger = logging.getLogger(__name__)


class MultiHorizonTrafficPredictor:
    """Enhanced traffic predictor supporting multiple prediction horizons."""
    
    HORIZONS = [15, 30, 60, 120]
    
    def __init__(self):
        self.models = {horizon: RandomForestRegressor(n_estimators=100, random_state=42 + horizon) 
                      for horizon in self.HORIZONS}
        self.scalers = {horizon: StandardScaler() for horizon in self.HORIZONS}
        self.is_trained = {horizon: False for horizon in self.HORIZONS}
        
        self.feature_names = ['ti_lag1', 'ti_lag2', 'ti_lag3', 'ti_an_lag1', 'ti_av_lag1', 
                             'hour_sin', 'hour_cos', 'day_of_week']
        
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        
        self._load_models()
    
    def _get_model_paths(self, horizon: int) -> Tuple[Path, Path, Path]:
        """Get file paths for model, scaler, and metadata for a given horizon."""
        return (
            self.model_dir / f"traffic_predictor_{horizon}m.pkl",
            self.model_dir / f"traffic_scaler_{horizon}m.pkl", 
            self.model_dir / f"model_metadata_{horizon}m.pkl"
        )
    
    def _save_models(self):
        """Save all trained models, scalers, and metadata to disk."""
        try:
            for horizon in self.HORIZONS:
                if not self.is_trained[horizon]:
                    continue
                    
                model_path, scaler_path, metadata_path = self._get_model_paths(horizon)
                
                with open(model_path, 'wb') as f:
                    pickle.dump(self.models[horizon], f)
                with open(scaler_path, 'wb') as f:
                    pickle.dump(self.scalers[horizon], f)
                
                metadata = {
                    'horizon_minutes': horizon,
                    'feature_names': self.feature_names,
                    'is_trained': self.is_trained[horizon],
                    'trained_at': datetime.utcnow().isoformat(),
                    'model_type': 'RandomForestRegressor',
                    'n_estimators': 100
                }
                
                with open(metadata_path, 'wb') as f:
                    pickle.dump(metadata, f)
            
            ml_logger.info("Multi-horizon models saved successfully")
            logger.info("Enhanced ML models saved to disk")
            
        except Exception as e:
            ml_logger.error(f"Failed to save models: {e}")
            logger.error(f"Model save error: {e}")
    
    def _load_models(self):
        """Load existing models, scalers, and metadata from disk."""
        loaded_count = 0
        
        for horizon in self.HORIZONS:
            try:
                model_path, scaler_path, metadata_path = self._get_model_paths(horizon)
                
                if not all([model_path.exists(), scaler_path.exists(), metadata_path.exists()]):
                    continue
                
                with open(model_path, 'rb') as f:
                    self.models[horizon] = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scalers[horizon] = pickle.load(f)
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                
                self.is_trained[horizon] = metadata.get('is_trained', False)
                trained_at = metadata.get('trained_at', 'Unknown')
                
                if self.is_trained[horizon]:
                    loaded_count += 1
                    ml_logger.info(f"Model for {horizon}m horizon loaded (trained: {trained_at})")
                
            except Exception as e:
                ml_logger.warning(f"Failed to load {horizon}m model: {e}")
                self.is_trained[horizon] = False
        
        if loaded_count > 0:
            logger.info(f"Loaded {loaded_count}/{len(self.HORIZONS)} existing ML models")
        else:
            ml_logger.info("No existing models found, will train new models")
    
    def _prepare_enhanced_features(self, data: List[Tuple[int, int, int]], 
                                  target_horizon: int) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Prepare enhanced features including temporal patterns."""
        min_data_points = max(10, target_horizon + 5)
        
        if len(data) < min_data_points:
            return None, None
        
        df = pd.DataFrame(data, columns=['ti', 'ti_an', 'ti_av'])
        
        current_time = datetime.utcnow()
        timestamps = [current_time.replace(second=0, microsecond=0) - 
                     pd.Timedelta(minutes=i) for i in range(len(data)-1, -1, -1)]
        df['timestamp'] = timestamps
        
        df['ti_lag1'] = df['ti'].shift(1)
        df['ti_lag2'] = df['ti'].shift(2)
        df['ti_lag3'] = df['ti'].shift(3)
        df['ti_an_lag1'] = df['ti_an'].shift(1)
        df['ti_av_lag1'] = df['ti_av'].shift(1)
        
        df['hour'] = df['timestamp'].dt.hour
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        df['target'] = df['ti'].shift(-target_horizon)
        
        df = df.dropna()
        
        if df.empty:
            return None, None
        
        features = df[self.feature_names].values
        target = df['target'].values
        
        return features, target
    
    def train_models(self, data: List[Tuple[int, int, int]]) -> Dict[int, bool]:
        """Train models for all prediction horizons."""
        training_start = datetime.utcnow()
        ml_logger.info(f"Starting multi-horizon ML training at {training_start}")
        logger.info(f"Enhanced ML training started with {len(data)} data points")
        
        results = {}
        
        for horizon in self.HORIZONS:
            ml_logger.info(f"Training model for {horizon}-minute horizon")
            
            try:
                features, target = self._prepare_enhanced_features(data, horizon)
                
                if features is None or len(features) < 5:
                    ml_logger.warning(f"Insufficient data for {horizon}m horizon: "
                                    f"{len(features) if features is not None else 0} samples")
                    results[horizon] = False
                    continue
                
                ml_logger.info(f"Prepared {len(features)} samples for {horizon}m training")
                
                features_scaled = self.scalers[horizon].fit_transform(features)
                self.models[horizon].fit(features_scaled, target)
                self.is_trained[horizon] = True
                
                train_predictions = self.models[horizon].predict(features_scaled)
                train_mae = mean_absolute_error(target, train_predictions)
                train_mse = mean_squared_error(target, train_predictions)
                train_r2 = r2_score(target, train_predictions)
                
                ml_logger.info(f"{horizon}m model trained successfully!")
                ml_logger.info(f"   MAE: {train_mae:.2f}, MSE: {train_mse:.2f}, R²: {train_r2:.3f}")
                
                results[horizon] = True
                
            except Exception as e:
                ml_logger.error(f"Training failed for {horizon}m horizon: {e}")
                results[horizon] = False
        
        self._save_models()
        
        training_end = datetime.utcnow()
        training_duration = (training_end - training_start).total_seconds()
        successful_models = sum(results.values())
        
        ml_logger.info(f"Multi-horizon training completed in {training_duration:.2f}s")
        ml_logger.info(f"Successfully trained {successful_models}/{len(self.HORIZONS)} models")
        logger.info(f"Enhanced ML training completed - {successful_models}/{len(self.HORIZONS)} models trained")
        
        return results
    
    def predict_multi_horizon(self, recent_data: List[Tuple[int, int, int]]) -> Dict[int, Optional[int]]:
        """Make predictions for all trained horizons."""
        prediction_start = datetime.utcnow()
        ml_logger.info("Starting multi-horizon predictions")
        
        predictions = {}
        
        for horizon in self.HORIZONS:
            if not self.is_trained[horizon]:
                ml_logger.warning(f"{horizon}m model not trained, skipping prediction")
                predictions[horizon] = None
                continue
            
            try:
                features, _ = self._prepare_enhanced_features(recent_data, horizon)
                
                if features is None:
                    ml_logger.warning(f"Cannot prepare features for {horizon}m prediction")
                    predictions[horizon] = None
                    continue
                
                latest_features = features[-1:].reshape(1, -1)
                features_scaled = self.scalers[horizon].transform(latest_features)
                
                raw_prediction = self.models[horizon].predict(features_scaled)[0]
                final_prediction = max(0, int(round(raw_prediction)))
                
                predictions[horizon] = final_prediction
                ml_logger.info(f"{horizon}m prediction: {final_prediction} (raw: {raw_prediction:.2f})")
                
            except Exception as e:
                ml_logger.error(f"{horizon}m prediction failed: {e}")
                predictions[horizon] = None
        
        prediction_end = datetime.utcnow()
        prediction_time = (prediction_end - prediction_start).total_seconds() * 1000
        
        successful_predictions = sum(1 for p in predictions.values() if p is not None)
        ml_logger.info(f"Multi-horizon predictions completed in {prediction_time:.2f}ms")
        ml_logger.info(f"Generated {successful_predictions}/{len(self.HORIZONS)} predictions")
        
        return predictions
    
    def get_training_status(self) -> Dict[int, bool]:
        """Get training status for all horizons."""
        return self.is_trained.copy()
    
    def _validate_consecutive_timestamps(self, data_with_timestamps: List[Tuple[datetime, int, int, int]], 
                                       expected_interval_minutes: int = 1, tolerance_seconds: int = 30) -> bool:
        """Validate that data points have consecutive timestamps within tolerance."""
        if len(data_with_timestamps) < 2:
            return True
        
        sorted_data = sorted(data_with_timestamps, key=lambda x: x[0])
        
        expected_interval = timedelta(minutes=expected_interval_minutes)
        tolerance = timedelta(seconds=tolerance_seconds)
        
        gaps_found = []
        
        for i in range(1, len(sorted_data)):
            current_time = sorted_data[i][0]
            previous_time = sorted_data[i-1][0]
            actual_interval = current_time - previous_time
            
            if abs(actual_interval - expected_interval) > tolerance:
                gap_minutes = actual_interval.total_seconds() / 60
                gaps_found.append({
                    'index': i,
                    'previous_time': previous_time,
                    'current_time': current_time,
                    'gap_minutes': gap_minutes
                })
        
        if gaps_found:
            ml_logger.warning(f"🚨 Non-consecutive data detected! Found {len(gaps_found)} gaps:")
            for gap in gaps_found:
                ml_logger.warning(f"   Gap between {gap['previous_time']} and {gap['current_time']}: "
                                f"{gap['gap_minutes']:.1f} minutes (expected: {expected_interval_minutes} min)")
            
            gap_sizes = [gap['gap_minutes'] for gap in gaps_found]
            avg_gap = sum(gap_sizes) / len(gap_sizes)
            max_gap = max(gap_sizes)
            
            ml_logger.warning(f"   Gap statistics - Average: {avg_gap:.1f}min, Maximum: {max_gap:.1f}min")
            logger.warning(f"Training skipped: {len(gaps_found)} data gaps detected "
                         f"(avg: {avg_gap:.1f}min, max: {max_gap:.1f}min)")
            
            return False
        
        ml_logger.info(f"✅ Data validation passed: {len(sorted_data)} consecutive data points")
        return True


class TrafficPredictor(MultiHorizonTrafficPredictor):
    """Legacy single-horizon predictor for backward compatibility."""
    
    def __init__(self):
        super().__init__()
        self.default_horizon = 15
    
    def prepare_features(self, data: List[Tuple[int, int, int]]) -> Optional[np.ndarray]:
        """Legacy method for preparing features (15-minute horizon only)."""
        features, _ = self._prepare_enhanced_features(data, self.default_horizon)
        return features
    
    def train_model(self, data: List[Tuple[int, int, int]]) -> bool:
        """Legacy method for training model (15-minute horizon only)."""
        results = self.train_models(data)
        return results.get(self.default_horizon, False)
    
    def predict_next_ti(self, recent_data: List[Tuple[int, int, int]]) -> Optional[int]:
        """Legacy method for making predictions (15-minute horizon only)."""
        predictions = self.predict_multi_horizon(recent_data)
        return predictions.get(self.default_horizon)
    
    def evaluate_model(self, data: List[Tuple[int, int, int]]) -> Optional[float]:
        """Legacy method for model evaluation (15-minute horizon only)."""
        if not self.is_trained[self.default_horizon]:
            return None
        
        try:
            features, target = self._prepare_enhanced_features(data, self.default_horizon)
            if features is None:
                return None
            
            features_scaled = self.scalers[self.default_horizon].transform(features)
            predictions = self.models[self.default_horizon].predict(features_scaled)
            
            return mean_absolute_error(target, predictions)
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return None
