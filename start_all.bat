@echo off
echo ========================================
echo DocuMind AI - System Launcher
echo ========================================
echo.
echo Launching File Watcher and Web App in separate windows...

start "DocuMind Redis" cmd /k "call start_redis.bat"
start "DocuMind Watcher" cmd /k "call start_watcher.bat"
start "DocuMind Web App + Ngrok" cmd /k "python deploy_to_internet.py"
start "DocuMind Worker" cmd /k "call start_worker.bat"
start "Ollama Service" cmd /k "ollama serve"

echo.
echo System components started! 
echo You can minimize this window.
echo.
pause
