# CinemaRAG

A production-quality, local-first RAG (Retrieval-Augmented Generation) system for filmmaking and storytelling. Think NotebookLM for screenwriters, critics, and film students.

## Features

- **Beautiful Web UI**: Simple, intuitive interface - no command-line required
- **Drag & Drop Upload**: Upload scripts, reviews, interviews, and more
- **Intelligent Text Chunking**: Screenplay-aware text segmentation
- **Semantic Search**: Find relevant content across all your documents
- **Multiple Document Types**: Support for scripts, reviews, interviews, lectures, notes, and subtitles
- **File Format Support**: PDF, DOCX, TXT, SRT
- **Citation Support**: Full metadata tracking for proper attribution
- **Local-First**: Runs entirely on your machine (with API-based embeddings)

## Requirements

- Docker Desktop ([Download here](https://www.docker.com/products/docker-desktop))
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- 8GB+ RAM recommended

## Quick Start (One-Click!)

### Mac / Linux

1. Double-click `start.sh` or run in terminal:
   ```bash
   ./start.sh
   ```

2. On first run, you'll be prompted to enter your OpenAI API key

3. Your browser will automatically open to `http://localhost:8000/app`

### Windows

1. Double-click `start.bat`

2. On first run, you'll be prompted to enter your OpenAI API key

3. Your browser will automatically open to `http://localhost:8000/app`

That's it! The web interface will guide you through uploading and searching documents.

## Using CinemaRAG

### Upload Documents

1. Click the **Upload** tab
2. Drag & drop a file or click to select (PDF, DOCX, TXT, SRT)
3. Choose document type (script, review, interview, etc.)
4. Add title, film name, and author (optional)
5. Click **Upload & Process**

### Search Your Library

1. Click the **Search** tab
2. Enter your question or search query
3. Optionally filter by film or document type
4. View results with relevance scores and citations

### Configure API Key

- Click the ⚙️ Settings button
- Enter your OpenAI API key
- The key is stored in `.env` for future sessions

## Architecture

- **Frontend**: Vanilla JavaScript (no framework bloat!)
- **Backend**: FastAPI
- **Vector Store**: Qdrant
- **Database**: PostgreSQL
- **Embeddings**: OpenAI text-embedding-ada-002
- **Deployment**: Docker Compose

## Stopping the System

Press `Ctrl+C` in the terminal window, or run:

```bash
# Mac/Linux
docker compose down

# Windows
docker-compose down
```

## Advanced: API Access

The system also provides a REST API for programmatic access.

- **Interactive API Docs**: http://localhost:8000/docs
- **Web UI**: http://localhost:8000/app
- **Health Check**: http://localhost:8000/health

### API Endpoints

**Upload File**: `POST /upload`
- Upload PDF, DOCX, TXT, or SRT files

**Search Text**: `POST /ingest`
- Ingest text directly (JSON)

**Query**: `POST /query`
- Semantic search across documents

See full API documentation at http://localhost:8000/docs when running.

## Project Structure

```
.
├── start.sh                 # 🚀 One-click startup (Mac/Linux)
├── start.bat                # 🚀 One-click startup (Windows)
├── docker-compose.yml       # Service orchestration
├── api/
│   ├── static/              # Web UI files
│   │   ├── index.html       # Main UI
│   │   ├── style.css        # Styling
│   │   └── app.js           # JavaScript
│   ├── main.py              # FastAPI application & endpoints
│   ├── models.py            # Database models
│   ├── chunking.py          # Intelligent text chunking
│   ├── file_utils.py        # File processing (PDF, DOCX, etc.)
│   ├── openai_service.py    # OpenAI embeddings integration
│   ├── qdrant_service.py    # Vector database client
│   └── requirements.txt     # Python dependencies
└── scripts/
    ├── smoke_test.sh        # End-to-end test
    └── validate_system.sh   # System validation
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

## How It Works

### Intelligent Chunking

- **Screenplays**: Preserves scene boundaries and dialogue structure
- **General Text**: Paragraph-aware segmentation
- **Overlap**: 100-character overlap between chunks for context continuity

### Citation & Metadata

Every search result includes:
- Source document (title, film, author)
- Document type (script, review, etc.)
- Relevance score (0-100%)
- Original text for direct quotation

### Privacy & Data

- All data stored locally on your machine
- Only embeddings sent to OpenAI API
- No cloud storage or external databases
- You control your data

## Future Enhancements

- Advanced screenplay parsing (character arcs, scene detection)
- Multi-modal support (images, audio transcripts)
- Custom embedding models (local alternatives to OpenAI)
- Local LLM support for query generation
- Bulk import tools
- Export/backup functionality

## License

See LICENSE file for details.
