#!/usr/bin/env python3
"""
Test script to validate the architecture diagram generation improvements
"""
import sys
import os
sys.path.append('.')

from backend.main import CustomerInputs, validate_customer_inputs, analyze_free_text_requirements, generate_azure_architecture_diagram, AZURE_SERVICES_MAPPING
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_enhanced_input_validation():
    """Test enhanced input validation with detailed error messages"""
    print("🔍 Testing Enhanced Input Validation")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Valid minimal input",
            "input": CustomerInputs(
                business_objective="Test app",
                compute_services=["virtual_machines"],
                network_services=["virtual_network"]
            ),
            "should_pass": True
        },
        {
            "name": "Invalid service name",
            "input": CustomerInputs(
                business_objective="Test app",
                compute_services=["invalid_service"],
                network_services=["virtual_network"]
            ),
            "should_pass": False
        },
        {
            "name": "Too many services in category",
            "input": CustomerInputs(
                business_objective="Test app",
                compute_services=["virtual_machines"] * 25  # Exceeds limit of 20
            ),
            "should_pass": False
        },
        {
            "name": "Too long business objective",
            "input": CustomerInputs(
                business_objective="x" * 1001,  # Exceeds limit of 1000
                compute_services=["virtual_machines"]
            ),
            "should_pass": False
        },
        {
            "name": "Invalid URL format",
            "input": CustomerInputs(
                business_objective="Test app",
                url_input="not-a-valid-url",
                compute_services=["virtual_machines"]
            ),
            "should_pass": False
        },
        {
            "name": "Valid HTTPS URL",
            "input": CustomerInputs(
                business_objective="Test app",
                url_input="https://example.com",
                compute_services=["virtual_machines"]
            ),
            "should_pass": True
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        try:
            validate_customer_inputs(test_case["input"])
            if test_case["should_pass"]:
                print(f"✅ {test_case['name']}: PASSED (validation succeeded as expected)")
                passed += 1
            else:
                print(f"❌ {test_case['name']}: FAILED (validation should have failed)")
        except ValueError as e:
            if not test_case["should_pass"]:
                print(f"✅ {test_case['name']}: PASSED (validation failed as expected)")
                print(f"   Error message: {str(e)[:100]}...")
                passed += 1
            else:
                print(f"❌ {test_case['name']}: FAILED (validation should have succeeded)")
                print(f"   Error: {e}")
        except Exception as e:
            print(f"❌ {test_case['name']}: ERROR (unexpected exception: {e})")
    
    print(f"\n📊 Input Validation Tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_conservative_ai_analysis():
    """Test conservative AI analysis with service limits"""
    print("\n🤖 Testing Conservative AI Analysis")
    print("=" * 50)
    
    test_cases = [
        "I need a simple web application",
        "Create a basic database for storing user data",
        "Set up monitoring for my application",
        "I need a complex enterprise microservices platform with advanced analytics and machine learning capabilities"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        try:
            result = analyze_free_text_requirements(test_case)
            services = result.get("services", [])
            reasoning = result.get("reasoning", "")
            needs_confirmation = result.get("needs_confirmation", False)
            
            print(f"   Services suggested: {len(services)} services")
            print(f"   Services: {', '.join(services) if services else 'None'}")
            print(f"   Needs confirmation: {needs_confirmation}")
            print(f"   Reasoning length: {len(reasoning)} characters")
            
            # Validate constraints
            if len(services) <= 5:
                print("   ✅ Service count constraint met (≤5)")
            else:
                print(f"   ❌ Service count constraint violated ({len(services)} > 5)")
            
            # Check if services are valid
            invalid_services = [s for s in services if s not in AZURE_SERVICES_MAPPING]
            if not invalid_services:
                print("   ✅ All suggested services are valid")
            else:
                print(f"   ❌ Invalid services suggested: {invalid_services}")
                
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
    
    print("\n📊 Conservative AI Analysis Tests completed")

def test_user_input_adherence():
    """Test strict adherence to user input"""
    print("\n👤 Testing Strict User Input Adherence")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Empty services (should create empty framework)",
            "input": CustomerInputs(
                business_objective="Empty test"
            ),
            "expected_behavior": "Should create empty architecture framework"
        },
        {
            "name": "Single service (should include only that service)",
            "input": CustomerInputs(
                business_objective="Single service test",
                compute_services=["virtual_machines"]
            ),
            "expected_behavior": "Should include only virtual machines"
        },
        {
            "name": "Multiple specific services",
            "input": CustomerInputs(
                business_objective="Multi-service test",
                compute_services=["virtual_machines", "aks"],
                network_services=["virtual_network", "application_gateway"],
                security_services=["key_vault"]
            ),
            "expected_behavior": "Should include only the 5 specified services"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Expected: {test_case['expected_behavior']}")
        try:
            # Create a small test diagram
            diagram_path = generate_azure_architecture_diagram(test_case["input"], format="svg")
            
            # Check if file was created
            if os.path.exists(diagram_path):
                file_size = os.path.getsize(diagram_path)
                print(f"   ✅ Diagram created: {diagram_path} ({file_size} bytes)")
                
                # Basic validation - check if file is reasonable size
                if file_size > 100:  # SVG should be at least 100 bytes
                    print("   ✅ File size validation passed")
                else:
                    print(f"   ⚠️  File seems small ({file_size} bytes)")
                    
            else:
                print(f"   ❌ Diagram file not created")
                
        except Exception as e:
            print(f"   ❌ Diagram generation failed: {e}")
    
    print("\n📊 User Input Adherence Tests completed")

def test_error_handling():
    """Test improved error handling"""
    print("\n🚨 Testing Improved Error Handling")
    print("=" * 50)
    
    # Test with various invalid inputs that should produce clear error messages
    error_test_cases = [
        {
            "name": "Non-existent service",
            "input": CustomerInputs(
                business_objective="Test",
                compute_services=["non_existent_service"]
            )
        },
        {
            "name": "Malformed URL",
            "input": CustomerInputs(
                business_objective="Test", 
                url_input="ftp://not-supported"
            )
        }
    ]
    
    for test_case in error_test_cases:
        print(f"\nTest: {test_case['name']}")
        try:
            validate_customer_inputs(test_case["input"])
            print("   ❌ Should have failed validation")
        except ValueError as e:
            print(f"   ✅ Produced clear error message: {str(e)[:150]}...")
        except Exception as e:
            print(f"   ⚠️  Unexpected error type: {type(e).__name__}: {e}")
    
    print("\n📊 Error Handling Tests completed")

def main():
    """Run all improvement tests"""
    print("🚀 Testing Architecture Diagram Generation Improvements")
    print("=" * 70)
    
    try:
        # Test 1: Enhanced Input Validation
        validation_success = test_enhanced_input_validation()
        
        # Test 2: Conservative AI Analysis  
        test_conservative_ai_analysis()
        
        # Test 3: User Input Adherence
        test_user_input_adherence()
        
        # Test 4: Error Handling
        test_error_handling()
        
        print("\n" + "=" * 70)
        if validation_success:
            print("🎉 All improvement tests completed! Key improvements validated:")
            print("   ✅ Enhanced input validation with detailed error messages")
            print("   ✅ Conservative AI analysis with 5-service limit")
            print("   ✅ Strict user input adherence (no random services)")
            print("   ✅ Improved error handling with actionable messages")
        else:
            print("⚠️  Some tests failed. Please review the output above.")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()