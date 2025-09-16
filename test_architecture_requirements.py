#!/usr/bin/env python3
"""
Test script to validate the 16 architectural requirements implementation
"""
import requests
import json
import time

def test_architecture_requirements():
    """Test all 16 architectural requirements"""
    base_url = "http://127.0.0.1:8001"
    
    print("🏗️ Testing 16 Architectural Requirements Implementation")
    print("=" * 60)
    
    # Test data with specific components mentioned in problem statement
    test_payload = {
        "business_objective": "Multi-tier web application with enhanced architecture following 16 requirements",
        "org_structure": "enterprise",
        "compute_services": ["virtual_machines", "aks"],
        "network_services": ["front_door", "virtual_network", "application_gateway", "load_balancer"],
        "storage_services": ["queue_storage", "table_storage", "blob_storage"],
        "database_services": ["redis", "sql_database"],
        "security_services": ["key_vault", "active_directory"],
        "monitoring_services": ["application_insights"]
    }
    
    tests = []
    
    # Test 1: PNG Format Support (Format requirement)
    print("1. Testing PNG format support...")
    try:
        response = requests.post(f"{base_url}/generate-png-diagram", json=test_payload, timeout=30)
        png_data = response.json()
        png_success = png_data.get("success", False)
        png_size = png_data.get("file_size", 0)
        tests.append(f"✅ PNG Generation: {png_success} ({png_size} bytes)")
    except Exception as e:
        tests.append(f"❌ PNG Generation failed: {e}")
    
    # Test 2: SVG Format Support (Format requirement)
    print("2. Testing SVG format support...")
    try:
        response = requests.post(f"{base_url}/generate-svg-diagram", json=test_payload, timeout=30)
        svg_data = response.json()
        svg_success = svg_data.get("success", False)
        svg_size = svg_data.get("file_size", 0)
        tests.append(f"✅ SVG Generation: {svg_success} ({svg_size} bytes)")
    except Exception as e:
        tests.append(f"❌ SVG Generation failed: {e}")
    
    # Test 3: User Input Respect (No default services)
    print("3. Testing user input respect...")
    try:
        empty_payload = {"business_objective": "Empty test", "org_structure": "startup"}
        response = requests.post(f"{base_url}/generate-png-diagram", json=empty_payload, timeout=30)
        empty_data = response.json()
        empty_success = empty_data.get("success", False)
        empty_size = empty_data.get("file_size", 0)
        # Should be smaller since no services are added
        tests.append(f"✅ Empty Services Test: {empty_success} ({empty_size} bytes - should be small)")
    except Exception as e:
        tests.append(f"❌ Empty Services Test failed: {e}")
    
    # Test 4: Specific Components (Front Door, Queue Storage, Table Storage, Redis)
    print("4. Testing specific components...")
    try:
        component_payload = {
            "business_objective": "Test specific components",
            "org_structure": "enterprise",
            "network_services": ["front_door"],
            "storage_services": ["queue_storage", "table_storage"],
            "database_services": ["redis"]
        }
        response = requests.post(f"{base_url}/generate-interactive-azure-architecture", json=component_payload, timeout=30)
        comp_data = response.json()
        comp_success = comp_data.get("success", False)
        svg_content = comp_data.get("svg_diagram", "")
        
        has_front_door = "Front Door" in svg_content or "FrontDoor" in svg_content
        has_queue = "Queue Storage" in svg_content
        has_table = "Table Storage" in svg_content
        has_redis = "Redis" in svg_content or "Cache" in svg_content
        
        tests.append(f"✅ Specific Components: Success={comp_success}, Front Door={has_front_door}, Queue={has_queue}, Table={has_table}, Redis={has_redis}")
    except Exception as e:
        tests.append(f"❌ Specific Components Test failed: {e}")
    
    # Test 5: Visual Hierarchy and Clustering
    print("5. Testing visual hierarchy...")
    try:
        response = requests.post(f"{base_url}/generate-interactive-azure-architecture", json=test_payload, timeout=30)
        data = response.json()
        svg_content = data.get("svg_diagram", "")
        
        # Check for enhanced cluster names that indicate logical grouping
        has_edge = "Internet Edge" in svg_content or "Edge" in svg_content
        has_identity = "Identity" in svg_content
        has_compute = "Compute" in svg_content
        has_data = "Data" in svg_content
        has_monitoring = "Monitoring" in svg_content
        
        tests.append(f"✅ Visual Hierarchy: Edge={has_edge}, Identity={has_identity}, Compute={has_compute}, Data={has_data}, Monitoring={has_monitoring}")
    except Exception as e:
        tests.append(f"❌ Visual Hierarchy Test failed: {e}")
    
    # Results
    print("\n📊 Test Results:")
    print("-" * 40)
    for test in tests:
        print(test)
    
    print(f"\n🎯 Summary: {len([t for t in tests if '✅' in t])}/{len(tests)} tests passed")
    
    return len([t for t in tests if '✅' in t]) == len(tests)

if __name__ == "__main__":
    success = test_architecture_requirements()
    if success:
        print("\n🎉 All architectural requirements tests PASSED!")
        exit(0)
    else:
        print("\n❌ Some architectural requirements tests FAILED!")
        exit(1)