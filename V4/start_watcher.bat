@echo off
echo ========================================
echo Universal RAG System - Quick Start
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting File Watcher...
echo Drop files into data\incoming\ to process them
echo.

python watcher.py

pause
