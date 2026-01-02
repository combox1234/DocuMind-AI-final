@echo off
echo ========================================
echo DocuMind AI - Redis Server (Memurai)
echo ========================================
echo.

tasklist /FI "IMAGENAME eq memurai.exe" 2>NUL | find /I /N "memurai.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Memurai is already running. Skipping startup.
    timeout /t 5
    exit
)

echo Starting Memurai...
"C:\Program Files\Memurai\memurai.exe"
pause
