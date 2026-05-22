import sys
import os

# Add the project path to sys.path
project_root = "/Users/vishnu/Documents/Tracxn/Discovery/Ghost/Ghost P1"
sys.path.append(project_root)

from engine.forensics import ForensicEngine
import asyncio

async def test_scoring():
    engine = ForensicEngine()
    
    mock_pool = {
        "wayback": [
            # Business-like year 2015
            {"url": "http://example.com/", "timestamp": "20150101", "is_root": True, "length": 5000, "digest": "d1"},
            {"url": "http://example.com/about", "timestamp": "20150201", "is_root": False, "length": 8000, "digest": "d2"},
            {"url": "http://example.com/products", "timestamp": "20150301", "is_root": False, "length": 12000, "digest": "d3"},
            
            # Parked-like year 2020
            {"url": "http://example.com/", "timestamp": "20200101", "is_root": True, "length": 1000, "digest": "d4"},
            {"url": "http://example.com/buy-this-domain", "timestamp": "20200201", "is_root": False, "length": 500, "digest": "d5"},
        ]
    }
    
    selected = engine._select_golden_era_snapshots(mock_pool)
    
    print("\n--- Selected Snapshots ---")
    for s in selected:
        print(f"Year: {s['timestamp'][:4]} | URL: {s['url']} | Score: {s.get('quality_score')} | Source: {s.get('source')}")

if __name__ == "__main__":
    asyncio.run(test_scoring())
