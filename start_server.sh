#!/bin/bash

# Azure LZ Agent Server Startup Script
# This script ensures all dependencies are installed and starts the backend server

set -e

echo "🚀 Starting Azure LZ Agent Server..."
echo "============================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Navigate to project directory
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)
echo "📁 Project directory: $PROJECT_DIR"

# Install system dependencies
echo "📦 Installing system dependencies..."
if ! command -v dot &> /dev/null; then
    echo "Installing Graphviz..."
    sudo apt-get update -qq
    sudo apt-get install -y graphviz
else
    echo "✅ Graphviz already installed"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Create output directory if it doesn't exist
mkdir -p /tmp/azure_diagrams

# Test server health
echo "🩺 Testing server health..."
cd backend

# Check if server is already running
if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
    echo "⚠️  Server already running on port 8001"
    echo "Stopping existing server..."
    pkill -f "uvicorn main:app" || true
    sleep 2
fi

# Start the server
echo "🚀 Starting backend server..."
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Start server in background
nohup uvicorn main:app --host 0.0.0.0 --port 8001 > ../server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
        echo "✅ Server started successfully!"
        echo "🌐 Server running at: http://127.0.0.1:8001"
        echo "📚 API Documentation: http://127.0.0.1:8001/docs"
        echo "🆔 Server PID: $SERVER_PID"
        
        # Test basic functionality
        echo "🧪 Testing basic functionality..."
        HEALTH_STATUS=$(curl -s http://127.0.0.1:8001/health | jq -r '.status')
        if [ "$HEALTH_STATUS" = "healthy" ]; then
            echo "✅ Health check passed: $HEALTH_STATUS"
        else
            echo "❌ Health check failed: $HEALTH_STATUS"
        fi
        
        echo ""
        echo "🎉 Azure LZ Agent is ready!"
        echo "You can now run tests and demos:"
        echo "  python final_solution_demo.py"
        echo "  python test_fixes_comprehensive.py"
        echo ""
        exit 0
    fi
    echo "   Attempt $i/30: Server not ready yet..."
    sleep 1
done

echo "❌ Server failed to start within 30 seconds"
echo "📋 Server log:"
cat ../server.log || echo "No log file found"
exit 1