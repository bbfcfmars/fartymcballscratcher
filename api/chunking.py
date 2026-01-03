"""Text chunking utilities for screenplay and general text."""

import re
from typing import List


def chunk_text(text: str, kind: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Intelligently chunk text based on document kind.
    
    Args:
        text: The text to chunk
        kind: Document kind (script, review, interview, lecture, notes, subtitle)
        max_chunk_size: Maximum characters per chunk
        overlap: Characters to overlap between chunks for context
        
    Returns:
        List of text chunks
    """
    if kind == "script":
        return chunk_screenplay(text, max_chunk_size, overlap)
    else:
        return chunk_general(text, max_chunk_size, overlap)


def chunk_screenplay(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Chunk screenplay text while preserving scene structure.
    
    Screenplays have specific formatting:
    - Scene headings (INT./EXT.)
    - Character names (centered, all caps)
    - Dialogue
    - Action lines
    """
    chunks = []
    current_chunk = ""
    
    # Split by double newline (scene/paragraph boundaries)
    paragraphs = re.split(r'\n\n+', text)
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # Check if adding this paragraph exceeds chunk size
        if len(current_chunk) + len(para) + 2 <= max_chunk_size:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
        else:
            # Save current chunk if not empty
            if current_chunk:
                chunks.append(current_chunk)
                
                # Add overlap from end of previous chunk
                if overlap > 0 and len(current_chunk) > overlap:
                    overlap_text = current_chunk[-overlap:].strip()
                    current_chunk = overlap_text + "\n\n" + para
                else:
                    current_chunk = para
            else:
                # Paragraph itself is too large, need to split it
                if len(para) > max_chunk_size:
                    # Split large paragraph by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        # If sentence itself is too large, force split by chunk size
                        if len(sent) > max_chunk_size:
                            # Split into max_chunk_size pieces as last resort
                            for i in range(0, len(sent), max_chunk_size):
                                chunk_piece = sent[i:i + max_chunk_size]
                                if current_chunk:
                                    chunks.append(current_chunk)
                                    current_chunk = ""
                                # Append the piece directly since it's already at max size
                                if i + max_chunk_size < len(sent):
                                    # Not the last piece, append immediately
                                    chunks.append(chunk_piece)
                                else:
                                    # Last piece, set as current_chunk
                                    current_chunk = chunk_piece
                        elif len(current_chunk) + len(sent) + 1 <= max_chunk_size:
                            current_chunk = (current_chunk + " " + sent).strip()
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = sent
                else:
                    current_chunk = para
    
    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def chunk_general(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Chunk general text (reviews, interviews, lectures, notes) by paragraphs.
    """
    chunks = []
    current_chunk = ""
    
    # Split by paragraph
    paragraphs = re.split(r'\n\n+', text)
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # Try to add paragraph to current chunk
        test_chunk = (current_chunk + "\n\n" + para) if current_chunk else para
        
        if len(test_chunk) <= max_chunk_size:
            current_chunk = test_chunk
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(current_chunk)
                
                # Add overlap
                if overlap > 0 and len(current_chunk) > overlap:
                    overlap_text = current_chunk[-overlap:].strip()
                    current_chunk = overlap_text + "\n\n" + para
                else:
                    current_chunk = para
            else:
                # Single paragraph too large, split by sentences
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sent in sentences:
                    if len(current_chunk) + len(sent) + 1 <= max_chunk_size:
                        current_chunk = (current_chunk + " " + sent).strip()
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sent
    
    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    # Handle empty case
    if not chunks and text.strip():
        # Text is very short or has no paragraph breaks
        chunks.append(text.strip())
    
    return chunks
