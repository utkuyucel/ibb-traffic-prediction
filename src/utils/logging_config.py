"""Logging configuration for the Istanbul Traffic Prediction System."""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from config import config


def setup_logging():
    """Setup comprehensive logging configuration."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Separate handler for ML activities
    ml_handler = logging.handlers.RotatingFileHandler(
        log_dir / "ml_training.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    ml_handler.setLevel(logging.INFO)
    ml_handler.setFormatter(detailed_formatter)
    
    # ML logger
    ml_logger = logging.getLogger("ml")
    ml_logger.addHandler(ml_handler)
    ml_logger.setLevel(logging.INFO)
    
    # Data collection logger
    data_handler = logging.handlers.RotatingFileHandler(
        log_dir / "data_collection.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    data_handler.setLevel(logging.INFO)
    data_handler.setFormatter(detailed_formatter)
    
    data_logger = logging.getLogger("data_collector")
    data_logger.addHandler(data_handler)
    data_logger.setLevel(logging.INFO)
    
    logging.info(f"Logging system initialized at {datetime.utcnow()}")
    return root_logger
