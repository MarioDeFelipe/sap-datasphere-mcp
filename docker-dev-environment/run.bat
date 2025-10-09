@echo off
REM SAP Datasphere Control Panel - Docker Development Runner (Windows)

echo 🐳 SAP Datasphere Control Panel - Docker Development Environment
echo ================================================================

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not in PATH
    echo.
    echo Please install Docker Desktop for Windows:
    echo https://docs.docker.com/desktop/install/windows-install/
    echo.
    echo After installation, restart your terminal and try again.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not available
    echo Docker Compose should be included with Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker is available
echo ✅ Docker Compose is available
echo.

REM Parse command line arguments
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=start

if "%COMMAND%"=="start" goto start
if "%COMMAND%"=="stop" goto stop
if "%COMMAND%"=="restart" goto restart
if "%COMMAND%"=="logs" goto logs
if "%COMMAND%"=="shell" goto shell
if "%COMMAND%"=="clean" goto clean
if "%COMMAND%"=="build" goto build
if "%COMMAND%"=="status" goto status
if "%COMMAND%"=="help" goto help

echo ❌ Unknown command: %COMMAND%
goto help

:start
echo 🚀 Starting SAP Datasphere development environment...
docker-compose up -d --build
echo.
echo ✅ Environment started successfully!
echo.
echo 🌐 Access your application:
echo    Web Interface: http://localhost:8000
echo    API Endpoint:  http://localhost:8000/api/hello
echo    Health Check:  http://localhost:8000/health
echo.
echo 📊 View logs: run.bat logs
echo 🐚 Access shell: run.bat shell
goto end

:stop
echo 🛑 Stopping SAP Datasphere development environment...
docker-compose down
echo ✅ Environment stopped successfully!
goto end

:restart
echo 🔄 Restarting SAP Datasphere development environment...
docker-compose down
docker-compose up -d --build
echo ✅ Environment restarted successfully!
goto end

:logs
echo 📋 Showing application logs (Press Ctrl+C to exit)...
docker-compose logs -f sap-datasphere-app
goto end

:shell
echo 🐚 Accessing application container shell...
docker-compose exec sap-datasphere-app bash
goto end

:clean
echo 🧹 Cleaning up all containers and volumes...
docker-compose down -v
docker system prune -f
echo ✅ Cleanup completed!
goto end

:build
echo 🔨 Rebuilding containers...
docker-compose build --no-cache
echo ✅ Build completed!
goto end

:status
echo 📊 Container Status:
docker-compose ps
echo.
echo 🔍 Docker System Info:
docker system df
goto end

:help
echo Usage: run.bat [COMMAND]
echo.
echo Commands:
echo   start     Start the development environment
echo   stop      Stop the development environment
echo   restart   Restart the development environment
echo   logs      Show application logs
echo   shell     Access the application container shell
echo   clean     Stop and remove all containers and volumes
echo   build     Rebuild the containers
echo   status    Show container status
echo   help      Show this help message
echo.
goto end

:end
pause