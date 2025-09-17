#!/usr/bin/env python3
"""
Test script for Figma API integration with Azure Landing Zone Agent.
This script demonstrates how to use the new Figma diagram generation feature.
"""

import requests
import json
import os
import sys

# Configuration
API_BASE_URL = "http://localhost:8001"
FIGMA_API_TOKEN = os.getenv('FIGMA_API_TOKEN')  # Set this in your environment
FIGMA_FILE_ID = os.getenv('FIGMA_FILE_ID')     # Set this in your environment

def test_figma_token_validation():
    """Test Figma API token validation."""
    print("🔍 Testing Figma API token validation...")
    
    if not FIGMA_API_TOKEN:
        print("❌ FIGMA_API_TOKEN not set. Please set this environment variable.")
        return False
    
    # Test token validation through the FigmaConfig class
    try:
        from scripts.arch_agent.figma_renderer import FigmaConfig
        is_valid = FigmaConfig.validate_token(FIGMA_API_TOKEN)
        
        if is_valid:
            print("✅ Figma API token is valid")
            user_info = FigmaConfig.get_user_info(FIGMA_API_TOKEN)
            if user_info:
                print(f"   User: {user_info.get('name', 'Unknown')}")
                print(f"   Email: {user_info.get('email', 'Unknown')}")
            return True
        else:
            print("❌ Figma API token is invalid")
            return False
            
    except Exception as e:
        print(f"❌ Error validating token: {e}")
        return False

def test_api_endpoints():
    """Test that the API endpoints are available."""
    print("\n🔍 Testing API endpoints...")
    
    try:
        # Test root endpoint
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get('endpoints', [])
            figma_endpoint = any('/generate-figma-diagram' in ep for ep in endpoints)
            
            if figma_endpoint:
                print("✅ Figma endpoint is available")
                return True
            else:
                print("❌ Figma endpoint not found in API")
                return False
        else:
            print(f"❌ API not responding: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_figma_diagram_generation():
    """Test the full Figma diagram generation workflow."""
    print("\n🔍 Testing Figma diagram generation...")
    
    if not FIGMA_API_TOKEN or not FIGMA_FILE_ID:
        print("❌ Missing required environment variables:")
        print("   - FIGMA_API_TOKEN: Your Figma personal access token")
        print("   - FIGMA_FILE_ID: ID of an existing Figma file")
        print("\nTo set these:")
        print("   export FIGMA_API_TOKEN=figd_xxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("   export FIGMA_FILE_ID=abc123def456ghi789")
        return False
    
    # Sample architecture request
    request_data = {
        "customer_inputs": {
            "business_objective": "Test architecture generation",
            "free_text_input": "Create a simple web application with load balancer, VMs, database, and storage for testing Figma integration",
            "compute_services": ["virtual_machines", "app_services"],
            "network_services": ["virtual_network", "load_balancer"],
            "storage_services": ["storage_accounts"],
            "database_services": ["sql_database"],
            "security_services": ["key_vault", "active_directory"],
            "security_posture": "standard"
        },
        "figma_api_token": FIGMA_API_TOKEN,
        "figma_file_id": FIGMA_FILE_ID,
        "page_name": "Test Azure Architecture",
        "pattern": "ha-multiregion"
    }
    
    try:
        print("📤 Sending request to generate Figma diagram...")
        response = requests.post(
            f"{API_BASE_URL}/generate-figma-diagram",
            headers={"Content-Type": "application/json"},
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Figma diagram generated successfully!")
                print(f"   Figma URL: {result.get('figma_url')}")
                print(f"   File ID: {result.get('figma_file_id')}")
                print(f"   Page: {result.get('figma_page_name')}")
                
                if result.get('user_info'):
                    print(f"   Account: {result['user_info'].get('name', 'Unknown')}")
                
                return True
            else:
                print(f"❌ Generation failed: {result}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"   Error: {error_detail}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False

def test_backend_imports():
    """Test that backend imports work correctly."""
    print("\n🔍 Testing backend imports...")
    
    try:
        # Test architecture agent import
        sys.path.append('/home/runner/work/AZ-LZ-Agent/AZ-LZ-Agent')
        from scripts.arch_agent.agent import ArchitectureDiagramAgent
        from scripts.arch_agent.figma_renderer import FigmaRenderer, FigmaConfig
        
        print("✅ Successfully imported architecture agent components")
        
        # Test agent initialization
        agent = ArchitectureDiagramAgent()
        print("✅ Architecture agent initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Azure Landing Zone Agent - Figma Integration Test")
    print("=" * 55)
    
    # Run tests
    tests = [
        test_backend_imports,
        test_api_endpoints,
        test_figma_token_validation,
        test_figma_diagram_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Figma integration is working correctly.")
        
        if FIGMA_API_TOKEN and FIGMA_FILE_ID:
            print("\n🔗 Next steps:")
            print("   1. Check your Figma file for the generated diagram")
            print("   2. Try the frontend interface for a better user experience")
            print("   3. Explore different architecture patterns and services")
        else:
            print("\n💡 To test diagram generation, set these environment variables:")
            print("   export FIGMA_API_TOKEN=figd_xxxxxxxxxxxxxxxxxxxxxxxxxx")
            print("   export FIGMA_FILE_ID=abc123def456ghi789")
    else:
        print(f"❌ {total - passed} tests failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())