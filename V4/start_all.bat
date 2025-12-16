@echo off
echo ========================================
echo DocuMind AI - System Launcher
echo ========================================
echo.
echo Launching File Watcher and Web App in separate windows...

start "DocuMind Watcher" cmd /k "call start_watcher.bat"
start "DocuMind Web App" cmd /k "call start_webapp.bat"

echo.
echo System components started! 
echo You can minimize this window.
echo.
pause
