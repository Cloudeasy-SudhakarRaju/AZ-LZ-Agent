#!/bin/bash

echo "🚀 Starting Azure Landing Zone Agent Backend..."
echo "Installing dependencies..."
cd backend
pip install -r requirements.txt

echo "🌐 Starting FastAPI server on http://127.0.0.1:8001"
uvicorn main:app --host 127.0.0.1 --port 8001 --reload