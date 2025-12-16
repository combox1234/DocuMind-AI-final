"""
Quick test script to measure response time optimization
Tests the Flask app response time
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

test_queries = [
    "What is cyber security?",
    "Tell me about machine learning",
    "How does REST API work?",
    "What are neural networks?"
]

def test_response_time():
    """Test response time for queries"""
    print("=" * 60)
    print("RESPONSE TIME OPTIMIZATION TEST")
    print("=" * 60)
    
    times = []
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"query": query},
                timeout=30
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                answer_preview = data.get('answer', '')[:100] + "..."
                chunks = data.get('chunks_retrieved', 0)
                
                print(f"Status: ✅ Success")
                print(f"Time: {elapsed:.2f} seconds")
                print(f"Chunks: {chunks}")
                print(f"Answer: {answer_preview}")
                
                times.append(elapsed)
            else:
                print(f"Status: ❌ Failed ({response.status_code})")
                
        except Exception as e:
            print(f"Status: ❌ Error - {e}")
    
    # Summary
    if times:
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Average response time: {sum(times) / len(times):.2f} seconds")
        print(f"Fastest: {min(times):.2f} seconds")
        print(f"Slowest: {max(times):.2f} seconds")
        print(f"Target: 5-10 seconds ✅" if all(5 <= t <= 10 for t in times) else f"Target: 5-10 seconds ❌")
        print("=" * 60)

if __name__ == "__main__":
    print("\nWaiting for Flask app to respond...")
    print("Make sure you started the app with: python app.py")
    print("\nStarting tests...\n")
    
    time.sleep(2)  # Wait for app to be ready
    test_response_time()
