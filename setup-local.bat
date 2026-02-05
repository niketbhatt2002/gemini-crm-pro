@echo off
REM GeminiCRM Pro - Quick Setup Script for Windows
REM Run this to set up and start the application locally

echo.
echo ============================================
echo   GeminiCRM Pro - Local Setup
echo   Enterprise CRM with Material Design 3
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [✓] Python found
python --version

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed
    echo Please install Python with pip
    pause
    exit /b 1
)

echo [✓] pip found
echo.

REM Navigate to project directory
echo Navigating to project directory...
cd /d "c:\Users\Niket Bhatt\Documents\gemini-crm-pro"

if errorlevel 1 (
    echo [ERROR] Could not find project directory
    echo Please ensure the path is correct:
    echo c:\Users\Niket Bhatt\Documents\gemini-crm-pro
    pause
    exit /b 1
)

echo [✓] In project directory
echo.

REM Install dependencies
echo ============================================
echo Installing dependencies...
echo ============================================
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo Try running: pip install --upgrade pip
    pause
    exit /b 1
)

echo.
echo [✓] Dependencies installed successfully
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    (
        echo # GeminiCRM Pro Configuration
        echo # Get your free API key from: https://aistudio.google.com/app/apikey
        echo GEMINI_API_KEY=
        echo SECRET_KEY=your-secret-key-here
    ) > .env
    echo [✓] .env file created (you can add API key later)
    echo.
)

REM Start the application
echo ============================================
echo Starting GeminiCRM Pro...
echo ============================================
echo.
echo The application will open in your browser in a moment...
echo.
echo Access it at: http://localhost:5000
echo Press CTRL+C in this window to stop the server
echo.

timeout /t 2

python app.py

pause
