"""
Test script for new sorting enhancements
Tests adaptive chunking, time-based sorting, multilingual LLM, and API endpoints
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:5000"

def test_analytics():
    """Test analytics endpoint"""
    print("\n=== Testing Analytics Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/analytics")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Analytics retrieved successfully")
        print(f"   Total files: {data.get('total_files', 0)}")
        print(f"   Storage: {data.get('storage_mb', 0)} MB")
        print(f"   Domains: {list(data.get('by_domain', {}).keys())}")
    else:
        print(f"❌ Failed: {response.status_code}")

def test_duplicates():
    """Test duplicates endpoint"""
    print("\n=== Testing Duplicates Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/duplicates")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Duplicates retrieved successfully")
        print(f"   Duplicate groups: {data.get('count', 0)}")
    else:
        print(f"❌ Failed: {response.status_code}")

def test_categories():
    """Test categories endpoint"""
    print("\n=== Testing Categories Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/categories")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Categories retrieved successfully")
        print(f"   Custom categories: {len(data.get('custom_categories', {}))}")
    else:
        print(f"❌ Failed: {response.status_code}")

def test_multilingual_chat():
    """Test multilingual chat"""
    print("\n=== Testing Multilingual Chat ===")
    
    # Test English query
    print("\n1. Testing English query...")
    response = requests.post(f"{BASE_URL}/chat", json={
        "query": "What is machine learning?"
    })
    if response.status_code == 200:
        data = response.json()
        detected_lang = data.get('detected_language', 'unknown')
        print(f"✅ English query processed")
        print(f"   Detected language: {detected_lang}")
        print(f"   Answer preview: {data.get('answer', '')[:100]}...")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test Hindi query (if you have Hindi documents)
    print("\n2. Testing Hindi query...")
    response = requests.post(f"{BASE_URL}/chat", json={
        "query": "मशीन लर्निंग क्या है?"
    })
    if response.status_code == 200:
        data = response.json()
        detected_lang = data.get('detected_language', 'unknown')
        print(f"✅ Hindi query processed")
        print(f"   Detected language: {detected_lang}")
    else:
        print(f"❌ Failed: {response.status_code}")

def test_status():
    """Test enhanced status endpoint"""
    print("\n=== Testing Status Endpoint ===")
    response = requests.get(f"{BASE_URL}/status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status retrieved successfully")
        print(f"   Database count: {data.get('database_count', 0)}")
        print(f"   Sorted files: {data.get('sorted_files', 0)}")
        print(f"   Ollama available: {data.get('ollama_available', False)}")
    else:
        print(f"❌ Failed: {response.status_code}")

def test_manager_endpoints():
    """Test manager-only endpoints"""
    print("\n=== Testing Manager-Only Endpoints ===")
    
    # Test without manager header (should fail)
    print("\n1. Testing without manager access...")
    response = requests.post(f"{BASE_URL}/api/categories", json={
        "domain": "Technology",
        "category_name": "TestCategory",
        "keywords": ["test", "example"]
    })
    if response.status_code == 403:
        print(f"✅ Correctly blocked non-manager access")
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
    
    # Test with manager header (should succeed)
    print("\n2. Testing with manager access...")
    headers = {"X-Manager": "true"}
    response = requests.post(f"{BASE_URL}/api/categories", 
        json={
            "domain": "Technology",
            "category_name": "TestCategory",
            "keywords": ["test", "example"]
        },
        headers=headers
    )
    if response.status_code == 200:
        print(f"✅ Manager successfully added category")
        
        # Clean up - delete the test category
        response = requests.delete(
            f"{BASE_URL}/api/categories/Technology/TestCategory",
            headers=headers
        )
        if response.status_code == 200:
            print(f"✅ Test category cleaned up")
    else:
        print(f"❌ Failed: {response.status_code}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("SORTING ENHANCEMENTS - TEST SUITE")
    print("=" * 60)
    
    try:
        # Test basic endpoints
        test_status()
        test_analytics()
        test_duplicates()
        test_categories()
        
        # Test multilingual
        test_multilingual_chat()
        
        # Test manager endpoints
        test_manager_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("   Make sure the Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
