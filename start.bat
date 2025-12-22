@echo off
REM CinemaRAG Startup Script
REM One-click startup for Windows

echo.
echo 🎬 Starting CinemaRAG...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check for .env file
if not exist .env (
    echo ⚙️  First-time setup detected!
    echo.
    echo CinemaRAG requires an OpenAI API key to generate embeddings.
    echo Get your API key from: https://platform.openai.com/api-keys
    echo.
    set /p api_key="Enter your OpenAI API key (sk-...): "

    echo !api_key! | findstr /r "^sk-" >nul
    if errorlevel 1 (
        echo ❌ Invalid API key format. Key should start with 'sk-'
        pause
        exit /b 1
    )

    echo OPENAI_API_KEY=!api_key! > .env
    echo ✅ API key saved to .env file
    echo.
)

REM Start Docker Compose
echo 🚀 Starting services...
docker compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Check if API is responding
set max_attempts=30
set attempt=0

:check_health
curl -s http://localhost:8000/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ CinemaRAG is ready!
    goto ready
)

set /a attempt+=1
if %attempt% geq %max_attempts% (
    echo ❌ Services failed to start. Check logs with: docker compose logs
    pause
    exit /b 1
)

timeout /t 1 /nobreak >nul
goto check_health

:ready
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   🎬 CinemaRAG is running!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   Web UI:  http://localhost:8000/app
echo   API:     http://localhost:8000/docs
echo.
echo   Close this window or press Ctrl+C to stop all services
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Open browser
start http://localhost:8000/app

REM Show logs
docker compose logs -f
