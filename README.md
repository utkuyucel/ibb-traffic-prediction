# Istanbul Municipality Traffic Prediction System

A comprehensive system for collecting, analyzing, and predicting Istanbul's traffic data using machine learning with advanced logging and model persistence.

## 🚀 Features

### Core Functionality
- ✅ **Real-time Data Collection**: Fetches traffic data every 60 seconds from Istanbul Municipality API
- ✅ **PostgreSQL Storage**: Robust database storage with proper indexing
- ✅ **Multi-Horizon Predictions**: Advanced ML models for 15, 30, 60, and 120-minute traffic forecasts
- ✅ **Enhanced Machine Learning**: Random Forest models with temporal features and lag variables
- ✅ **REST API**: FastAPI-based API with automatic documentation
- ✅ **Docker Support**: Production-ready containerization

### Advanced Features
- 🔍 **Comprehensive Logging**: Multi-level logging with file rotation
- 💾 **Model Persistence**: Automatic model saving and loading with PKL files
- 📊 **Training Metrics**: Detailed model performance tracking
- ⚡ **Performance Monitoring**: Request timing and system metrics
- 🎯 **Smart Training**: Automatic model retraining with threshold-based triggers

## Project Structure

```
ibb-traffic-prediction/
├── src/
│   ├── api/             # FastAPI application
│   ├── database/        # Database models and repository
│   ├── ml/              # Machine learning predictor
│   └── services/        # Data collection and scheduling services
├── docker/              # Docker configuration
├── config.py            # Application configuration
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies
```

## Quick Start

### Using Docker 

1. **Clone and setup**:
   ```bash
   cd /home/utku/ibb-traffic-prediction
   ```

2. **Start services**:
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Access API**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## API Endpoints

### Traffic Data
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /traffic/latest?limit=10` - Get latest traffic data
- `GET /traffic/stats` - Get traffic statistics

### Predictions
- `GET /prediction` - Get legacy single-point traffic prediction (next minute)
- `GET /predictions` - Get multi-horizon traffic predictions (15, 30, 60, 120 minutes)

### Prediction Response Examples

**Legacy endpoint** (`/prediction`):
```json
{
  "prediction": 42,
  "timestamp": "2025-06-22T17:47:25.813456",
  "status": "prediction_available"
}
```

**Multi-horizon endpoint** (`/predictions`):
```json
{
  "predictions": {
    "15": 41,
    "30": 39,
    "60": 36,
    "120": 34
  },
  "timestamp": "2025-06-22T17:47:18.235315",
  "status": "predictions_available",
  "training_status": {
    "15": true,
    "30": true,
    "60": true,
    "120": false
  }
}

## Configuration

Configuration is managed in `config.py`:

- `TRAFFIC_API_URL`: Istanbul Municipality API endpoint
- `DATA_FETCH_INTERVAL`: Data collection interval (60 seconds)
- `ML_TRIGGER_THRESHOLD`: ML training trigger (10 data points)
- `DATABASE_URL`: PostgreSQL connection string

## Database Schema

```sql
CREATE TABLE traffic_data (
    id SERIAL PRIMARY KEY,
    inserted_timestamp TIMESTAMP DEFAULT NOW(),
    ti INTEGER NOT NULL,
    ti_an INTEGER NOT NULL,
    ti_av INTEGER NOT NULL
);
```

## Machine Learning

### Multi-Horizon Prediction System
- **Algorithm**: Separate Random Forest Regressor models for each time horizon
- **Horizons**: 15, 30, 60, and 120-minute predictions
- **Features**: Enhanced feature engineering with:
  - Lag features (1, 2, 3 minutes back) for TI, TI_AN, TI_AV
  - Time-of-day features (hour, minute)
  - Day-of-week patterns
  - Rolling averages and statistical measures

### Training Requirements
- **15-minute horizon**: Minimum 20 data points
- **30-minute horizon**: Minimum 35 data points  
- **60-minute horizon**: Minimum 65 data points
- **120-minute horizon**: Minimum 125 data points
- **Training Trigger**: Every 10 new data points collected
- **Model Persistence**: Automatic saving/loading with performance metrics

## Monitoring

- Health check endpoint for service monitoring
- Comprehensive logging for debugging
- Database connection health checks

## Development

### Setup Development Environment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ibb-traffic-prediction
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # For development tools
   pip install -e .[dev]
   ```

### Code Quality

Before pushing code, run the linting script:

```bash
# Auto-format and fix all linting issues
./lint.sh
```

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Start application
python main.py
```

### Configuration Files

- **pyproject.toml**: Project configuration with Ruff and pytest settings
- **requirements.txt**: Production dependencies
- **lint.sh**: Linting and code quality script

### Code Style Guidelines

- **Line length**: 100 characters maximum
- **Import organization**: Automated with Ruff's isort functionality
- **Formatting**: Handled by Ruff formatter
- **Linting**: Comprehensive checks with Ruff

