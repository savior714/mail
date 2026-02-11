
@echo off
echo Starting Mail Archivist (React + FastAPI)...

:: Start Backend
start "Mail Backend" cmd /k "uvicorn src.api.main:app --port 8000 --reload"

:: Start Frontend
cd frontend
start "Mail Frontend" cmd /k "npm run dev"

echo.
echo Application started!
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000/docs
echo.
echo Press any key to exit this launcher (servers will keep running)...
pause >nul
