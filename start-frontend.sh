#!/bin/bash

echo "🎨 Starting Azure Landing Zone Agent Frontend..."
echo "Installing dependencies..."
cd frontend
npm install

echo "🌐 Starting React dev server on http://localhost:5173"
npm run dev