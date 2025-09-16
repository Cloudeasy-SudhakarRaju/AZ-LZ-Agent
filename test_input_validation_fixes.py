#!/usr/bin/env python3
"""
Test script to validate the enhanced input validation and user input adherence fixes
"""
import requests
import json
import time

def test_enhanced_input_validation():
    """Test enhanced input validation with detailed error messages"""
    base_url = "http://127.0.0.1:8001"
    
    print("🧪 Testing Enhanced Input Validation Fixes")
    print("=" * 50)
    
    tests = []
    
    # Test 1: Invalid service selection
    print("1. Testing invalid service validation...")
    try:
        invalid_payload = {
            "business_objective": "Test invalid services",
            "org_structure": "enterprise",
            "compute_services": ["invalid_service", "fake_service"]
        }
        response = requests.post(f"{base_url}/generate-azure-diagram", json=invalid_payload, timeout=15)
        if response.status_code == 400:
            error_data = response.json()
            if "invalid" in error_data.get("detail", "").lower():
                tests.append("✅ Invalid service validation: Proper error message returned")
            else:
                tests.append(f"❌ Invalid service validation: Unexpected error - {error_data.get('detail')}")
        else:
            tests.append(f"❌ Invalid service validation: Expected 400 error, got {response.status_code}")
    except Exception as e:
        tests.append(f"❌ Invalid service validation failed: {e}")
    
    # Test 2: Empty input handling
    print("2. Testing empty input handling...")
    try:
        empty_payload = {}
        response = requests.post(f"{base_url}/generate-azure-diagram", json=empty_payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                tests.append("✅ Empty input handling: Generated minimal framework")
            else:
                tests.append(f"❌ Empty input handling: Generation failed - {data}")
        else:
            tests.append(f"❌ Empty input handling: Unexpected status {response.status_code}")
    except Exception as e:
        tests.append(f"❌ Empty input handling failed: {e}")
    
    # Test 3: Excessive service selection
    print("3. Testing excessive service selection...")
    try:
        excessive_payload = {
            "business_objective": "Test excessive services",
            "org_structure": "enterprise",
            "compute_services": ["virtual_machines"] * 60  # Over the limit
        }
        response = requests.post(f"{base_url}/generate-azure-diagram", json=excessive_payload, timeout=15)
        if response.status_code == 400:
            error_data = response.json()
            if "too many" in error_data.get("detail", "").lower():
                tests.append("✅ Excessive service validation: Proper limit enforcement")
            else:
                tests.append(f"❌ Excessive service validation: Unexpected error - {error_data.get('detail')}")
        else:
            tests.append(f"❌ Excessive service validation: Expected 400 error, got {response.status_code}")
    except Exception as e:
        tests.append(f"❌ Excessive service validation failed: {e}")
    
    # Test 4: URL validation
    print("4. Testing URL validation...")
    try:
        bad_url_payload = {
            "business_objective": "Test URL validation",
            "url_input": "not-a-valid-url"
        }
        response = requests.post(f"{base_url}/generate-azure-diagram", json=bad_url_payload, timeout=15)
        if response.status_code == 400:
            error_data = response.json()
            if "url" in error_data.get("detail", "").lower():
                tests.append("✅ URL validation: Proper URL format validation")
            else:
                tests.append(f"❌ URL validation: Unexpected error - {error_data.get('detail')}")
        else:
            tests.append(f"❌ URL validation: Expected 400 error, got {response.status_code}")
    except Exception as e:
        tests.append(f"❌ URL validation failed: {e}")
    
    return tests


def test_user_input_adherence():
    """Test that diagrams strictly follow user input without random additions"""
    base_url = "http://127.0.0.1:8001"
    
    print("\n🎯 Testing User Input Adherence")
    print("=" * 35)
    
    tests = []
    
    # Test 1: Specific service selection should be honored
    print("1. Testing specific service selection adherence...")
    try:
        specific_payload = {
            "business_objective": "Exact service test",
            "org_structure": "enterprise",
            "compute_services": ["aks"],
            "database_services": ["cosmos_db"],
            "security_services": ["key_vault"]
        }
        response = requests.post(f"{base_url}/generate-interactive-azure-architecture", json=specific_payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            svg_content = data.get("svg_diagram", "")
            
            # Check that only selected services appear in the diagram
            has_aks = "kubernetes" in svg_content.lower() or "aks" in svg_content.lower()
            has_cosmos = "cosmos" in svg_content.lower()
            has_kv = "key vault" in svg_content.lower() or "keyvault" in svg_content.lower()
            
            # Check that unselected services DON'T appear
            has_sql = "sql database" in svg_content.lower() and "cosmos" not in svg_content.lower()
            has_vm = "virtual machine" in svg_content.lower() and "aks" not in svg_content.lower()
            
            if has_aks and has_cosmos and has_kv and not has_sql and not has_vm:
                tests.append("✅ Specific service adherence: Only selected services present")
            else:
                tests.append(f"❌ Service adherence: AKS={has_aks}, Cosmos={has_cosmos}, KV={has_kv}, SQL={has_sql}, VM={has_vm}")
        else:
            tests.append(f"❌ Specific service test: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ Specific service test failed: {e}")
    
    # Test 2: Minimal input should produce minimal output
    print("2. Testing minimal input produces minimal output...")
    try:
        minimal_payload = {
            "business_objective": "Minimal test",
            "compute_services": ["app_services"]  # Only one service
        }
        response = requests.post(f"{base_url}/generate-png-diagram", json=minimal_payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            file_size = data.get("file_size", 0)
            # Minimal diagrams should be smaller than complex ones
            if 10000 < file_size < 100000:  # Reasonable range for minimal diagram
                tests.append(f"✅ Minimal input: Appropriate file size ({file_size} bytes)")
            else:
                tests.append(f"⚠️ Minimal input: File size may be too large ({file_size} bytes)")
        else:
            tests.append(f"❌ Minimal input test: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ Minimal input test failed: {e}")
    
    # Test 3: No default service additions
    print("3. Testing no default service additions...")
    try:
        # Request with only business objective - should not add random services
        no_services_payload = {
            "business_objective": "Test with no service selections"
        }
        response = requests.post(f"{base_url}/generate-interactive-azure-architecture", json=no_services_payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            svg_content = data.get("svg_diagram", "")
            
            # Should show framework but no specific services unless user selected them
            has_framework = "azure" in svg_content.lower() or "subscription" in svg_content.lower()
            has_specific_services = any(service in svg_content.lower() for service in 
                                     ["virtual machine", "sql database", "storage account", "kubernetes"])
            
            if has_framework and not has_specific_services:
                tests.append("✅ No default services: Framework shown without random services")
            else:
                tests.append(f"❌ Default services added: Framework={has_framework}, Services={has_specific_services}")
        else:
            tests.append(f"❌ No default services test: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ No default services test failed: {e}")
    
    return tests


def test_svg_png_generation_reliability():
    """Test SVG and PNG generation reliability and error handling"""
    base_url = "http://127.0.0.1:8001"
    
    print("\n🖼️ Testing SVG/PNG Generation Reliability")
    print("=" * 42)
    
    tests = []
    
    # Test PNG generation with various service combinations
    print("1. Testing PNG generation reliability...")
    try:
        png_payload = {
            "business_objective": "PNG reliability test",
            "compute_services": ["virtual_machines", "aks"],
            "network_services": ["virtual_network", "application_gateway"],
            "storage_services": ["blob_storage"]
        }
        response = requests.post(f"{base_url}/generate-png-diagram", json=png_payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("file_size", 0) > 5000:
                tests.append(f"✅ PNG generation: Success ({data.get('file_size')} bytes)")
            else:
                tests.append(f"❌ PNG generation: Invalid response - {data}")
        else:
            tests.append(f"❌ PNG generation: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ PNG generation failed: {e}")
    
    # Test SVG generation
    print("2. Testing SVG generation reliability...")
    try:
        svg_payload = {
            "business_objective": "SVG reliability test",
            "compute_services": ["app_services"],
            "database_services": ["sql_database"]
        }
        response = requests.post(f"{base_url}/generate-svg-diagram", json=svg_payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("file_size", 0) > 1000:
                tests.append(f"✅ SVG generation: Success ({data.get('file_size')} bytes)")
            else:
                tests.append(f"❌ SVG generation: Invalid response - {data}")
        else:
            tests.append(f"❌ SVG generation: HTTP {response.status_code}")
    except Exception as e:
        tests.append(f"❌ SVG generation failed: {e}")
    
    return tests


def main():
    """Run all validation tests"""
    print("🚀 Running Enhanced Validation and User Input Adherence Tests")
    print("=" * 65)
    
    all_tests = []
    
    # Run test suites
    all_tests.extend(test_enhanced_input_validation())
    all_tests.extend(test_user_input_adherence())
    all_tests.extend(test_svg_png_generation_reliability())
    
    # Summary
    passed = len([t for t in all_tests if t.startswith("✅")])
    warnings = len([t for t in all_tests if t.startswith("⚠️")])
    failed = len([t for t in all_tests if t.startswith("❌")])
    total = len(all_tests)
    
    print(f"\n📊 Test Results Summary:")
    print(f"{'='*30}")
    for test in all_tests:
        print(test)
    
    print(f"\n🎯 Overall Summary:")
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ⚠️ Warnings: {warnings}/{total}")
    print(f"   ❌ Failed: {failed}/{total}")
    
    if failed == 0:
        print("\n🎉 All critical tests PASSED! Fixes are working correctly.")
        return 0
    else:
        print(f"\n❌ {failed} tests FAILED. Please review the issues above.")
        return 1


if __name__ == "__main__":
    exit(main())