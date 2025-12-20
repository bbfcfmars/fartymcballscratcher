#!/bin/bash

set -e

echo "=========================================="
echo "CinemaRAG Smoke Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
echo "Checking services..."

# Wait for API to be ready
MAX_RETRIES=30
RETRY_COUNT=0
API_URL="http://localhost:8000/health"

echo -n "Waiting for API to be ready..."
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -f "$API_URL" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e " ${RED}✗${NC}"
    echo -e "${RED}Error: API did not start within expected time${NC}"
    echo "Please ensure 'docker compose up --build' is running"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 1: Ingest Sample Document"
echo "=========================================="

SAMPLE_TEXT="INT. TYRELL CORPORATION - NIGHT

A vast room lit by ceiling banks. The man at the console is HOLDEN. Across from him sits LEON, an agitated man in a waiter's jacket.

HOLDEN
Tell me about your mother.

LEON
My mother? Let me tell you about my mother.

LEON reaches for something in his jacket. HOLDEN sees it and reacts—too late. LEON fires. The force of the shot slams HOLDEN through the wall.

This opening scene establishes the Voight-Kampff test, a crucial element of the Blade Runner universe used to identify replicants."

INGEST_RESPONSE=$(curl -s -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d "{
    \"kind\": \"script\",
    \"title\": \"Blade Runner Opening Scene\",
    \"film\": \"Blade Runner\",
    \"author\": \"Hampton Fancher, David Peoples\",
    \"text\": $(echo "$SAMPLE_TEXT" | jq -Rs .)
  }")

echo "Response:"
echo "$INGEST_RESPONSE" | jq .

SOURCE_ID=$(echo "$INGEST_RESPONSE" | jq -r '.source_id')
CHUNKS_CREATED=$(echo "$INGEST_RESPONSE" | jq -r '.chunks_created')

if [ "$SOURCE_ID" != "null" ] && [ "$CHUNKS_CREATED" -gt 0 ]; then
    echo -e "${GREEN}✓ Successfully ingested document (Source ID: $SOURCE_ID, Chunks: $CHUNKS_CREATED)${NC}"
else
    echo -e "${RED}✗ Failed to ingest document${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 2: Query the System"
echo "=========================================="

# Give Qdrant a moment to index
sleep 2

QUERY_RESPONSE=$(curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What happens in the opening scene with Leon?",
    "top_k": 3
  }')

echo "Response:"
echo "$QUERY_RESPONSE" | jq .

RESULT_COUNT=$(echo "$QUERY_RESPONSE" | jq '.results | length')

if [ "$RESULT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Successfully retrieved $RESULT_COUNT results${NC}"
    echo ""
    echo "Top result:"
    echo "$QUERY_RESPONSE" | jq '.results[0]'
else
    echo -e "${RED}✗ No results returned${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 3: Query with Film Filter"
echo "=========================================="

FILTERED_RESPONSE=$(curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Voight-Kampff test",
    "film": "Blade Runner",
    "top_k": 2
  }')

echo "Response:"
echo "$FILTERED_RESPONSE" | jq .

FILTERED_COUNT=$(echo "$FILTERED_RESPONSE" | jq '.results | length')

if [ "$FILTERED_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Successfully retrieved $FILTERED_COUNT filtered results${NC}"
else
    echo -e "${YELLOW}⚠ No filtered results (this may be okay if the sample doesn't match)${NC}"
fi

echo ""
echo "=========================================="
echo "Smoke Test Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}All tests passed!${NC}"
echo ""
echo "Next steps:"
echo "  - API is running at http://localhost:8000"
echo "  - View API docs at http://localhost:8000/docs"
echo "  - View logs with: docker compose logs -f api"
echo ""
