@echo off
echo Starting PhysicsAI...

:: Start backend
start "PhysicsAI Backend" cmd /k "cd /d D:\Phyai\backend && python -m uvicorn main:app --reload --port 8000"

:: Wait a moment then start frontend
timeout /t 2 /nobreak >nul
start "PhysicsAI Frontend" cmd /k "cd /d D:\Phyai\frontend && npm run dev"

echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
