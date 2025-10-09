@echo off
echo 🚀 Starting Ailien Platform Control Panel - DEV Environment
echo.
cd /d "%~dp0"
python dev_server.py --env dev
pause