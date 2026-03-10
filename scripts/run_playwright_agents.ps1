#!/usr/bin/env pwsh
# Playwright Agents UI Launcher
# Starts the Streamlit dashboard for Planner, Generator, and Healer agents

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎭 PLAYWRIGHT AGENTS DASHBOARD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Streamlit UI..." -ForegroundColor Yellow
Write-Host ""

# Navigate to the framework directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$frameworkDir = Join-Path $scriptDir "framework"

# Check if streamlit is installed
try {
    $streamlitCheck = Get-Command streamlit -ErrorAction Stop
    Write-Host "✓ Streamlit found" -ForegroundColor Green
} catch {
    Write-Host "✗ Streamlit not found. Installing..." -ForegroundColor Red
    pip install streamlit
}

# Run the UI
Write-Host ""
Write-Host "🚀 Launching dashboard..." -ForegroundColor Cyan
Write-Host "   URL: http://localhost:8501" -ForegroundColor Gray
Write-Host ""

Set-Location $PSScriptRoot
streamlit run framework/playwright_agents_ui.py --server.port 8501 --server.headless true
