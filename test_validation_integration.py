#!/usr/bin/env python3
"""
Simple test script to verify the architecture validation integration.
"""
import requests
import json
import sys

def test_validation_endpoint():
    """Test the architecture validation endpoint"""
    
    print("🧪 Testing Azure Landing Zone Architecture Validation Integration")
    print("=" * 70)
    
    # Test data - represents a typical enterprise architecture request
    test_payload = {
        "business_objective": "Secure enterprise web application",
        "regulatory": "PCI-DSS compliance required", 
        "security_posture": "zero-trust",
        "compute_services": ["virtual_machines", "aks"],
        "network_services": ["azure_firewall"],
        "database_services": ["sql_database"],
        "storage_services": ["storage_accounts"],
        "monitoring": "azure-monitor",
        "backup": "comprehensive",
        "scalability": "high"
    }
    
    try:
        print("📡 Making request to validation endpoint...")
        response = requests.post(
            "http://127.0.0.1:8001/validate-architecture",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Validation Request: SUCCESS")
            print(f"📊 Compliance Score: {data['validation']['compliance_score']}%")
            print(f"📝 Total Resources Analyzed: {data['validation']['total_resources']}")
            print(f"📋 Total Issues Found: {data['validation']['total_issues']}")
            print(f"🔴 Critical Issues: {data['validation']['summary']['critical_issues']}")
            print(f"🟡 High Priority Issues: {data['validation']['summary']['high_issues']}")
            print(f"🟠 Medium Priority Issues: {data['validation']['summary']['medium_issues']}")
            print(f"🟢 Low Priority Issues: {data['validation']['summary']['low_issues']}")
            
            print("\n🎯 Issue Categories:")
            for category, count in data['validation']['summary']['issues_by_category'].items():
                print(f"   - {category}: {count} issues")
            
            print("\n🔧 Top Recommendations:")
            for i, rec in enumerate(data['validation']['summary']['top_recommendations'][:5], 1):
                print(f"   {i}. {rec}")
            
            print("\n📐 Diagram Structure:")
            ds = data['diagram_structure']
            print(f"   - Total Nodes: {ds['nodes']}")
            print(f"   - Connections: {ds['connections']}")
            print(f"   - Layout Type: {ds['layout_type']}")
            print(f"   - Hub Resources: {ds['metadata']['hub_resources']}")
            print(f"   - Spoke Resources: {ds['metadata']['spoke_resources']}")
            print(f"   - Shared Resources: {ds['metadata']['shared_resources']}")
            
            print("\n🏗️ Sample Architecture Resources:")
            for resource in data['architecture']['resources'][:3]:
                status = ""
                if 'private_endpoint' in resource:
                    status = "🔒 Secured" if resource['private_endpoint'] else "⚠️ Exposed"
                print(f"   - {resource['name']} ({resource['type']}) {status}")
            
            # Validate that critical validation features are working
            validation_checks = [
                (data['validation']['compliance_score'] >= 0, "Compliance scoring is functional"),
                (data['validation']['total_issues'] > 0, "Issue detection is working"),
                (len(data['validation']['summary']['top_recommendations']) > 0, "Recommendations are generated"),
                (data['diagram_structure']['nodes'] > 0, "Diagram structure generation is working"),
                (len(data['architecture']['resources']) > 0, "Architecture conversion is successful")
            ]
            
            print("\n✅ Validation Integration Checks:")
            all_passed = True
            for check, description in validation_checks:
                if check:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description}")
                    all_passed = False
            
            if all_passed:
                print("\n🎉 All validation integration tests PASSED!")
                print("📦 The validate_architecture.py module is successfully integrated!")
                return True
            else:
                print("\n⚠️  Some validation checks failed.")
                return False
                
        else:
            print(f"❌ Validation Request FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - server may be processing or overloaded")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def test_health_check():
    """Test that the server is running"""
    try:
        response = requests.get("http://127.0.0.1:8001/health", timeout=10)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Starting Architecture Validation Integration Tests")
    print()
    
    # Check if server is running
    if not test_health_check():
        print("❌ Backend server is not running on http://127.0.0.1:8001")
        print("Please start the server with: cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8001")
        sys.exit(1)
    
    # Run validation tests
    if test_validation_endpoint():
        print("\n🎯 Integration test completed successfully!")
        print("🔗 You can now use the validation features in your applications.")
        sys.exit(0)
    else:
        print("\n💥 Integration test failed!")
        sys.exit(1)