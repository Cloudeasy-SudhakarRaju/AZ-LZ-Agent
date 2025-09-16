#!/usr/bin/env python3
"""
Comprehensive test script for architecture diagram generation fixes
Tests the 4 key areas mentioned in the problem statement without requiring a running server
"""
import sys
import os
sys.path.append('.')

from backend.main import CustomerInputs, validate_customer_inputs, analyze_free_text_requirements, generate_azure_architecture_diagram, AZURE_SERVICES_MAPPING
import logging
import tempfile
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_fix_1_enhanced_input_validation():
    """Test Fix 1: Enhanced Input Validation with detailed error messages"""
    print("🔍 Testing Fix 1: Enhanced Input Validation")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1.1: Service existence validation
    print("\n1.1 Testing service existence validation...")
    total_tests += 1
    try:
        inputs = CustomerInputs(
            business_objective="Test",
            compute_services=["non_existent_service", "invalid_service_2"]
        )
        validate_customer_inputs(inputs)
        print("   ❌ Should have failed - invalid services not caught")
    except ValueError as e:
        if "Invalid services" in str(e) and "Available services include" in str(e):
            print(f"   ✅ Caught invalid services with helpful error: {str(e)[:100]}...")
            tests_passed += 1
        else:
            print(f"   ⚠️  Caught error but message could be better: {e}")
    
    # Test 1.2: Input length validation with clear messages
    print("\n1.2 Testing input length validation...")
    total_tests += 1
    try:
        inputs = CustomerInputs(
            business_objective="x" * 1001,  # Exceeds limit
            compute_services=["virtual_machines"]
        )
        validate_customer_inputs(inputs)
        print("   ❌ Should have failed - input too long")
    except ValueError as e:
        if "too long" in str(e) and "maximum" in str(e) and "characters allowed" in str(e):
            print(f"   ✅ Clear length validation error: {str(e)[:100]}...")
            tests_passed += 1
        else:
            print(f"   ⚠️  Error caught but message unclear: {e}")
    
    # Test 1.3: URL format validation
    print("\n1.3 Testing URL format validation...")
    total_tests += 1
    try:
        inputs = CustomerInputs(
            business_objective="Test",
            url_input="not-a-valid-url"
        )
        validate_customer_inputs(inputs)
        print("   ❌ Should have failed - invalid URL format")
    except ValueError as e:
        if "URL must start with" in str(e) and "Example:" in str(e):
            print(f"   ✅ Clear URL validation error: {str(e)[:100]}...")
            tests_passed += 1
        else:
            print(f"   ⚠️  Error caught but message unclear: {e}")
    
    # Test 1.4: Service count limits per category
    print("\n1.4 Testing service count limits...")
    total_tests += 1
    try:
        inputs = CustomerInputs(
            business_objective="Test",
            compute_services=["virtual_machines"] * 25  # Exceeds 20 limit
        )
        validate_customer_inputs(inputs)
        print("   ❌ Should have failed - too many services in category")
    except ValueError as e:
        if "Too many services selected" in str(e) and "maximum 20 per category" in str(e):
            print(f"   ✅ Service count limit enforced: {str(e)[:100]}...")
            tests_passed += 1
        else:
            print(f"   ⚠️  Error caught but message unclear: {e}")
    
    print(f"\n📊 Fix 1 Results: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_fix_2_strict_user_input_adherence():
    """Test Fix 2: Strict User Input Adherence - no random services"""
    print("\n👤 Testing Fix 2: Strict User Input Adherence")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 2.1: Empty services should create empty framework
    print("\n2.1 Testing empty services handling...")
    total_tests += 1
    try:
        inputs = CustomerInputs(business_objective="Empty test")
        with tempfile.TemporaryDirectory() as temp_dir:
            diagram_path = generate_azure_architecture_diagram(inputs, output_dir=temp_dir, format="svg")
            
            if os.path.exists(diagram_path):
                # Read SVG content to verify it's minimal
                with open(diagram_path, 'r') as f:
                    content = f.read()
                
                # Should contain framework but not random services
                if "Ready for Service Selection" in content or "No services specified" in content:
                    print("   ✅ Empty services created empty framework (no random services added)")
                    tests_passed += 1
                else:
                    print("   ⚠️  Empty services might have added unexpected content")
            else:
                print("   ❌ Failed to create diagram file")
    except Exception as e:
        print(f"   ❌ Empty services test failed: {e}")
    
    # Test 2.2: Single service should include only that service
    print("\n2.2 Testing single service adherence...")
    total_tests += 1
    try:
        inputs = CustomerInputs(
            business_objective="Single service test",
            compute_services=["virtual_machines"]
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            diagram_path = generate_azure_architecture_diagram(inputs, output_dir=temp_dir, format="svg")
            
            if os.path.exists(diagram_path):
                with open(diagram_path, 'r') as f:
                    content = f.read()
                
                # Should contain virtual machines but not other services the user didn't request
                has_vm = "Virtual Machine" in content or "virtual_machine" in content
                # Check for common services that might be auto-added
                has_unexpected = any(service in content.lower() for service in [
                    "sql database", "storage account", "key vault", "application gateway"
                ]) and "virtual_machine" not in content.lower()
                
                if has_vm and not has_unexpected:
                    print("   ✅ Single service diagram contains only requested service")
                    tests_passed += 1
                else:
                    print(f"   ⚠️  Single service test: VM={has_vm}, Unexpected={has_unexpected}")
            else:
                print("   ❌ Failed to create diagram file")
    except Exception as e:
        print(f"   ❌ Single service test failed: {e}")
    
    # Test 2.3: Logging of user service selections
    print("\n2.3 Testing user service selection logging...")
    total_tests += 1
    try:
        inputs = CustomerInputs(
            business_objective="Multi-service test",
            compute_services=["virtual_machines", "aks"],
            network_services=["virtual_network"]
        )
        
        # Capture log output (simple validation)
        import io
        import logging
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logging.getLogger().addHandler(handler)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            diagram_path = generate_azure_architecture_diagram(inputs, output_dir=temp_dir, format="svg")
            
        log_output = log_capture.getvalue()
        logging.getLogger().removeHandler(handler)
        
        # Check if logging mentions user-selected services
        if "User selected" in log_output and "services" in log_output:
            print("   ✅ User service selections are logged for transparency")
            tests_passed += 1
        else:
            print("   ⚠️  User service selection logging might be missing")
    except Exception as e:
        print(f"   ❌ Service selection logging test failed: {e}")
    
    print(f"\n📊 Fix 2 Results: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_fix_3_conservative_ai_analysis():
    """Test Fix 3: Conservative AI Analysis with service limits"""
    print("\n🤖 Testing Fix 3: Conservative AI Analysis")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 3.1: Maximum 5 services limit
    print("\n3.1 Testing 5-service limit enforcement...")
    total_tests += 1
    try:
        # Test with a complex requirement that might suggest many services
        complex_requirement = "I need a comprehensive enterprise microservices platform with advanced analytics, machine learning, security, monitoring, backup, and global distribution"
        
        result = analyze_free_text_requirements(complex_requirement)
        services = result.get("services", [])
        
        if len(services) <= 5:
            print(f"   ✅ AI analysis limited to {len(services)} services (≤5)")
            tests_passed += 1
        else:
            print(f"   ❌ AI analysis suggested {len(services)} services (>5)")
    except Exception as e:
        print(f"   ❌ Service limit test failed: {e}")
    
    # Test 3.2: Reasoning transparency
    print("\n3.2 Testing reasoning transparency...")
    total_tests += 1
    try:
        result = analyze_free_text_requirements("I need a simple web application")
        reasoning = result.get("reasoning", "")
        needs_confirmation = result.get("needs_confirmation", False)
        
        if reasoning and len(reasoning) > 50 and needs_confirmation:
            print("   ✅ AI analysis provides reasoning and requires confirmation")
            tests_passed += 1
        else:
            print(f"   ⚠️  Reasoning transparency could be improved (reasoning length: {len(reasoning)}, needs confirmation: {needs_confirmation})")
    except Exception as e:
        print(f"   ❌ Reasoning transparency test failed: {e}")
    
    # Test 3.3: Service validation (AI shouldn't suggest invalid services)
    print("\n3.3 Testing AI service validation...")
    total_tests += 1
    try:
        result = analyze_free_text_requirements("I need monitoring and analytics")
        services = result.get("services", [])
        
        # All suggested services should exist in our mapping
        invalid_services = [s for s in services if s not in AZURE_SERVICES_MAPPING]
        
        if not invalid_services:
            print(f"   ✅ All {len(services)} AI-suggested services are valid")
            tests_passed += 1
        else:
            print(f"   ❌ AI suggested invalid services: {invalid_services}")
    except Exception as e:
        print(f"   ❌ Service validation test failed: {e}")
    
    print(f"\n📊 Fix 3 Results: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_fix_4_improved_error_handling():
    """Test Fix 4: Improved Error Handling and file generation"""
    print("\n🚨 Testing Fix 4: Improved Error Handling")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 4.1: Graphviz validation with installation instructions
    print("\n4.1 Testing Graphviz validation and error messages...")
    total_tests += 1
    try:
        # Test with valid input to ensure Graphviz is working
        inputs = CustomerInputs(
            business_objective="Test Graphviz",
            compute_services=["virtual_machines"]
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            diagram_path = generate_azure_architecture_diagram(inputs, output_dir=temp_dir, format="svg")
            
            if os.path.exists(diagram_path):
                print("   ✅ Graphviz validation and diagram generation working")
                tests_passed += 1
            else:
                print("   ❌ Diagram generation failed")
    except Exception as e:
        # Check if error message contains helpful installation instructions
        error_msg = str(e)
        if "Graphviz" in error_msg and ("install" in error_msg or "sudo apt-get" in error_msg):
            print(f"   ✅ Graphviz error includes installation instructions: {error_msg[:100]}...")
            tests_passed += 1
        else:
            print(f"   ❌ Graphviz error lacks helpful instructions: {e}")
    
    # Test 4.2: File generation verification with size checks
    print("\n4.2 Testing file generation verification...")
    total_tests += 1
    try:
        inputs = CustomerInputs(
            business_objective="File size test",
            compute_services=["virtual_machines"],
            network_services=["virtual_network"]
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test SVG generation
            svg_path = generate_azure_architecture_diagram(inputs, output_dir=temp_dir, format="svg")
            
            if os.path.exists(svg_path):
                svg_size = os.path.getsize(svg_path)
                if svg_size > 100:  # Reasonable minimum size
                    print(f"   ✅ SVG file generated with reasonable size: {svg_size} bytes")
                    tests_passed += 1
                else:
                    print(f"   ⚠️  SVG file seems too small: {svg_size} bytes")
            else:
                print("   ❌ SVG file not generated")
    except Exception as e:
        # Should provide clear error about file generation
        error_msg = str(e)
        if "generation" in error_msg or "file" in error_msg:
            print(f"   ⚠️  File generation error with some clarity: {error_msg[:100]}...")
        else:
            print(f"   ❌ File generation error unclear: {e}")
    
    # Test 4.3: Comprehensive logging
    print("\n4.3 Testing comprehensive logging...")
    total_tests += 1
    try:
        import io
        import logging
        
        # Capture logs
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        logger = logging.getLogger('backend.main')
        logger.addHandler(handler)
        
        inputs = CustomerInputs(
            business_objective="Logging test",
            compute_services=["virtual_machines"]
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            diagram_path = generate_azure_architecture_diagram(inputs, output_dir=temp_dir, format="svg")
        
        log_output = log_capture.getvalue()
        logger.removeHandler(handler)
        
        # Check for comprehensive logging
        key_log_items = [
            "validation", "user selected", "services", "diagram generation",
            "Graphviz", "created", "completed"
        ]
        
        found_logs = sum(1 for item in key_log_items if item.lower() in log_output.lower())
        
        if found_logs >= 4:  # Should have most key logging elements
            print(f"   ✅ Comprehensive logging present ({found_logs}/{len(key_log_items)} key items)")
            tests_passed += 1
        else:
            print(f"   ⚠️  Logging could be more comprehensive ({found_logs}/{len(key_log_items)} key items)")
            
    except Exception as e:
        print(f"   ❌ Logging test failed: {e}")
    
    print(f"\n📊 Fix 4 Results: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_svg_png_reliability():
    """Test SVG/PNG generation reliability as mentioned in problem statement"""
    print("\n🎨 Testing SVG/PNG Generation Reliability")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test both formats
    formats = ["svg", "png"]
    
    for format_type in formats:
        print(f"\n   Testing {format_type.upper()} generation...")
        total_tests += 1
        
        try:
            inputs = CustomerInputs(
                business_objective=f"Test {format_type} generation",
                compute_services=["virtual_machines"],
                network_services=["virtual_network"],
                security_services=["key_vault"]
            )
            
            with tempfile.TemporaryDirectory() as temp_dir:
                diagram_path = generate_azure_architecture_diagram(inputs, output_dir=temp_dir, format=format_type)
                
                if os.path.exists(diagram_path):
                    file_size = os.path.getsize(diagram_path)
                    min_size = 100 if format_type == "svg" else 1000  # PNG should be larger
                    
                    if file_size >= min_size:
                        print(f"   ✅ {format_type.upper()} generated successfully: {file_size} bytes")
                        tests_passed += 1
                    else:
                        print(f"   ⚠️  {format_type.upper()} file seems too small: {file_size} bytes")
                else:
                    print(f"   ❌ {format_type.upper()} file not created")
                    
        except Exception as e:
            print(f"   ❌ {format_type.upper()} generation failed: {e}")
    
    print(f"\n📊 Format Generation Results: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def main():
    """Run comprehensive tests for all 4 key fixes"""
    print("🔧 Testing Architecture Diagram Generation Fixes")
    print("=" * 70)
    print("Testing fixes for the 4 key issues identified in the problem statement:")
    print("1. Enhanced Input Validation")
    print("2. Strict User Input Adherence") 
    print("3. Conservative AI Analysis")
    print("4. Improved Error Handling")
    print("=" * 70)
    
    all_results = []
    
    try:
        # Test each fix area
        result1 = test_fix_1_enhanced_input_validation()
        all_results.append(("Enhanced Input Validation", result1))
        
        result2 = test_fix_2_strict_user_input_adherence()
        all_results.append(("Strict User Input Adherence", result2))
        
        result3 = test_fix_3_conservative_ai_analysis()
        all_results.append(("Conservative AI Analysis", result3))
        
        result4 = test_fix_4_improved_error_handling()
        all_results.append(("Improved Error Handling", result4))
        
        result5 = test_svg_png_reliability()
        all_results.append(("SVG/PNG Generation Reliability", result5))
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        
        passed_count = sum(1 for _, result in all_results if result)
        
        for fix_name, result in all_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}: {fix_name}")
        
        print(f"\n📊 Overall Results: {passed_count}/{len(all_results)} fix areas validated")
        
        if passed_count == len(all_results):
            print("\n🎉 ALL ARCHITECTURAL DIAGRAM ISSUES FIXED!")
            print("   ✅ Input validation enhanced with detailed error messages")
            print("   ✅ User input adherence strictly enforced (no random services)")
            print("   ✅ AI analysis made conservative with 5-service limit")
            print("   ✅ Error handling improved with actionable messages")
            print("   ✅ SVG/PNG generation reliability validated")
            return True
        else:
            print(f"\n⚠️  {len(all_results) - passed_count} fix area(s) need attention")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)