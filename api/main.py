"""FastAPI application for CinemaRAG."""

import os
import uuid
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import init_db, get_db
from models import Source, Chunk
from chunking import chunk_text
from openai_service import OpenAIService, get_openai_service
from qdrant_service import QdrantService, get_qdrant_service
from file_utils import extract_text_from_file


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


# Request/Response models
class IngestRequest(BaseModel):
    """Request model for ingesting a document."""
    kind: str  # script, review, interview, lecture, notes, subtitle
    title: str
    film: Optional[str] = None
    author: Optional[str] = None
    uri: Optional[str] = None
    text: str


class QueryRequest(BaseModel):
    """Request model for querying documents."""
    query: str
    film: Optional[str] = None
    kind: Optional[str] = None
    top_k: Optional[int] = 10


class ChunkResult(BaseModel):
    """Result model for a single chunk."""
    score: float
    text: str
    source_id: int
    chunk_index: int
    kind: str
    title: str
    film: Optional[str] = None
    author: Optional[str] = None
    uri: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for query results."""
    results: List[ChunkResult]


class IngestResponse(BaseModel):
    """Response model for ingest."""
    source_id: int
    chunks_created: int
    message: str


# Create FastAPI app
app = FastAPI(
    title="CinemaRAG",
    description="Local-first RAG system for filmmaking and storytelling",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "CinemaRAG",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(
    request: IngestRequest,
    db: Session = Depends(get_db)
):
    """
    Ingest a document into the system.
    
    Steps:
    1. Create Source record in Postgres
    2. Chunk the text intelligently
    3. Generate embeddings for chunks
    4. Store chunks in Postgres and Qdrant
    """
    # Validate kind
    valid_kinds = ["script", "review", "interview", "lecture", "notes", "subtitle"]
    if request.kind not in valid_kinds:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid kind. Must be one of: {', '.join(valid_kinds)}"
        )
    
    # Check for OpenAI API key
    try:
        openai_service = get_openai_service()
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e) + ". Please set OPENAI_API_KEY environment variable."
        )
    
    # Create source record
    source = Source(
        kind=request.kind,
        title=request.title,
        film=request.film,
        author=request.author,
        uri=request.uri
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    
    try:
        # Chunk the text
        chunks = chunk_text(request.text, request.kind)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks generated from text"
            )
        
        # Generate embeddings
        embeddings = openai_service.get_embeddings(chunks)
        
        # Prepare data for Qdrant and Postgres
        chunk_ids = []
        chunk_records = []
        payloads = []
        
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            chunk_ids.append(chunk_id)
            
            # Create Chunk record
            chunk_record = Chunk(
                source_id=source.id,
                chunk_index=idx,
                text=chunk_text,
                qdrant_id=chunk_id
            )
            chunk_records.append(chunk_record)
            
            # Prepare payload for Qdrant
            payload = {
                "text": chunk_text,
                "source_id": source.id,
                "chunk_index": idx,
                "kind": request.kind,
                "title": request.title,
                "film": request.film,
                "author": request.author,
                "uri": request.uri
            }
            payloads.append(payload)
        
        # Store chunks in Postgres
        db.add_all(chunk_records)
        db.commit()
        
        # Store embeddings in Qdrant
        qdrant_service = get_qdrant_service()
        qdrant_service.upsert_chunks(embeddings, chunk_ids, payloads)
        
        return IngestResponse(
            source_id=source.id,
            chunks_created=len(chunks),
            message=f"Successfully ingested {len(chunks)} chunks"
        )
    
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error during ingestion: {str(e)}"
        )


@app.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query the system for relevant chunks.
    
    Steps:
    1. Generate embedding for query
    2. Search Qdrant for similar chunks
    3. Return results with metadata
    """
    # Check for OpenAI API key
    try:
        openai_service = get_openai_service()
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e) + ". Please set OPENAI_API_KEY environment variable."
        )
    
    try:
        # Generate query embedding
        query_embedding = openai_service.get_embedding(request.query)
        
        # Search Qdrant
        qdrant_service = get_qdrant_service()
        results = qdrant_service.search(
            query_vector=query_embedding,
            limit=request.top_k or 10,
            film=request.film,
            kind=request.kind
        )
        
        # Format results
        chunk_results = [
            ChunkResult(
                score=result["score"],
                text=result["text"],
                source_id=result["source_id"],
                chunk_index=result["chunk_index"],
                kind=result["kind"],
                title=result["title"],
                film=result["film"],
                author=result["author"],
                uri=result["uri"]
            )
            for result in results
        ]
        
        return QueryResponse(results=chunk_results)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during query: {str(e)}"
        )


