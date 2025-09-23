#!/usr/bin/env python3
"""
Test script for LangGraph Hub-Spoke Orchestration

This script tests the new LangGraph agent orchestration functionality
for the Azure Landing Zone Agent.
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_langgraph_workflow():
    """Test the LangGraph workflow independently"""
    print("Testing LangGraph Hub-Spoke Workflow...")
    
    try:
        # Import the workflow module
        from langgraph_workflow import AzureLandingZoneOrchestrator, categorize_services_by_hub_spoke, create_orchestrator
        
        # Test service categorization
        test_services = [
            'firewall', 'bastion', 'dns', 'app_services', 'sql_database', 
            'virtual_machines', 'security_center', 'storage_accounts', 'aks'
        ]
        
        categories = categorize_services_by_hub_spoke(test_services)
        print(f"✅ Service categorization test passed:")
        print(f"   Hub services: {categories['hub_services']}")
        print(f"   Spoke services: {categories['spoke_services']}")
        
        # Test orchestrator creation
        orchestrator = create_orchestrator()
        print("✅ Orchestrator created successfully")
        
        # Test sample workflow execution
        sample_inputs = {
            "business_objective": "Enterprise web application with high availability",
            "network_services": ["firewall", "bastion", "vpn_gateway"],
            "compute_services": ["app_services", "virtual_machines"],
            "database_services": ["sql_database"],
            "storage_services": ["storage_accounts"],
            "security_services": ["key_vault", "security_center"],
            "scalability": "high",
            "security_posture": "zero_trust"
        }
        
        result = orchestrator.process_landing_zone_request(sample_inputs)
        
        if result.get("final_result", {}).get("success"):
            print("✅ Workflow execution test passed")
            print(f"   Hub services count: {result['final_result'].get('hub_services_count', 0)}")
            print(f"   Spoke services count: {result['final_result'].get('spoke_services_count', 0)}")
            print(f"   Architecture pattern: {result['final_result'].get('architecture_pattern', 'unknown')}")
        else:
            print("❌ Workflow execution test failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ LangGraph workflow test failed: {e}")
        traceback.print_exc()
        return False

def test_main_integration():
    """Test integration with main.py"""
    print("\nTesting Main.py Integration...")
    
    try:
        # Test imports
        from main import CustomerInputs, langgraph_orchestrator, generate_professional_mermaid_with_orchestration
        
        print("✅ Main.py imports successful")
        
        # Test CustomerInputs model
        sample_inputs = CustomerInputs(
            business_objective="Test enterprise application",
            network_services=["firewall", "bastion"],
            compute_services=["app_services"],
            database_services=["sql_database"],
            scalability="moderate"
        )
        
        print("✅ CustomerInputs model test passed")
        
        # Test orchestrator availability
        if langgraph_orchestrator:
            print("✅ LangGraph orchestrator is available in main.py")
        else:
            print("⚠️ LangGraph orchestrator is not available (may be expected if dependencies not installed)")
        
        return True
        
    except Exception as e:
        print(f"❌ Main.py integration test failed: {e}")
        traceback.print_exc()
        return False

def test_mermaid_generation():
    """Test Mermaid diagram generation with orchestration"""
    print("\nTesting Mermaid Diagram Generation...")
    
    try:
        from main import CustomerInputs, generate_professional_mermaid_with_orchestration
        from langgraph_workflow import create_orchestrator
        
        # Create test inputs
        inputs = CustomerInputs(
            business_objective="Test web application",
            network_services=["firewall", "bastion", "dns"],
            compute_services=["app_services", "virtual_machines"],
            database_services=["sql_database"],
            storage_services=["storage_accounts"],
            security_services=["security_center"],
            scalability="high"
        )
        
        # Test with orchestration
        orchestrator = create_orchestrator()
        orchestration_result = orchestrator.process_landing_zone_request(inputs.dict())
        
        mermaid_output = generate_professional_mermaid_with_orchestration(inputs, orchestration_result)
        
        # Basic validation
        if "Hub Infrastructure" in mermaid_output and "Spoke" in mermaid_output:
            print("✅ Mermaid diagram generation test passed")
            print(f"   Generated diagram length: {len(mermaid_output)} characters")
            print(f"   Contains hub-spoke separation: {'Hub Infrastructure' in mermaid_output}")
            return True
        else:
            print("❌ Mermaid diagram generation test failed - missing expected content")
            return False
        
    except Exception as e:
        print(f"❌ Mermaid diagram generation test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Azure Landing Zone Agent - LangGraph Hub-Spoke Orchestration")
    print("=" * 70)
    
    tests = [
        test_langgraph_workflow,
        test_main_integration,
        test_mermaid_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LangGraph integration is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())