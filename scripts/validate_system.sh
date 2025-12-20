#!/bin/bash

# Quick validation script to ensure the system is properly configured
# This script validates the system WITHOUT requiring an OpenAI API key

set -e

echo "=========================================="
echo "CinemaRAG System Validation"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "1. Checking if Docker Compose is running..."
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Docker Compose services are running${NC}"
else
    echo -e "${RED}✗ Docker Compose services are not running${NC}"
    echo "Please run: docker compose up --build"
    exit 1
fi

echo ""
echo "2. Checking API health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API is not responding properly${NC}"
    exit 1
fi

echo ""
echo "3. Checking root endpoint..."
ROOT_RESPONSE=$(curl -s http://localhost:8000/)
if echo "$ROOT_RESPONSE" | grep -q "CinemaRAG"; then
    echo -e "${GREEN}✓ Root endpoint returns correct information${NC}"
    echo "   $(echo $ROOT_RESPONSE | jq -c .)"
else
    echo -e "${RED}✗ Root endpoint not working${NC}"
    exit 1
fi

echo ""
echo "4. Testing error handling (without API key)..."
ERROR_RESPONSE=$(curl -s -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"kind":"script","title":"Test","text":"Test content"}')
  
if echo "$ERROR_RESPONSE" | grep -q "OPENAI_API_KEY"; then
    echo -e "${GREEN}✓ API correctly handles missing API key${NC}"
else
    echo -e "${RED}✗ API did not return expected error${NC}"
    exit 1
fi

echo ""
echo "5. Checking Qdrant health..."
QDRANT_RESPONSE=$(curl -s http://localhost:6333/readyz)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Qdrant is responding${NC}"
else
    echo -e "${YELLOW}⚠ Qdrant health check returned non-zero (may be normal)${NC}"
fi

echo ""
echo "6. Checking PostgreSQL..."
if docker compose exec -T postgres pg_isready -U cinema > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not ready${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "System Validation Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}All core components are working correctly!${NC}"
echo ""
echo "To test with actual data ingestion and queries:"
echo "  1. Set your OpenAI API key: export OPENAI_API_KEY=sk-..."
echo "  2. Restart services: docker compose down && docker compose up -d"
echo "  3. Run: ./scripts/smoke_test.sh"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