@app.post("/upload", response_model=IngestResponse)
async def upload_file(
    file: UploadFile = File(...),
    kind: str = Form(...),
    title: str = Form(...),
    film: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    uri: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and ingest a file into the system.

    Supported file formats: .pdf, .docx, .txt, .srt
    """
    # Validate kind
    valid_kinds = ["script", "review", "interview", "lecture", "notes", "subtitle"]
    if kind not in valid_kinds:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid kind. Must be one of: {', '.join(valid_kinds)}"
        )

    # Check for OpenAI API key
    try:
        openai_service = get_openai_service()
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e) + ". Please set OPENAI_API_KEY environment variable."
        )

    # Extract text from file
    try:
        content = await file.read()
        text = extract_text_from_file(content, file.filename)

        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the file"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading file: {str(e)}"
        )

    # Create source record
    source = Source(
        kind=kind,
        title=title,
        film=film,
        author=author,
        uri=uri or file.filename
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    try:
        # Chunk the text
        chunks = chunk_text(text, kind)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks generated from text"
            )

        # Generate embeddings
        embeddings = openai_service.get_embeddings(chunks)

        # Prepare data for Qdrant and Postgres
        chunk_ids = []
        chunk_records = []
        payloads = []

        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            chunk_ids.append(chunk_id)

            # Create Chunk record
            chunk_record = Chunk(
                source_id=source.id,
                chunk_index=idx,
                text=chunk_text,
                qdrant_id=chunk_id
            )
            chunk_records.append(chunk_record)

            # Prepare payload for Qdrant
            payload = {
                "text": chunk_text,
                "source_id": source.id,
                "chunk_index": idx,
                "kind": kind,
                "title": title,
                "film": film,
                "author": author,
                "uri": uri or file.filename
            }
            payloads.append(payload)

        # Store chunks in Postgres
        db.add_all(chunk_records)
        db.commit()

        # Store embeddings in Qdrant
        qdrant_service = get_qdrant_service()
        qdrant_service.upsert_chunks(embeddings, chunk_ids, payloads)

        return IngestResponse(
            source_id=source.id,
            chunks_created=len(chunks),
            message=f"Successfully ingested {len(chunks)} chunks from {file.filename}"
        )

    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error during ingestion: {str(e)}"
        )


@app.get("/settings/api-key")
async def get_api_key_status():
    """Check if OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    return {
        "configured": bool(api_key),
        "key_preview": f"{api_key[:7]}..." if api_key else None
    }


@app.post("/settings/api-key")
async def set_api_key(api_key: str = Form(...)):
    """
    Set OpenAI API key.

    Note: This updates the environment variable for the current process only.
    To persist across restarts, update the .env file.
    """
    if not api_key or not api_key.startswith("sk-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid API key format. Must start with 'sk-'"
        )

    os.environ["OPENAI_API_KEY"] = api_key

    return {
        "success": True,
        "message": "API key updated successfully",
        "key_preview": f"{api_key[:7]}..."
    }


# Mount static files (web UI)
# The static directory will be created next to main.py
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/app")
async def serve_app():
    """Serve the main web UI."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_dir, "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(
            status_code=404,
            detail="Web UI not found. Please ensure static files are present."
        )
