"""
Test all AI features
"""

from data_loader import DataLoader
from demand_forecast import DemandForecaster
from reorder_engine import ReorderEngine
from segmentation import Segmenter
from anomaly_detector import AnomalyDetector
from qa_assistant import QAAssistant


def test_all():
    print("=" * 60)
    print("🤖 TESTING ALL AI FEATURES")
    print("=" * 60)
    
    # 1. Data Loader
    print("\n📂 1. Testing Data Loader...")
    loader = DataLoader()
    loader.load_all_data()
    print(f"   ✅ Stock In: {len(loader.stock_data)} records")
    print(f"   ✅ Sales: {len(loader.sales_data)} records")
    
    # 2. Demand Forecasting
    print("\n📊 2. Testing Demand Forecaster...")
    forecaster = DemandForecaster()
    results = forecaster.forecast_all_products()
    count = len([r for r in results.values() if r['status'] == 'success'])
    print(f"   ✅ Forecasted {count} products")
    
    # 3. Reorder Engine
    print("\n🔄 3. Testing Reorder Engine...")
    engine = ReorderEngine()
    recs = engine.get_all_recommendations()
    print(f"   ✅ Found {len(recs)} reorder recommendations")
    
    # 4. Segmentation
    print("\n👥 4. Testing Segmentation...")
    segmenter = Segmenter()
    customers = segmenter.calculate_rfm_customers()
    suppliers = segmenter.calculate_rfm_suppliers()
    print(f"   ✅ {len(customers)} customers segmented")
    print(f"   ✅ {len(suppliers)} suppliers segmented")
    
    # 5. Anomaly Detection
    print("\n⚠️ 5. Testing Anomaly Detector...")
    detector = AnomalyDetector()
    alerts = detector.run_full_scan()
    print(f"   ✅ Found {len(alerts)} anomalies")
    
    # 6. Q&A Assistant
    print("\n💬 6. Testing Q&A Assistant...")
    assistant = QAAssistant()
    if assistant.llm_available:
        response = assistant.quick_query("What is the current stock status?")
        print(f"   ✅ Response: {response[:100]}...")
    else:
        print("   ⚠️ LLM not available - install Ollama")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    test_all()