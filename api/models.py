"""Database models for CinemaRAG."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Source(Base):
    """Source document metadata."""
    
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kind = Column(String(50), nullable=False)  # script, review, interview, lecture, notes, subtitle
    title = Column(String(500), nullable=False)
    film = Column(String(500))
    author = Column(String(500))
    uri = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to chunks
    chunks = relationship("Chunk", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Source(id={self.id}, kind={self.kind}, title={self.title})>"


class Chunk(Base):
    """Text chunk with embeddings stored in Qdrant."""
    
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within source
    text = Column(Text, nullable=False)
    qdrant_id = Column(String(100), nullable=False, unique=True)  # UUID for Qdrant point
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to source
    source = relationship("Source", back_populates="chunks")
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, source_id={self.source_id}, index={self.chunk_index})>"
