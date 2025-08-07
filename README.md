# Istanbul Municipality Traffic Prediction System

A comprehensive system for collecting, analyzing, and predicting Istanbul's traffic data using machine learning with advanced logging and model persistence.

## Architecture Overview

```mermaid
flowchart TD
    %% ===== TITLE =====
    TITLE([Istanbul Traffic Prediction System]):::title
    
    %% ===== EXTERNAL ENTITIES =====
    subgraph EXTERNAL[External Entities]
        direction TB
        EXT[🌐 Istanbul Traffic API]:::external
        USER[👥 End Users]:::external
    end

    %% ===== CORE SYSTEM =====
    subgraph DOCKER[ Dockerized Services ]
        direction LR
        
        subgraph DOCKER1[🐳 FastAPI Container]
            API[<b>FastAPI Backend</b><br/>• REST API Endpoints<br/>• Prediction Requests]:::container
            SCHEDULER[<b>Scheduler Service</b><br/>• Trigger Data Collection<br/>• Initiate ML Training]:::container
            COLLECTOR[<b>Data Collector</b><br/>• ETL Pipeline<br/>• Data Validation]:::container
            ML[<b>ML Predictor</b><br/>• Multi-Horizon Forecasting<br/>• Model Inference]:::container
        end

        subgraph DOCKER2[💾 PostgreSQL Container]
            DB[(<b>Traffic Database</b><br/>• Historical Records<br/>• Real-time Metrics)]:::database
        end
    end

    %% ===== MODEL STORAGE =====
    subgraph MODELS[📦 Model Storage]
        M15[<b>15-min Model</b>]:::model
        M30[<b>30-min Model</b>]:::model
        M60[<b>60-min Model</b>]:::model
        M120[<b>120-min Model</b>]:::model
    end

    %% ===== DATA FLOW =====
    USER -->|HTTP Requests<br/>Prediction Queries| API
    EXT -->|Live Traffic Data<br/>JSON/CSV| COLLECTOR
    COLLECTOR -->|Cleaned Data<br/>Batch Insert| DB
    DB -->|Training Data| SCHEDULER
    SCHEDULER -->|Trigger ETL| COLLECTOR
    SCHEDULER -->|Start Training| ML
    ML -->|Save Trained Models| MODELS
    ML -->|Load Models| MODELS
    API -->|Request Predictions| ML
    API -->|Manual Triggers| SCHEDULER

    %% ===== STYLING =====
    classDef title fill:#2c3e50,stroke:none,color:white,font-size:20px,font-weight:bold
    classDef external fill:#3498db,stroke:#2980b9,color:white,stroke-width:2px
    classDef container fill:#9b59b6,stroke:#8e44ad,color:white,stroke-width:2px
    classDef database fill:#27ae60,stroke:#2ecc71,color:white,stroke-width:2px
    classDef model fill:#e67e22,stroke:#d35400,color:white,stroke-width:2px
    linkStyle default stroke:#95a5a6,stroke-width:2px
```


## Quick Start


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
```

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

### Code Quality

Before pushing code, run the linting script:

```bash
# Auto-format and fix all linting issues
./lint.sh
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
