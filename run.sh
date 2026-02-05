#!/bin/bash
# GeminiCRM Pro - Startup Script

echo "🚀 Starting GeminiCRM Pro..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please update .env with your Gemini API key"
fi

# Check if requirements are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the Flask app
echo "✅ Starting Flask server on http://localhost:5000"
python app.py
