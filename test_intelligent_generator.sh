#!/bin/bash

# Intelligent Architecture Diagram Generator - Usage Examples
# This script demonstrates various capabilities of the intelligent diagram generator

echo "🚀 Azure Landing Zone Agent - Intelligent Diagram Generator Examples"
echo "=================================================================="
echo ""

SERVER_URL="http://127.0.0.1:8001"

# Check if server is running
echo "🔍 Checking server health..."
health_response=$(curl -s "${SERVER_URL}/health" 2>/dev/null)
if echo "$health_response" | grep -q '"status":"healthy"'; then
    echo "   ✅ Server is healthy and ready"
else
    echo "   ❌ Server is not running or unhealthy"
    echo "   💡 Start the server with: cd backend && python3 -m uvicorn main:app --reload --port 8001"
    exit 1
fi

echo ""

# Example 1: Simple Web Application
echo "📝 Example 1: Simple Web Application"
echo "-----------------------------------"
echo "Requirements: 'Create a web application with database and user authentication'"

simple_response=$(curl -s -X POST "${SERVER_URL}/generate-intelligent-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Create a web application with database backend and user authentication for a small business"
  }' --max-time 30)

if echo "$simple_response" | grep -q '"success":true'; then
    echo "   ✅ Simple web app diagram generated successfully"
    compliance_score=$(echo "$simple_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('enterprise_compliance_score', 0))")
    echo "   📊 Compliance Score: $compliance_score/100"
    
    # Count review comments
    review_count=$(echo "$simple_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('review_comments', [])))")
    echo "   📋 Review Comments: $review_count items"
else
    echo "   ❌ Simple web app diagram generation failed"
fi

echo ""

# Example 2: Enterprise Microservices
echo "📝 Example 2: Enterprise Microservices Architecture"
echo "------------------------------------------------"
echo "Requirements: 'Kubernetes-based microservices with API management and monitoring'"

microservices_response=$(curl -s -X POST "${SERVER_URL}/generate-intelligent-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Design a microservices architecture using Kubernetes with auto-scaling, API management, monitoring, and secure data storage for a financial services application requiring GDPR compliance and high availability"
  }' --max-time 30)

if echo "$microservices_response" | grep -q '"success":true'; then
    echo "   ✅ Enterprise microservices diagram generated successfully"
    compliance_score=$(echo "$microservices_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('enterprise_compliance_score', 0))")
    echo "   📊 Compliance Score: $compliance_score/100"
    
    # Show detected services
    echo "   🔧 Detected Azure Services:"
    detected_services=$(echo "$microservices_response" | python3 -c "
import sys, json, re
data = json.load(sys.stdin)
code = data.get('generated_code', '')
# Extract Azure service imports
imports = re.findall(r'from diagrams\.azure\.\w+ import (\w+)', code)
for service in sorted(set(imports)):
    print(f'      - {service}')
" 2>/dev/null)
    echo "$detected_services"
else
    echo "   ❌ Enterprise microservices diagram generation failed"
fi

echo ""

# Example 3: Data Analytics Platform
echo "📝 Example 3: Data Analytics Platform"
echo "-----------------------------------"
echo "Requirements: 'Data analytics with machine learning and real-time processing'"

analytics_response=$(curl -s -X POST "${SERVER_URL}/generate-intelligent-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Build a comprehensive data analytics platform with data ingestion from multiple sources, real-time stream processing, machine learning capabilities, data lake storage, and interactive dashboards with enterprise security and monitoring"
  }' --max-time 30)

if echo "$analytics_response" | grep -q '"success":true'; then
    echo "   ✅ Data analytics platform diagram generated successfully"
    compliance_score=$(echo "$analytics_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('enterprise_compliance_score', 0))")
    echo "   📊 Compliance Score: $compliance_score/100"
    
    # Show intelligent features
    echo "   🧠 Intelligent Features Active:"
    features=$(echo "$analytics_response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
features = data.get('intelligent_features', {})
for feature, active in features.items():
    status = '✅' if active else '❌'
    print(f'      {status} {feature.replace(\"_\", \" \").title()}')
" 2>/dev/null)
    echo "$features"
else
    echo "   ❌ Data analytics platform diagram generation failed"
fi

echo ""

# Example 4: Enhancement Demo
echo "📝 Example 4: Diagram Enhancement"
echo "-------------------------------"
echo "Requirements: Enhance existing diagram with monitoring and backup"

# First generate a simple diagram
base_response=$(curl -s -X POST "${SERVER_URL}/generate-intelligent-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Simple web application with database"
  }' --max-time 20)

if echo "$base_response" | grep -q '"success":true'; then
    echo "   ✅ Base diagram generated"
    
    # Extract the generated code
    base_code=$(echo "$base_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('generated_code', ''))" 2>/dev/null)
    
    if [ -n "$base_code" ]; then
        # Now enhance it
        enhancement_response=$(curl -s -X POST "${SERVER_URL}/enhance-diagram" \
          -H "Content-Type: application/json" \
          -d "{
            \"existing_code\": $(echo "$base_code" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read()))" 2>/dev/null),
            \"enhancement_requirements\": \"Add comprehensive monitoring, backup and disaster recovery capabilities, and enhanced security with firewall\"
          }" --max-time 20)
        
        if echo "$enhancement_response" | grep -q '"success":true'; then
            echo "   ✅ Diagram enhanced successfully"
            compliance_score=$(echo "$enhancement_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('enterprise_compliance_score', 0))" 2>/dev/null)
            echo "   📊 Enhanced Compliance Score: $compliance_score/100"
        else
            echo "   ❌ Diagram enhancement failed"
        fi
    else
        echo "   ❌ Could not extract base code for enhancement"
    fi
else
    echo "   ❌ Base diagram generation failed"
fi

echo ""

# Summary
echo "📋 Summary"
echo "--------"
echo "✨ Intelligent Architecture Diagram Generator Features Demonstrated:"
echo "   🧠 Natural Language Processing - Convert text to structured requirements"
echo "   🎨 Professional Diagram Generation - Azure icons and enterprise styling"
echo "   ✅ Enterprise Review Agent - Compliance scoring and recommendations"
echo "   🔧 Diagram Enhancement - Iterative improvement of existing diagrams"
echo "   📊 Intelligent Service Detection - Automatic Azure service selection"

echo ""
echo "🚀 Next Steps:"
echo "   • Try the web interface at http://localhost:5173 (if frontend is running)"
echo "   • Explore API documentation at http://127.0.0.1:8001/docs"
echo "   • Read full documentation in INTELLIGENT_DIAGRAM_GENERATOR.md"
echo "   • Set OPENAI_API_KEY environment variable for enhanced AI capabilities"

echo ""
echo "🎯 Example completed successfully!"