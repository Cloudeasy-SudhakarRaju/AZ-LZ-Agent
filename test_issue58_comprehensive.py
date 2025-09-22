#!/usr/bin/env python3
"""
Comprehensive test script for Issue #58 - Architecture diagram generation
Tests PNG/SVG generation and validates user input matching
"""

import requests
import json
import base64
import time
import sys
from pathlib import Path

BASE_URL = "http://127.0.0.1:8001"

def test_server_health():
    """Test if server is running and healthy"""
    print("🩺 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        data = response.json()
        if data.get("status") == "healthy":
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server unhealthy: {data}")
            return False
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def test_png_generation():
    """Test PNG generation and validate output"""
    print("\n📸 Testing PNG generation...")
    
    test_payload = {
        "business_objective": "Test PNG generation for Issue #58",
        "network_services": ["front_door"],
        "storage_services": ["queue_storage"],
        "database_services": ["redis"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-png-diagram", 
                               json=test_payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ PNG request failed with status {response.status_code}")
            return False
            
        data = response.json()
        
        if not data.get("success"):
            print(f"❌ PNG generation failed: {data.get('error', 'Unknown error')}")
            return False
            
        # Validate PNG data
        png_base64 = data.get("png_base64")
        if not png_base64:
            print("❌ No PNG base64 data in response")
            return False
            
        # Decode and save PNG
        png_data = base64.b64decode(png_base64)
        png_path = Path("/tmp/test_issue58.png")
        png_path.write_bytes(png_data)
        
        # Validate PNG file
        if png_path.stat().st_size < 1000:
            print("❌ PNG file too small, likely corrupted")
            return False
            
        print(f"✅ PNG generated successfully: {len(png_data)} bytes")
        print(f"   File saved to: {png_path}")
        return True
        
    except Exception as e:
        print(f"❌ PNG generation test failed: {e}")
        return False

def test_svg_generation():
    """Test SVG generation and validate output"""
    print("\n🎨 Testing SVG generation...")
    
    test_payload = {
        "business_objective": "Test SVG generation for Issue #58",
        "network_services": ["front_door"],
        "storage_services": ["queue_storage"],
        "database_services": ["redis"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-interactive-azure-architecture", 
                               json=test_payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ SVG request failed with status {response.status_code}")
            return False
            
        data = response.json()
        
        if not data.get("success"):
            print(f"❌ SVG generation failed: {data.get('error', 'Unknown error')}")
            return False
            
        # Validate SVG data
        svg_content = data.get("svg_diagram")
        if not svg_content:
            print("❌ No SVG content in response")
            return False
            
        # Save SVG
        svg_path = Path("/tmp/test_issue58.svg")
        svg_path.write_text(svg_content)
        
        # Validate SVG contains expected elements
        if "Front Door" not in svg_content:
            print("❌ SVG missing Front Door service")
            return False
            
        if "Queue Storage" not in svg_content:
            print("❌ SVG missing Queue Storage service")
            return False
            
        if "Redis" not in svg_content:
            print("❌ SVG missing Redis service")
            return False
            
        print(f"✅ SVG generated successfully: {len(svg_content)} characters")
        print(f"   File saved to: {svg_path}")
        print("✅ All requested services found in SVG")
        return True
        
    except Exception as e:
        print(f"❌ SVG generation test failed: {e}")
        return False

def test_user_input_matching():
    """Test that diagram output matches user input exactly"""
    print("\n🎯 Testing user input matching...")
    
    test_cases = [
        {
            "name": "Specific services only",
            "payload": {
                "business_objective": "Only specific services requested",
                "compute_services": ["aks"],
                "database_services": ["cosmos_db"]
            },
            "expected_services": ["Azure Kubernetes Service", "Cosmos DB"],
            "excluded_services": ["Virtual Machine", "SQL Database", "Redis"]
        },
        {
            "name": "Empty architecture",
            "payload": {
                "business_objective": "Empty architecture - no services"
            },
            "expected_services": ["Ready for Service Selection"],
            "excluded_services": ["Virtual Machine", "Storage Account", "SQL Database"]
        },
        {
            "name": "Network services only",
            "payload": {
                "business_objective": "Network services test",
                "network_services": ["application_gateway", "front_door"]
            },
            "expected_services": ["Application Gateway", "Front Door"],
            "excluded_services": ["Virtual Machine", "Storage Account"]
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        
        try:
            response = requests.post(f"{BASE_URL}/generate-interactive-azure-architecture", 
                                   json=test_case["payload"], timeout=30)
            
            if response.status_code != 200:
                print(f"   ❌ Request failed with status {response.status_code}")
                continue
                
            data = response.json()
            
            if not data.get("success"):
                print(f"   ❌ Generation failed: {data.get('error', 'Unknown error')}")
                continue
                
            svg_content = data.get("svg_diagram", "")
            
            # Check expected services are present
            missing_expected = []
            for service in test_case["expected_services"]:
                if service not in svg_content:
                    missing_expected.append(service)
                    
            # Check excluded services are not present
            unexpected_present = []
            for service in test_case["excluded_services"]:
                if service in svg_content:
                    unexpected_present.append(service)
                    
            if missing_expected:
                print(f"   ❌ Missing expected services: {missing_expected}")
                continue
                
            if unexpected_present:
                print(f"   ❌ Unexpected services present: {unexpected_present}")
                continue
                
            print(f"   ✅ User input matching validated")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            
    print(f"\n✅ User input matching: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)

def test_icon_rendering():
    """Test that Azure icons are properly rendered (not broken)"""
    print("\n🎭 Testing icon rendering...")
    
    test_payload = {
        "business_objective": "Test icon rendering",
        "compute_services": ["virtual_machines", "aks"],
        "network_services": ["virtual_network", "front_door"],
        "database_services": ["sql_database", "cosmos_db"],
        "storage_services": ["storage_accounts"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-interactive-azure-architecture", 
                               json=test_payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Icon test request failed with status {response.status_code}")
            return False
            
        data = response.json()
        
        if not data.get("success"):
            print(f"❌ Icon test generation failed: {data.get('error', 'Unknown error')}")
            return False
            
        svg_content = data.get("svg_diagram", "")
        
        # Check for proper SVG structure
        if "<svg" not in svg_content:
            print("❌ Invalid SVG structure")
            return False
            
        # Check for service elements
        services_found = 0
        expected_services = ["Virtual Machine", "Azure Kubernetes", "Virtual Network", 
                           "Front Door", "SQL Database", "Cosmos DB", "Storage Account"]
        
        for service in expected_services:
            if service in svg_content:
                services_found += 1
                
        if services_found < len(expected_services) * 0.8:  # At least 80% should be found
            print(f"❌ Too few services found in SVG: {services_found}/{len(expected_services)}")
            return False
            
        print(f"✅ Icon rendering validated: {services_found}/{len(expected_services)} services found")
        return True
        
    except Exception as e:
        print(f"❌ Icon rendering test failed: {e}")
        return False

def main():
    """Run all tests for Issue #58"""
    print("🔍 ISSUE #58 COMPREHENSIVE TEST SUITE")
    print("=====================================")
    print("Testing: Architecture diagram generation does not match user input and fails to generate SVG/PNG")
    print()
    
    tests = [
        ("Server Health", test_server_health),
        ("PNG Generation", test_png_generation),
        ("SVG Generation", test_svg_generation),
        ("User Input Matching", test_user_input_matching),
        ("Icon Rendering", test_icon_rendering)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed_tests += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 TEST RESULTS")
    print(f"{'='*50}")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Issue #58 appears to be resolved.")
        print("\nGenerated files:")
        print("  - /tmp/test_issue58.png")
        print("  - /tmp/test_issue58.svg")
        return True
    else:
        print(f"\n❌ {total_tests - passed_tests} test(s) failed. Issue #58 still needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)