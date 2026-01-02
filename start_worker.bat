@echo off
echo ========================================
echo DocuMind AI - Background Worker
echo ========================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Celery Worker...
echo Logs will appear here.
echo.

celery -A worker.celery_app worker --loglevel=info -P eventlet
pause
