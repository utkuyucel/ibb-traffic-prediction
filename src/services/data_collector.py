"""Traffic data collection service with enhanced logging."""

import json
from dataclasses import dataclass
from typing import Optional
import httpx
import logging
from datetime import datetime
from config import config

# Create data collection specific logger
data_logger = logging.getLogger("data_collector")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrafficIndexData:
    ti: int
    ti_an: int
    ti_av: int


class DataCollector:
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def fetch_traffic_data(self) -> Optional[TrafficIndexData]:
        """Fetch traffic data with enhanced logging."""
        fetch_start = datetime.utcnow()
        
        try:
            data_logger.info("🌐 Fetching traffic data from Istanbul Municipality API...")
            logger.info("Starting data fetch from traffic API")
            
            response = await self.client.get(config.TRAFFIC_API_URL)
            response.raise_for_status()
            
            fetch_time = (datetime.utcnow() - fetch_start).total_seconds() * 1000  # ms
            data_logger.info(f"⚡ API response received in {fetch_time:.2f}ms")
            
            traffic_data = self._parse_json_response(response.text)
            
            if traffic_data:
                data_logger.info("✅ Traffic data parsed successfully:")
                data_logger.info(f"   - TI: {traffic_data.ti}")
                data_logger.info(f"   - TI_An: {traffic_data.ti_an}")
                data_logger.info(f"   - TI_Av: {traffic_data.ti_av}")
                logger.info(f"Traffic data fetched: TI={traffic_data.ti}, TI_An={traffic_data.ti_an}, TI_Av={traffic_data.ti_av}")
            else:
                data_logger.warning("⚠️  Failed to parse traffic data from API response")
                logger.warning("Traffic data parsing failed")
            
            return traffic_data
            
        except httpx.RequestError as e:
            fetch_time = (datetime.utcnow() - fetch_start).total_seconds() * 1000  # ms
            data_logger.error(f"❌ Network request failed after {fetch_time:.2f}ms: {e}")
            logger.error(f"Traffic API request failed: {e}")
            return None
        except Exception as e:
            fetch_time = (datetime.utcnow() - fetch_start).total_seconds() * 1000  # ms
            data_logger.error(f"❌ Unexpected error during data fetch after {fetch_time:.2f}ms: {e}")
            logger.error(f"Unexpected error during traffic data fetch: {e}")
            return None
    
    def _parse_json_response(self, json_content: str) -> Optional[TrafficIndexData]:
        """Parse JSON response from Istanbul Municipality traffic API."""
        try:
            data = json.loads(json_content)
            
            # Expected format: {"TI": 80, "TI_An": 75, "TI_Av": 85}
            # Extract values with error checking
            if not isinstance(data, dict):
                logger.error("Response is not a JSON object")
                return None
            
            # Check for required fields
            required_fields = ['TI', 'TI_An', 'TI_Av']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                logger.error(f"Missing required fields in JSON response: {missing_fields}")
                return None
            
            # Extract and validate values
            try:
                ti = int(data['TI'])
                ti_an = int(data['TI_An'])
                ti_av = int(data['TI_Av'])
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid numeric values in JSON response: {e}")
                return None
            
            return TrafficIndexData(ti=ti, ti_an=ti_an, ti_av=ti_av)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON response: {e}")
            return None
    
    async def close(self):
        await self.client.aclose()
