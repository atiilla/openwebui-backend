@echo off
setlocal enabledelayedexpansion

REM Check if Docker is running
docker info > nul 2>&1
if !errorlevel! neq 0 (
    echo Docker is not running. Please start Docker and try again.
    exit /b
)

REM Build and start the containers
echo Building and starting Open WebUI Backend...
docker-compose up -d --build

echo.
echo Open WebUI Backend is now running!
echo Backend API available at: http://localhost:8080
echo.
echo To stop the backend: docker-compose down
echo To view logs: docker-compose logs -f

endlocal 