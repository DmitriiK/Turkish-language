#!/bin/bash

# Turkish Language Learning System - Setup and Development Server

set -e  # Exit on any error

echo "🇹🇷 Turkish Language Learning System"
echo "======================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.12+ first."
    echo "   Visit: https://python.org/"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys before generating examples"
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d node_modules ]; then
    npm install
else 
    echo "   Frontend dependencies already installed"
fi

# Go back to root
cd ..

# Setup Python virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d .venv ]; then
    python3 -m venv .venv
    echo "   Created virtual environment"
fi

# Activate virtual environment and install dependencies
source .venv/bin/activate
pip install -q -r requirements.txt
echo "   Python dependencies installed"

# Check if training data exists
if [ ! -d "data/output/training_examples_for_verbs" ] || [ -z "$(ls -A data/output/training_examples_for_verbs 2>/dev/null)" ]; then
    echo ""
    echo "📚 No training examples found. You can generate them with:"
    echo "   npm run generate-a1    # Generate A1 level examples (recommended for first run)"
    echo "   npm run generate-a2    # Generate A2 level examples"  
    echo "   npm run generate-examples --language-level A1 --top-n-verbs 5"
    echo ""
    echo "⚠️  Make sure to add your API key to .env file first!"
else
    echo "✅ Training examples found"
fi

echo ""
echo "🚀 Setup complete! Available commands:"
echo ""
echo "   npm start              # Start development server"
echo "   npm run dev            # Same as start"
echo "   npm run build          # Build for production"
echo "   npm run generate-a1    # Generate A1 training examples"
echo "   npm run generate-a2    # Generate A2 training examples"
echo ""

# Ask if user wants to start the dev server
read -p "🤔 Start the development server now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌟 Starting development server..."
    echo "   Frontend will be available at: http://localhost:3000"
    echo "   Press Ctrl+C to stop"
    echo ""
    cd frontend && npm run dev
else
    echo "👍 Ready to go! Run 'npm start' when you're ready to begin."
fi