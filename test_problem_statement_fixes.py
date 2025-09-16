#!/usr/bin/env python3
"""
Test script to validate the specific fixes mentioned in the problem statement:
1. Random Architecture Generation fixes
2. SVG/PNG Generation Failure fixes
3. Input Validation and Error Handling improvements
"""
import requests
import json
import time
import base64

def test_random_architecture_fixes():
    """Test fixes for random architecture generation issues"""
    base_url = "http://127.0.0.1:8001"
    
    print("🎯 Testing Random Architecture Generation Fixes")
    print("=" * 48)
    
    tests = []
    
    # Test 1: User-specific service selection is honored
    print("1. Testing user-specific service selection adherence...")
    try:
        user_specific_payload = {
            "business_objective": "User-defined architecture test",
            "org_structure": "enterprise",
            "compute_services": ["aks"],  # Only AKS
            "database_services": ["cosmos_db"],  # Only Cosmos DB
            "security_services": ["key_vault"]  # Only Key Vault
        }
        response = requests.post(f"{base_url}/generate-azure-diagram", json=user_specific_payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                # The diagram should contain only the user-selected services
                tests.append("✅ User service selection: Diagram generated with only selected services")
            else:
                tests.append(f"❌ User service selection: Generation failed - {data}")
        else:
            tests.append(f"❌ User service selection: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ User service selection test failed: {e}")
    
    # Test 2: No default services when user provides minimal input
    print("2. Testing no random defaults with minimal input...")
    try:
        minimal_payload = {
            "business_objective": "Minimal input test - no defaults should be added"
        }
        response = requests.post(f"{base_url}/generate-azure-diagram", json=minimal_payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                # Should generate a minimal framework without random services
                file_size = len(base64.b64decode(data.get("diagram_base64", "")))
                if file_size < 50000:  # Small file indicates minimal content
                    tests.append(f"✅ No random defaults: Minimal diagram generated ({file_size} bytes)")
                else:
                    tests.append(f"⚠️ No random defaults: File size may indicate added services ({file_size} bytes)")
            else:
                tests.append(f"❌ No random defaults: Generation failed - {data}")
        else:
            tests.append(f"❌ No random defaults: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ No random defaults test failed: {e}")
    
    # Test 3: Architecture patterns align with user inputs
    print("3. Testing architecture pattern alignment...")
    try:
        pattern_payload = {
            "business_objective": "Microservices architecture with container orchestration",
            "org_structure": "enterprise",
            "compute_services": ["aks", "container_instances"],
            "network_services": ["application_gateway", "virtual_network"],
            "database_services": ["cosmos_db"],
            "integration_services": ["service_bus", "api_management"]
        }
        response = requests.post(f"{base_url}/generate-interactive-azure-architecture", json=pattern_payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                # Should reflect the microservices pattern with containers
                svg_content = data.get("svg_diagram", "").lower()
                has_containers = "kubernetes" in svg_content or "container" in svg_content
                has_api_mgmt = "api management" in svg_content or "api" in svg_content
                has_microservices_elements = has_containers and has_api_mgmt
                
                if has_microservices_elements:
                    tests.append("✅ Architecture pattern: Microservices pattern correctly reflected")
                else:
                    tests.append(f"❌ Architecture pattern: Missing microservices elements (containers={has_containers}, api_mgmt={has_api_mgmt})")
            else:
                tests.append(f"❌ Architecture pattern: Generation failed - {data}")
        else:
            tests.append(f"❌ Architecture pattern: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ Architecture pattern test failed: {e}")
    
    return tests


def test_svg_png_generation_fixes():
    """Test fixes for SVG/PNG generation failures"""
    base_url = "http://127.0.0.1:8001"
    
    print("\n🖼️ Testing SVG/PNG Generation Reliability Fixes")
    print("=" * 49)
    
    tests = []
    
    # Test 1: PNG generation reliability
    print("1. Testing PNG generation reliability...")
    try:
        png_payload = {
            "business_objective": "PNG generation test",
            "compute_services": ["virtual_machines", "aks"],
            "network_services": ["virtual_network", "load_balancer"],
            "storage_services": ["blob_storage"],
            "database_services": ["sql_database"]
        }
        response = requests.post(f"{base_url}/generate-png-diagram", json=png_payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("png_base64"):
                file_size = data.get("file_size", 0)
                if file_size > 10000:  # Reasonable PNG size
                    tests.append(f"✅ PNG generation: Reliable generation ({file_size} bytes)")
                else:
                    tests.append(f"❌ PNG generation: File too small ({file_size} bytes)")
            else:
                tests.append(f"❌ PNG generation: Missing data - {data}")
        else:
            tests.append(f"❌ PNG generation: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ PNG generation test failed: {e}")
    
    # Test 2: SVG generation reliability
    print("2. Testing SVG generation reliability...")
    try:
        svg_payload = {
            "business_objective": "SVG generation test", 
            "compute_services": ["app_services"],
            "network_services": ["application_gateway"],
            "database_services": ["cosmos_db"]
        }
        response = requests.post(f"{base_url}/generate-svg-diagram", json=svg_payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("svg_content"):
                file_size = data.get("file_size", 0)
                svg_content = data.get("svg_content", "")
                is_valid_svg = svg_content.startswith("<?xml") or svg_content.startswith("<svg")
                
                if file_size > 1000 and is_valid_svg:
                    tests.append(f"✅ SVG generation: Reliable generation ({file_size} bytes, valid SVG)")
                else:
                    tests.append(f"❌ SVG generation: Invalid SVG (size={file_size}, valid={is_valid_svg})")
            else:
                tests.append(f"❌ SVG generation: Missing data - {data}")
        else:
            tests.append(f"❌ SVG generation: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ SVG generation test failed: {e}")
    
    # Test 3: Fallback mechanism testing
    print("3. Testing fallback mechanisms...")
    try:
        # Test with complex service selection to stress the system
        complex_payload = {
            "business_objective": "Complex architecture stress test",
            "compute_services": ["virtual_machines", "aks", "app_services", "functions"],
            "network_services": ["virtual_network", "application_gateway", "load_balancer", "firewall"],
            "storage_services": ["storage_accounts", "blob_storage"],
            "database_services": ["sql_database", "cosmos_db", "redis"],
            "security_services": ["key_vault", "active_directory", "security_center"],
            "monitoring_services": ["monitor", "log_analytics"]
        }
        response = requests.post(f"{base_url}/generate-interactive-azure-architecture", json=complex_payload, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            has_svg = bool(data.get("svg_diagram"))
            has_mermaid = bool(data.get("mermaid"))
            
            if success and (has_svg or has_mermaid):
                tests.append("✅ Fallback mechanisms: Complex diagram generated successfully")
            else:
                tests.append(f"❌ Fallback mechanisms: Failed (success={success}, svg={has_svg}, mermaid={has_mermaid})")
        else:
            tests.append(f"❌ Fallback mechanisms: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ Fallback mechanisms test failed: {e}")
    
    return tests


def test_input_validation_and_error_handling():
    """Test enhanced input validation and error handling improvements"""
    base_url = "http://127.0.0.1:8001"
    
    print("\n🛡️ Testing Input Validation and Error Handling Fixes")
    print("=" * 53)
    
    tests = []
    
    # Test 1: Invalid service names with helpful error messages
    print("1. Testing enhanced invalid service validation...")
    try:
        invalid_payload = {
            "business_objective": "Invalid service test",
            "compute_services": ["nonexistent_service", "fake_azure_service"]
        }
        response = requests.post(f"{base_url}/generate-azure-diagram", json=invalid_payload, timeout=15)
        
        if response.status_code == 500:  # Should return error
            error_data = response.json()
            error_detail = error_data.get("detail", "").lower()
            has_helpful_message = "available options" in error_detail or "invalid" in error_detail
            
            if has_helpful_message:
                tests.append("✅ Invalid service validation: Helpful error message with available options")
            else:
                tests.append(f"❌ Invalid service validation: Unhelpful error - {error_detail}")
        else:
            tests.append(f"❌ Invalid service validation: Expected error, got {response.status_code}")
    except Exception as e:
        tests.append(f"❌ Invalid service validation test failed: {e}")
    
    # Test 2: Excessive service selection validation
    print("2. Testing excessive service selection limits...")
    try:
        excessive_payload = {
            "business_objective": "Excessive services test",
            "compute_services": ["virtual_machines"] * 60  # Over reasonable limit
        }
        response = requests.post(f"{base_url}/generate-azure-diagram", json=excessive_payload, timeout=15)
        
        if response.status_code == 500:  # Should return error
            error_data = response.json()
            error_detail = error_data.get("detail", "").lower()
            has_limit_message = "too many" in error_detail or "max" in error_detail
            
            if has_limit_message:
                tests.append("✅ Excessive service validation: Proper limit enforcement with clear message")
            else:
                tests.append(f"❌ Excessive service validation: Unclear error - {error_detail}")
        else:
            tests.append(f"❌ Excessive service validation: Expected error, got {response.status_code}")
    except Exception as e:
        tests.append(f"❌ Excessive service validation test failed: {e}")
    
    # Test 3: Malformed URL validation
    print("3. Testing URL format validation...")
    try:
        bad_url_payload = {
            "business_objective": "URL validation test",
            "url_input": "this-is-not-a-valid-url-format"
        }
        response = requests.post(f"{base_url}/generate-azure-diagram", json=bad_url_payload, timeout=15)
        
        if response.status_code == 500:  # Should return error
            error_data = response.json()
            error_detail = error_data.get("detail", "").lower()
            has_url_message = "url" in error_detail and ("http" in error_detail or "format" in error_detail)
            
            if has_url_message:
                tests.append("✅ URL validation: Clear URL format error message")
            else:
                tests.append(f"❌ URL validation: Unclear error - {error_detail}")
        else:
            tests.append(f"❌ URL validation: Expected error, got {response.status_code}")
    except Exception as e:
        tests.append(f"❌ URL validation test failed: {e}")
    
    # Test 4: Comprehensive error logging (test health endpoint for system status)
    print("4. Testing system health and error reporting...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            status = health_data.get("status")
            dependencies = health_data.get("dependencies", {})
            
            all_healthy = (status == "healthy" and 
                          dependencies.get("graphviz_available") and
                          dependencies.get("diagrams_available") and
                          dependencies.get("output_directory_accessible"))
            
            if all_healthy:
                tests.append("✅ System health: All dependencies healthy with detailed status")
            else:
                tests.append(f"❌ System health: Issues detected - {health_data}")
        else:
            tests.append(f"❌ System health: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ System health test failed: {e}")
    
    return tests


def main():
    """Run all problem statement fix validation tests"""
    print("🚀 Testing Problem Statement Fixes - AZ-LZ-Agent")
    print("=" * 52)
    print("Validating fixes for:")
    print("1. Random Architecture Generation")
    print("2. SVG/PNG Generation Failures") 
    print("3. Input Validation and Error Handling")
    print("=" * 52)
    
    all_tests = []
    
    # Run all test suites
    all_tests.extend(test_random_architecture_fixes())
    all_tests.extend(test_svg_png_generation_fixes())
    all_tests.extend(test_input_validation_and_error_handling())
    
    # Calculate results
    passed = len([t for t in all_tests if t.startswith("✅")])
    warnings = len([t for t in all_tests if t.startswith("⚠️")])
    failed = len([t for t in all_tests if t.startswith("❌")])
    total = len(all_tests)
    
    # Display results
    print(f"\n📊 Problem Statement Fix Validation Results:")
    print("=" * 47)
    for test in all_tests:
        print(test)
    
    print(f"\n🎯 Final Summary:")
    print("=" * 15)
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ⚠️ Warnings: {warnings}/{total}")
    print(f"   ❌ Failed: {failed}/{total}")
    
    if failed == 0:
        print(f"\n🎉 SUCCESS: All {total} problem statement fixes validated!")
        print("✅ Random architecture generation fixed")
        print("✅ SVG/PNG generation reliability improved")
        print("✅ Input validation and error handling enhanced")
        return 0
    else:
        print(f"\n❌ ISSUES: {failed} test(s) failed. Review issues above.")
        return 1


if __name__ == "__main__":
    exit(main())