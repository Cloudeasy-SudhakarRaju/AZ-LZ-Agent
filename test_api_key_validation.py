#!/usr/bin/env python3
"""
Test for diagram endpoint response when API key is missing/invalid.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/backend')

try:
    from fastapi.testclient import TestClient
except ImportError:
    # Fallback for older FastAPI versions
    from starlette.testclient import TestClient

def test_missing_api_key():
    """Test that endpoint returns proper error when API key is missing"""
    # Ensure no API key is set
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    # Import main after removing API key to ensure proper initialization
    import importlib
    if 'main' in sys.modules:
        importlib.reload(sys.modules['main'])
    
    from main import app
    
    client = TestClient(app)
    
    response = client.post(
        "/generate-intelligent-diagram",
        json={"requirements": "Create a simple Azure VM with a VNet"}
    )
    
    assert response.status_code == 503
    assert "OpenAI API key is required" in response.json()["detail"]
    print("✓ Missing API key test passed")

def test_invalid_api_key():
    """Test that endpoint returns proper error when API key is invalid"""
    # Set invalid API key
    os.environ['OPENAI_API_KEY'] = 'invalid-key-123'
    
    # Import main after setting invalid API key
    import importlib
    if 'main' in sys.modules:
        importlib.reload(sys.modules['main'])
    
    from main import app
    
    client = TestClient(app)
    
    response = client.post(
        "/generate-intelligent-diagram",
        json={"requirements": "Create a simple Azure VM with a VNet"}
    )
    
    assert response.status_code == 503
    assert "OpenAI API key" in response.json()["detail"]
    print("✓ Invalid API key test passed")

def test_valid_format_api_key_but_fake():
    """Test that endpoint accepts valid-format API key but may fail at API call"""
    # Set valid format but fake API key
    os.environ['OPENAI_API_KEY'] = 'sk-fake-key-for-testing-123456789012345678901234567890'
    
    # Import main after setting valid format API key
    import importlib
    if 'main' in sys.modules:
        importlib.reload(sys.modules['main'])
    
    from main import app
    
    client = TestClient(app)
    
    response = client.post(
        "/generate-intelligent-diagram",
        json={"requirements": "Create a simple Azure VM with a VNet"}
    )
    
    # This should not fail at API key validation stage
    # It might fail at actual API call, which is expected with fake key
    assert response.status_code in [200, 500]  # 200 if mock works, 500 if API call fails
    print("✓ Valid format API key test passed")

if __name__ == "__main__":
    print("Running API key validation tests...")
    
    try:
        test_missing_api_key()
        test_invalid_api_key()
        test_valid_format_api_key_but_fake()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)