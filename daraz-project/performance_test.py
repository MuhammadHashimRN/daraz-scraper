#!/usr/bin/env python3

import requests
import time
import statistics

API_URL = "http://localhost:5000"

def test_endpoint(endpoint, method='GET', data=None):
    """Test endpoint performance"""
    times = []
    errors = 0
    
    for i in range(10):
        try:
            start = time.time()
            if method == 'GET':
                response = requests.get(f"{API_URL}{endpoint}", timeout=30)
            else:
                response = requests.post(f"{API_URL}{endpoint}", json=data, timeout=30)
            
            duration = time.time() - start
            times.append(duration)
            
            if response.status_code not in [200, 202]:
                errors += 1
        except Exception as e:
            errors += 1
            print(f"  Error: {e}")
    
    if times:
        return {
            'avg': statistics.mean(times),
            'min': min(times),
            'max': max(times),
            'errors': errors
        }
    return None

print("🧪 Performance Testing Daraz Scraper API")
print("=" * 50)

endpoints = [
    ('/', 'GET', None),
    ('/status', 'GET', None),
    ('/metrics', 'GET', None),
    ('/search', 'POST', {'min_price': 500}),
]

for endpoint, method, data in endpoints:
    print(f"\nTesting {method} {endpoint}...")
    result = test_endpoint(endpoint, method, data)
    
    if result:
        print(f"  Average: {result['avg']*1000:.2f}ms")
        print(f"  Min: {result['min']*1000:.2f}ms")
        print(f"  Max: {result['max']*1000:.2f}ms")
        print(f"  Errors: {result['errors']}/10")

print("\n✅ Performance testing complete!")