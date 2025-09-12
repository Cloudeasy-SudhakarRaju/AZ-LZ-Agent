#!/bin/bash

echo "🚀 Azure Landing Zone Agent - Full Stack Startup"
echo "================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "🎯 Starting services..."
echo "Backend will be available at: http://127.0.0.1:8001"
echo "Frontend will be available at: http://localhost:5173"
echo ""
echo "💡 Open your browser to http://localhost:5173 to use the application"
echo ""
echo "🛑 Press Ctrl+C to stop both services"
echo ""

# Start backend in background
cd backend
uvicorn main:app --host 127.0.0.1 --port 8001 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Wait for either process to exit
wait