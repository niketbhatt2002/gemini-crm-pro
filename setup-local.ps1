#!/usr/bin/env pwsh
<#
.SYNOPSIS
GeminiCRM Pro - Quick Setup Script for Windows PowerShell

.DESCRIPTION
This script sets up and starts GeminiCRM Pro locally on your machine.
It handles dependency installation and application startup.

.EXAMPLE
.\setup-local.ps1
#>

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  GeminiCRM Pro - Local Setup" -ForegroundColor Green
Write-Host "  Enterprise CRM with Material Design 3" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking for Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[✗] ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[✓] Python found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check if pip is available
Write-Host "Checking for pip installation..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[✗] ERROR: pip is not installed" -ForegroundColor Red
    Write-Host "Please install Python with pip included" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[✓] pip found: $pipVersion" -ForegroundColor Green
Write-Host ""

# Navigate to project directory
Write-Host "Navigating to project directory..." -ForegroundColor Yellow
$projectPath = "c:\Users\Niket Bhatt\Documents\gemini-crm-pro"

if (-not (Test-Path $projectPath)) {
    Write-Host "[✗] ERROR: Could not find project directory" -ForegroundColor Red
    Write-Host "Expected path: $projectPath" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location $projectPath
Write-Host "[✓] In project directory" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "[✗] ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host "Try running: pip install --upgrade pip" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[✓] Dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
# GeminiCRM Pro Configuration
# Get your free API key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=
SECRET_KEY=your-secret-key-here
"@ | Out-File -Encoding utf8 ".env"
    Write-Host "[✓] .env file created (you can add API key later)" -ForegroundColor Green
    Write-Host ""
}

# Start the application
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Starting GeminiCRM Pro..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will start in a moment..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Access it at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press CTRL+C in this window to stop the server" -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 2

python app.py

Read-Host "Press Enter to exit"
