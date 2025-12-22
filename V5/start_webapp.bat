--ver@echo off
echo ========================================
echo Universal RAG System - Web App
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Flask Web Application...
echo Access at: http://localhost:5000
echo.

python app.py

pause
