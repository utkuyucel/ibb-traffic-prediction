"""Simple test to verify the system setup."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.services.data_collector import DataCollector, TrafficIndexData
    print("✅ Data collector import successful")
except ImportError as e:
    print(f"❌ Data collector import failed: {e}")

try:
    from src.ml.predictor import TrafficPredictor
    print("✅ ML predictor import successful")
except ImportError as e:
    print(f"❌ ML predictor import failed: {e}")

try:
    from config import config
    print("✅ Configuration import successful")
    print(f"   API URL: {config.TRAFFIC_API_URL}")
    print(f"   Fetch interval: {config.DATA_FETCH_INTERVAL}s")
except ImportError as e:
    print(f"❌ Configuration import failed: {e}")


async def test_data_collector():
    """Test data collector functionality."""
    print("\n🔍 Testing data collector...")
    
    collector = DataCollector()
    try:
        # Test XML parsing with sample data
        sample_xml = '''<?xml version="1.0" encoding="utf-8"?>
<ResponseTrafficIndex_Sc1_Cont xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.datacontract.org/2004/07/TKMWebApi.Controllers.Traffic.Models">
<TI>42</TI>
<TI_An>44</TI_An>
<TI_Av>42</TI_Av>
</ResponseTrafficIndex_Sc1_Cont>'''
        
        result = collector._parse_xml_response(sample_xml)
        if result and result.ti == 42 and result.ti_an == 44 and result.ti_av == 42:
            print("✅ XML parsing works correctly")
        else:
            print("❌ XML parsing failed")
            
    except Exception as e:
        print(f"❌ Data collector test failed: {e}")
    finally:
        await collector.close()


def test_ml_predictor():
    """Test ML predictor functionality."""
    print("\n🤖 Testing ML predictor...")
    
    try:
        predictor = TrafficPredictor()
        
        # Test with sample data
        sample_data = [(40, 42, 38), (45, 47, 43), (42, 44, 40), (38, 40, 36), (41, 43, 39)]
        
        features = predictor.prepare_features(sample_data)
        if features is not None:
            print("✅ Feature preparation works")
        else:
            print("❌ Feature preparation failed")
            
        # Test training
        extended_data = sample_data * 4  # Create more data for training
        if predictor.train_model(extended_data):
            print("✅ Model training works")
            
            # Test prediction
            prediction = predictor.predict_next_ti(extended_data[-10:])
            if prediction is not None:
                print(f"✅ Model prediction works: {prediction}")
            else:
                print("❌ Model prediction failed")
        else:
            print("❌ Model training failed")
            
    except Exception as e:
        print(f"❌ ML predictor test failed: {e}")


async def main():
    """Run all tests."""
    print("🚀 Istanbul Municipality Traffic Prediction System Test\n")
    
    await test_data_collector()
    test_ml_predictor()
    
    print("\n✨ Test completed!")


if __name__ == "__main__":
    asyncio.run(main())
