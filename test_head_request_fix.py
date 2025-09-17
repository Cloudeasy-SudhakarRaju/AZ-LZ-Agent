#!/usr/bin/env python3
"""
Test specifically for HEAD request support in download functionality.

This test validates the fix for the download failure issue where HEAD requests
were not supported, causing "Download Failed" errors in some clients.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"

def test_head_request_support():
    """Test that HEAD requests work on download endpoints"""
    print("🔍 Testing HEAD request support...")
    
    # Use Figma fallback to generate a file with download URL
    test_data = {
        "customer_inputs": {
            "business_objective": "Test HEAD request support",
            "compute_services": ["virtual_machines"]
        },
        "figma_api_token": "invalid_token",
        "figma_file_id": "test_file_id",
        "fallback_format": "png"
    }
    
    # Generate PNG file via Figma fallback
    print("  📊 Generating test PNG file via Figma fallback...")
    response = requests.post(f"{BASE_URL}/generate-figma-diagram", json=test_data, timeout=30)
    if response.status_code != 200:
        print(f"  ❌ Failed to generate PNG: {response.status_code}")
        return False
    
    data = response.json()
    download_url = data.get("download_url")
    
    if not download_url:
        print("  ❌ No download URL returned")
        return False
    
    print(f"  ✅ Generated file with download URL: {download_url}")
    
    # Test HEAD request
    print("  🔍 Testing HEAD request...")
    head_response = requests.head(f"{BASE_URL}{download_url}", timeout=10)
    
    if head_response.status_code != 200:
        print(f"  ❌ HEAD request failed: {head_response.status_code}")
        return False
    
    # Verify headers
    expected_headers = ['content-type', 'content-length', 'content-disposition']
    for header in expected_headers:
        if header not in head_response.headers:
            print(f"  ❌ Missing expected header: {header}")
            return False
    
    content_type = head_response.headers.get('content-type')
    content_length = head_response.headers.get('content-length')
    content_disposition = head_response.headers.get('content-disposition')
    
    print(f"  ✅ HEAD response headers:")
    print(f"    Content-Type: {content_type}")
    print(f"    Content-Length: {content_length}")
    print(f"    Content-Disposition: {content_disposition}")
    
    # Verify content type is correct for PNG
    if content_type != 'image/png':
        print(f"  ❌ Wrong content type: expected 'image/png', got '{content_type}'")
        return False
    
    # Test GET request to compare
    print("  🔍 Testing GET request for comparison...")
    get_response = requests.get(f"{BASE_URL}{download_url}", timeout=10)
    
    if get_response.status_code != 200:
        print(f"  ❌ GET request failed: {get_response.status_code}")
        return False
    
    # Compare headers
    if get_response.headers.get('content-type') != head_response.headers.get('content-type'):
        print("  ❌ Content-Type mismatch between HEAD and GET")
        return False
    
    if get_response.headers.get('content-length') != head_response.headers.get('content-length'):
        print("  ❌ Content-Length mismatch between HEAD and GET")
        return False
    
    # Verify HEAD response has no body (or minimal body)
    if len(head_response.content) > 10:  # Allow some minimal content
        print(f"  ❌ HEAD response has unexpected body content: {len(head_response.content)} bytes")
        return False
    
    # Verify GET response has the expected body content
    actual_size = len(get_response.content)
    expected_size = int(content_length)
    
    if actual_size != expected_size:
        print(f"  ❌ GET response size mismatch: expected {expected_size}, got {actual_size}")
        return False
    
    print(f"  ✅ GET response body size matches Content-Length: {actual_size} bytes")
    print("  ✅ HEAD request support working correctly!")
    
    return True

def test_svg_head_request():
    """Test HEAD request support for SVG files"""
    print("🔍 Testing HEAD request support for SVG...")
    
    # Use Figma fallback to generate SVG file with download URL
    test_data = {
        "customer_inputs": {
            "business_objective": "Test SVG HEAD request support",
            "compute_services": ["virtual_machines"]
        },
        "figma_api_token": "invalid_token",
        "figma_file_id": "test_file_id",
        "fallback_format": "svg"
    }
    
    print("  📊 Generating test SVG file via Figma fallback...")
    response = requests.post(f"{BASE_URL}/generate-figma-diagram", json=test_data, timeout=30)
    if response.status_code != 200:
        print(f"  ❌ Failed to generate SVG: {response.status_code}")
        return False
    
    data = response.json()
    download_url = data.get("download_url")
    
    if not download_url:
        print("  ❌ No download URL returned")
        return False
    
    print(f"  ✅ Generated SVG with download URL: {download_url}")
    
    # Test HEAD request
    head_response = requests.head(f"{BASE_URL}{download_url}", timeout=10)
    
    if head_response.status_code != 200:
        print(f"  ❌ HEAD request failed: {head_response.status_code}")
        return False
    
    content_type = head_response.headers.get('content-type')
    if content_type != 'image/svg+xml':
        print(f"  ❌ Wrong content type: expected 'image/svg+xml', got '{content_type}'")
        return False
    
    print(f"  ✅ SVG HEAD request working correctly!")
    print(f"    Content-Type: {content_type}")
    print(f"    Content-Length: {head_response.headers.get('content-length')}")
    
    return True

def main():
    """Run all HEAD request tests"""
    print("🧪 Starting HEAD request support tests")
    print(f"Test started at: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        ("PNG HEAD Request Support", test_head_request_support),
        ("SVG HEAD Request Support", test_svg_head_request)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            if test_func():
                print(f"✅ PASS - {test_name}")
                passed_tests += 1
            else:
                print(f"❌ FAIL - {test_name}")
        except Exception as e:
            print(f"❌ ERROR - {test_name}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if i < passed_tests else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All HEAD request tests passed! Download functionality is fully working.")
        print("\n✅ Issues resolved:")
        print("   - HEAD requests now supported on download endpoints")
        print("   - Proper Content-Length and Content-Type headers returned")
        print("   - Both PNG and SVG formats support HEAD requests")
        print("   - Download clients should no longer fail with 'Method Not Allowed'")
        return True
    else:
        print(f"💥 {total_tests - passed_tests} tests failed. HEAD request support may have issues.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)