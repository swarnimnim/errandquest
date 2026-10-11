# ErrandQuest One-Click Development Launcher
Write-Host "==============================================" -ForegroundColor Green
Write-Host "   Starting ErrandQuest Development Server   " -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start FastAPI Backend on port 8000
Write-Host "`n[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory "$projectRoot\backend" -PassThru

# 2. Start Vite Frontend on port 5173
Write-Host "[2/2] Starting Vite Frontend on http://localhost:5173..." -ForegroundColor Cyan
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "$projectRoot\frontend" -PassThru

Write-Host "`nErrandQuest is running!" -ForegroundColor Green
Write-Host "-> Open your browser at: http://localhost:5173" -ForegroundColor Yellow
Write-Host "-> Backend API Docs at:  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C or close this terminal to stop both servers." -ForegroundColor Gray

try {
    # Keep script open and wait
    Wait-Process -Id $frontendProcess.Id, $backendProcess.Id
} finally {
    Write-Host "Stopping servers..." -ForegroundColor Red
    Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue
}
