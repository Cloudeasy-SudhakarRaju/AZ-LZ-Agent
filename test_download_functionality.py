#!/usr/bin/env python3
"""
Comprehensive test to validate SVG/PNG download functionality and fallback mechanisms.

This test validates the fixes for:
1. SVG/PNG download functionality
2. Fallback rendering mechanisms
3. Proper file path handling
4. Correct MIME type handling
"""

import requests
import os
import time
import json
from datetime import datetime

# Base URL for the backend
BASE_URL = "http://127.0.0.1:8001"

def test_endpoint_availability():
    """Test that the backend is running and available."""
    print("🔍 Testing backend availability...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is available")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not available: {e}")
        return False

def test_standard_png_generation():
    """Test standard PNG generation and download."""
    print("\n🔍 Testing standard PNG generation...")
    
    payload = {
        "business_objective": "Test PNG generation",
        "compute_services": ["virtual_machines"],
        "network_services": ["virtual_network"],
        "database_services": ["sql_database"]
    }
    
    try:
        # Generate diagram
        response = requests.post(f"{BASE_URL}/generate-azure-diagram", json=payload, timeout=30)
        if response.status_code != 200:
            print(f"❌ PNG generation failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        diagram_path = data.get("diagram_path")
        if not diagram_path:
            print("❌ No diagram path returned")
            return False
        
        filename = os.path.basename(diagram_path)
        print(f"✅ PNG generated: {filename}")
        
        # Test download
        download_response = requests.get(f"{BASE_URL}/generate-azure-diagram/download/{filename}", timeout=10)
        if download_response.status_code != 200:
            print(f"❌ PNG download failed: {download_response.status_code}")
            return False
        
        # Verify content type
        content_type = download_response.headers.get('content-type')
        if content_type != 'image/png':
            print(f"❌ Wrong content type for PNG: {content_type}")
            return False
        
        # Verify file size
        content_length = int(download_response.headers.get('content-length', 0))
        if content_length < 1000:  # PNG should be at least 1KB
            print(f"❌ PNG file too small: {content_length} bytes")
            return False
        
        print(f"✅ PNG download successful: {content_length} bytes, content-type: {content_type}")
        return True
        
    except Exception as e:
        print(f"❌ PNG test failed: {e}")
        return False

def test_standard_svg_generation():
    """Test standard SVG generation and download."""
    print("\n🔍 Testing standard SVG generation...")
    
    payload = {
        "business_objective": "Test SVG generation",
        "compute_services": ["virtual_machines"],
        "network_services": ["virtual_network"],
        "database_services": ["sql_database"]
    }
    
    try:
        # Generate SVG diagram
        response = requests.post(f"{BASE_URL}/generate-svg-diagram", json=payload, timeout=30)
        if response.status_code != 200:
            print(f"❌ SVG generation failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        svg_path = data.get("svg_path")
        if not svg_path:
            print("❌ No SVG path returned")
            return False
        
        filename = os.path.basename(svg_path)
        print(f"✅ SVG generated: {filename}")
        
        # Test download
        download_response = requests.get(f"{BASE_URL}/generate-azure-diagram/download/{filename}", timeout=10)
        if download_response.status_code != 200:
            print(f"❌ SVG download failed: {download_response.status_code}")
            return False
        
        # Verify content type
        content_type = download_response.headers.get('content-type')
        if content_type != 'image/svg+xml':
            print(f"❌ Wrong content type for SVG: {content_type}")
            return False
        
        # Verify file size
        content_length = int(download_response.headers.get('content-length', 0))
        if content_length < 100:  # SVG should be at least 100 bytes
            print(f"❌ SVG file too small: {content_length} bytes")
            return False
        
        print(f"✅ SVG download successful: {content_length} bytes, content-type: {content_type}")
        return True
        
    except Exception as e:
        print(f"❌ SVG test failed: {e}")
        return False

def test_figma_png_fallback():
    """Test Figma PNG fallback functionality."""
    print("\n🔍 Testing Figma PNG fallback...")
    
    payload = {
        "customer_inputs": {
            "business_objective": "Test PNG fallback",
            "compute_services": ["virtual_machines"],
            "network_services": ["virtual_network"],
            "database_services": ["sql_database"]
        },
        "figma_api_token": "invalid_token_for_testing_fallback",
        "figma_file_id": "test_file_id",
        "fallback_format": "png"
    }
    
    try:
        # Generate with fallback
        response = requests.post(f"{BASE_URL}/generate-figma-diagram", json=payload, timeout=30)
        if response.status_code != 200:
            print(f"❌ Figma PNG fallback failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        
        # Verify fallback was triggered
        if not data.get("is_fallback"):
            print("❌ Fallback was not triggered")
            return False
        
        download_url = data.get("download_url")
        fallback_filename = data.get("fallback_filename")
        
        if not download_url or not fallback_filename:
            print("❌ No download URL or filename returned")
            return False
        
        if not fallback_filename.endswith('.png'):
            print(f"❌ Expected PNG filename, got: {fallback_filename}")
            return False
        
        print(f"✅ PNG fallback triggered: {fallback_filename}")
        
        # Test download
        download_response = requests.get(f"{BASE_URL}{download_url}", timeout=10)
        if download_response.status_code != 200:
            print(f"❌ PNG fallback download failed: {download_response.status_code}")
            return False
        
        # Verify content type
        content_type = download_response.headers.get('content-type')
        if content_type != 'image/png':
            print(f"❌ Wrong content type for PNG fallback: {content_type}")
            return False
        
        # Verify file size
        content_length = int(download_response.headers.get('content-length', 0))
        if content_length < 1000:  # PNG should be at least 1KB
            print(f"❌ PNG fallback file too small: {content_length} bytes")
            return False
        
        print(f"✅ PNG fallback download successful: {content_length} bytes, content-type: {content_type}")
        return True
        
    except Exception as e:
        print(f"❌ PNG fallback test failed: {e}")
        return False

def test_figma_svg_fallback():
    """Test Figma SVG fallback functionality."""
    print("\n🔍 Testing Figma SVG fallback...")
    
    payload = {
        "customer_inputs": {
            "business_objective": "Test SVG fallback",
            "compute_services": ["virtual_machines"],
            "network_services": ["virtual_network"],
            "database_services": ["sql_database"]
        },
        "figma_api_token": "invalid_token_for_testing_fallback",
        "figma_file_id": "test_file_id",
        "fallback_format": "svg"
    }
    
    try:
        # Generate with fallback
        response = requests.post(f"{BASE_URL}/generate-figma-diagram", json=payload, timeout=30)
        if response.status_code != 200:
            print(f"❌ Figma SVG fallback failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        
        # Verify fallback was triggered
        if not data.get("is_fallback"):
            print("❌ Fallback was not triggered")
            return False
        
        download_url = data.get("download_url")
        fallback_filename = data.get("fallback_filename")
        
        if not download_url or not fallback_filename:
            print("❌ No download URL or filename returned")
            return False
        
        if not fallback_filename.endswith('.svg'):
            print(f"❌ Expected SVG filename, got: {fallback_filename}")
            return False
        
        print(f"✅ SVG fallback triggered: {fallback_filename}")
        
        # Test download
        download_response = requests.get(f"{BASE_URL}{download_url}", timeout=10)
        if download_response.status_code != 200:
            print(f"❌ SVG fallback download failed: {download_response.status_code}")
            return False
        
        # Verify content type
        content_type = download_response.headers.get('content-type')
        if content_type != 'image/svg+xml':
            print(f"❌ Wrong content type for SVG fallback: {content_type}")
            return False
        
        # Verify file size
        content_length = int(download_response.headers.get('content-length', 0))
        if content_length < 100:  # SVG should be at least 100 bytes
            print(f"❌ SVG fallback file too small: {content_length} bytes")
            return False
        
        print(f"✅ SVG fallback download successful: {content_length} bytes, content-type: {content_type}")
        return True
        
    except Exception as e:
        print(f"❌ SVG fallback test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Starting comprehensive download functionality tests")
    print(f"Test started at: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        ("Backend Availability", test_endpoint_availability),
        ("Standard PNG Generation", test_standard_png_generation),
        ("Standard SVG Generation", test_standard_svg_generation),
        ("Figma PNG Fallback", test_figma_png_fallback),
        ("Figma SVG Fallback", test_figma_svg_fallback),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SVG/PNG download functionality is working correctly.")
        print("\n✅ Issues fixed:")
        print("   - Download endpoint now serves files from correct location (/tmp/)")
        print("   - Both PNG and SVG files download with correct MIME types")
        print("   - Figma fallback generates files in accessible location")
        print("   - Fallback supports both PNG and SVG formats")
        return True
    else:
        print(f"💥 {total - passed} tests failed. Issues may still exist.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)