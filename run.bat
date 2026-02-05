@echo off
REM GeminiCRM Pro - Windows Startup Script

echo 🚀 Starting GeminiCRM Pro...

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo 📝 Please update .env with your Gemini API key
    pause
)

REM Check if requirements are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Start the Flask app
echo ✅ Starting Flask server on http://localhost:5000
python app.py

pause
