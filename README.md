# CinemaRAG

A production-quality, local-first RAG (Retrieval-Augmented Generation) system for filmmaking and storytelling. Think NotebookLM for screenwriters, critics, and film students.

## Features

- **Intelligent Text Chunking**: Paragraph-aware and screenplay-safe text segmentation
- **Vector Search**: Fast semantic search powered by Qdrant
- **Multiple Document Types**: Support for scripts, reviews, interviews, lectures, notes, and subtitles
- **Citation Support**: Full metadata tracking for proper attribution
- **API-First**: Clean REST API for easy integration
- **Local-First**: Runs entirely on your machine (with API-based embeddings)

## Architecture

- **Backend**: FastAPI
- **Vector Store**: Qdrant
- **Database**: PostgreSQL
- **Embeddings**: OpenAI text-embedding-ada-002
- **Deployment**: Docker Compose

## Requirements

- Docker Desktop for Mac (with Apple Silicon support)
- OpenAI API key
- 18GB+ RAM recommended

## Quick Start

### 1. Set Up Environment

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Important**: Never commit your `.env` file to git. It's already in `.gitignore`.

### 2. Start the System

```bash
docker compose up --build
```

This will:
- Start PostgreSQL database
- Start Qdrant vector store
- Build and start the FastAPI application
- Initialize database tables
- Create Qdrant collection

The API will be available at `http://localhost:8000`

### 3. Verify Installation

**Quick validation (without API key):**

```bash
./scripts/validate_system.sh
```

This validates that all services are running correctly.

**Full smoke test (requires API key):**

Run the smoke test:

```bash
./scripts/smoke_test.sh
```

This will:
- Check all services are running
- Ingest a sample document
- Query the system
- Display results

## API Usage

### Ingest a Document

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "script",
    "title": "Blade Runner Opening Scene",
    "film": "Blade Runner",
    "author": "Hampton Fancher, David Peoples",
    "text": "INT. TYRELL CORPORATION - NIGHT\n\nA vast room lit by ceiling banks... [full text]"
  }'
```

**Document Kinds:**
- `script` - Screenplays and scripts
- `review` - Film reviews and criticism
- `interview` - Interviews with filmmakers
- `lecture` - Educational content and lectures
- `notes` - General notes and commentary
- `subtitle` - Film subtitles

### Query Documents

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does the opening scene reveal about the world?",
    "top_k": 5
  }'
```

**Optional filters:**
- `film`: Filter by specific film name
- `kind`: Filter by document type
- `top_k`: Number of results (default: 10)

### Response Format

```json
{
  "results": [
    {
      "score": 0.89,
      "text": "INT. TYRELL CORPORATION - NIGHT...",
      "source_id": 1,
      "chunk_index": 0,
      "kind": "script",
      "title": "Blade Runner Opening Scene",
      "film": "Blade Runner",
      "author": "Hampton Fancher, David Peoples",
      "uri": null
    }
  ]
}
```

## Project Structure

```
.
├── api/
│   ├── Dockerfile           # API container definition
│   ├── pyproject.toml       # Python dependencies
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # Database connection
│   ├── chunking.py          # Text chunking logic
│   ├── openai_service.py    # OpenAI integration
│   └── qdrant_service.py    # Qdrant integration
├── scripts/
│   └── smoke_test.sh        # Smoke test script
├── docker-compose.yml       # Service orchestration
└── README.md                # This file
```

## Development

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f qdrant
docker compose logs -f postgres
```

### Access Database

```bash
docker compose exec postgres psql -U cinema -d cinemarag
```

### Stop Services

```bash
docker compose down
```

### Clean Up (Remove Data)

```bash
docker compose down -v
```

## Troubleshooting

### API Key Error

If you see "OPENAI_API_KEY environment variable is not set":
1. Ensure `.env` file exists in project root
2. Verify it contains: `OPENAI_API_KEY=sk-...`
3. Restart: `docker compose down && docker compose up --build`

### Port Conflicts

If ports 8000, 5432, or 6333 are in use:
1. Stop conflicting services
2. Or modify ports in `docker-compose.yml`

### Memory Issues

If Docker runs out of memory:
1. Increase Docker Desktop memory allocation to 8GB+
2. Close other applications

## Design Philosophy

### Chunking Strategy

- **Screenplays**: Preserves scene boundaries and dialogue structure
- **General Text**: Paragraph-aware with configurable overlap
- **Size**: ~1000 characters per chunk with 100-character overlap
- **Context**: Overlap ensures continuity for semantic search

### Citation Support

Every chunk includes:
- Source document metadata (title, film, author, URI)
- Chunk position within source
- Original text for direct quotation

### Error Handling

- Clear error messages when API key is missing
- Graceful degradation
- No silent failures
- All errors logged

## Future Enhancements

- Advanced screenplay parsing (character arcs, scene detection)
- Multi-modal support (images, audio transcripts)
- Custom embedding models
- Local LLM support
- Web UI
- Bulk import tools

## License

See LICENSE file for details.
