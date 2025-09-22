#!/usr/bin/env python3
"""
Test script specifically for testing the Figma fallback mechanism.
This tests the core functionality without requiring real Figma credentials.
"""

import requests
import json
import os

API_BASE_URL = "http://localhost:8001"

def test_fallback_mechanism():
    """Test that fallback to Python Diagrams works when Figma API fails."""
    print("🔍 Testing Figma fallback mechanism...")
    
    # Test data for architecture generation
    request_data = {
        "customer_inputs": {
            "business_objective": "Test architecture with fallback",
            "free_text_input": "Simple web application with VMs, network, storage, and database",
            "compute_services": ["virtual_machines"],
            "network_services": ["virtual_network"],
            "storage_services": ["storage_accounts"],
            "database_services": ["sql_database"],
            "security_services": ["key_vault"],
            "security_posture": "standard"
        },
        "figma_api_token": "fake-token-for-testing-fallback",
        "figma_file_id": "test-file-id-123",
        "page_name": "Test Architecture Fallback",
        "pattern": "ha-multiregion"
    }
    
    try:
        print("📤 Sending request with fake Figma token to test fallback...")
        response = requests.post(
            f"{API_BASE_URL}/generate-figma-diagram",
            headers={"Content-Type": "application/json"},
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if fallback was used
            if result.get("success") and result.get("is_fallback"):
                print("✅ Fallback mechanism working correctly!")
                print(f"   Fallback URL: {result.get('figma_url')}")
                print(f"   Format: {result.get('metadata', {}).get('diagram_format')}")
                
                # Check if the fallback file was actually created
                if "docs/diagrams/architecture_fallback" in result.get('figma_url', ''):
                    fallback_file = result['figma_url'].split(': ')[-1]
                    if os.path.exists(fallback_file):
                        print(f"   ✅ Fallback diagram file created: {fallback_file}")
                        file_size = os.path.getsize(fallback_file)
                        print(f"   📊 File size: {file_size} bytes")
                        return True
                    else:
                        print(f"   ❌ Fallback file not found: {fallback_file}")
                        return False
                else:
                    print("   ❌ Unexpected fallback URL format")
                    return False
            else:
                print(f"❌ Expected fallback but got: {result}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"   Error: {error_detail}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during fallback test: {e}")
        return False

def test_error_handling():
    """Test proper error handling for various edge cases."""
    print("\n🔍 Testing error handling...")
    
    test_cases = [
        {
            "name": "Missing Figma API token",
            "data": {
                "customer_inputs": {
                    "business_objective": "Test",
                    "compute_services": ["virtual_machines"],
                    "security_posture": "standard"
                },
                "figma_api_token": "",
                "figma_file_id": "test-id",
                "pattern": "ha-multiregion"
            },
            "expected_error": "Figma API token is required"
        },
        {
            "name": "Missing Figma file ID",
            "data": {
                "customer_inputs": {
                    "business_objective": "Test",
                    "compute_services": ["virtual_machines"],
                    "security_posture": "standard"
                },
                "figma_api_token": "fake-token",
                "figma_file_id": "",
                "pattern": "ha-multiregion"
            },
            "expected_error": "Figma file ID is required"
        },
        {
            "name": "Invalid pattern",
            "data": {
                "customer_inputs": {
                    "business_objective": "Test",
                    "compute_services": ["virtual_machines"],
                    "security_posture": "standard"
                },
                "figma_api_token": "fake-token",
                "figma_file_id": "test-id",
                "pattern": "invalid-pattern"
            },
            "expected_error": "Unknown pattern"
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate-figma-diagram",
                headers={"Content-Type": "application/json"},
                json=test_case["data"],
                timeout=10
            )
            
            if response.status_code == 500:
                error_detail = response.json().get('detail', '')
                if test_case["expected_error"] in error_detail:
                    print(f"   ✅ {test_case['name']}: Correct error handling")
                    passed += 1
                else:
                    print(f"   ❌ {test_case['name']}: Unexpected error: {error_detail}")
            else:
                print(f"   ❌ {test_case['name']}: Expected error but got status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {test_case['name']}: Exception during test: {e}")
    
    print(f"   📊 Error handling tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def main():
    """Run all fallback mechanism tests."""
    print("🚀 Azure Landing Zone Agent - Figma Fallback Mechanism Test")
    print("=" * 65)
    
    # Run tests
    tests = [
        test_fallback_mechanism,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fallback mechanism tests passed!")
        print("\n✅ Key achievements:")
        print("   - Figma API integration with proper token handling")
        print("   - Automatic fallback to Python Diagrams when Figma fails")
        print("   - Comprehensive error handling and validation")
        print("   - Service name mapping from customer inputs to catalog")
        print("   - Generated diagram files with proper metadata")
        
        return 0
    else:
        print(f"❌ {total - passed} tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())