"""Qdrant vector database integration."""

import os
import uuid
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue


class QdrantService:
    """Service for Qdrant vector database operations."""
    
    COLLECTION_NAME = "cinema_chunks"
    VECTOR_SIZE = 1536  # OpenAI ada-002 embedding size
    
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.client = QdrantClient(url=qdrant_url)
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
    
    def upsert_chunks(
        self,
        embeddings: List[List[float]],
        chunk_ids: List[str],
        payloads: List[Dict[str, Any]]
    ):
        """
        Upsert chunk embeddings with metadata.
        
        Args:
            embeddings: List of embedding vectors
            chunk_ids: List of unique chunk IDs
            payloads: List of metadata dictionaries
        """
        points = [
            PointStruct(
                id=chunk_id,
                vector=embedding,
                payload=payload
            )
            for chunk_id, embedding, payload in zip(chunk_ids, embeddings, payloads)
        ]
        
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points
        )
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        film: Optional[str] = None,
        kind: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            query_vector: Query embedding vector
            limit: Number of results to return
            film: Optional film name filter
            kind: Optional document kind filter
            
        Returns:
            List of search results with scores and metadata
        """
        # Build filter
        filter_conditions = []
        if film:
            filter_conditions.append(
                FieldCondition(key="film", match=MatchValue(value=film))
            )
        if kind:
            filter_conditions.append(
                FieldCondition(key="kind", match=MatchValue(value=kind))
            )
        
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Perform search
        results = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            query_filter=search_filter
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "score": result.score,
                "chunk_id": result.id,
                "text": result.payload.get("text", ""),
                "source_id": result.payload.get("source_id"),
                "chunk_index": result.payload.get("chunk_index"),
                "kind": result.payload.get("kind"),
                "title": result.payload.get("title"),
                "film": result.payload.get("film"),
                "author": result.payload.get("author"),
                "uri": result.payload.get("uri")
            })
        
        return formatted_results


def get_qdrant_service() -> QdrantService:
    """Get Qdrant service instance."""
    return QdrantService()
