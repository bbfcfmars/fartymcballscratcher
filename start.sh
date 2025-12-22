#!/bin/bash

# CinemaRAG Startup Script
# One-click startup for Mac/Linux

set -e

echo "🎬 Starting CinemaRAG..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚙️  First-time setup detected!"
    echo ""
    echo "CinemaRAG requires an OpenAI API key to generate embeddings."
    echo "Get your API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Enter your OpenAI API key (sk-...): " api_key

    if [[ ! $api_key =~ ^sk- ]]; then
        echo "❌ Invalid API key format. Key should start with 'sk-'"
        exit 1
    fi

    echo "OPENAI_API_KEY=$api_key" > .env
    echo "✅ API key saved to .env file"
    echo ""
fi

# Start Docker Compose
echo "🚀 Starting services..."
docker compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Check if API is responding
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ CinemaRAG is ready!"
        break
    fi

    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Services failed to start. Check logs with: docker compose logs"
        exit 1
    fi

    sleep 1
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎬 CinemaRAG is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Web UI:  http://localhost:8000/app"
echo "  API:     http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Open browser (try multiple commands for different systems)
if command -v open > /dev/null 2>&1; then
    # macOS
    open http://localhost:8000/app
elif command -v xdg-open > /dev/null 2>&1; then
    # Linux
    xdg-open http://localhost:8000/app
elif command -v wslview > /dev/null 2>&1; then
    # WSL
    wslview http://localhost:8000/app
fi

# Keep script running and show logs
docker compose logs -f
