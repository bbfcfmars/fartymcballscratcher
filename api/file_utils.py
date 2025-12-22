"""Utilities for extracting text from various file formats."""

import io
from PyPDF2 import PdfReader
from docx import Document
import pysrt


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from a PDF file."""
    try:
        pdf_file = io.BytesIO(content)
        pdf_reader = PdfReader(pdf_file)
        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from a DOCX file."""
    try:
        docx_file = io.BytesIO(content)
        doc = Document(docx_file)
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        return "\n\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_srt(content: bytes) -> str:
    """Extract text from an SRT subtitle file."""
    try:
        # Decode and parse
        text_content = content.decode('utf-8')
        subs = pysrt.from_string(text_content)
        text_parts = [sub.text for sub in subs]
        return "\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to extract text from SRT: {str(e)}")


def extract_text_from_txt(content: bytes) -> str:
    """Extract text from a plain text file."""
    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        # Try with latin-1 encoding as fallback
        return content.decode('latin-1')
    except Exception as e:
        raise ValueError(f"Failed to read text file: {str(e)}")


def extract_text_from_file(content: bytes, filename: str) -> str:
    """
    Extract text from file content based on filename extension.

    Supported formats: .pdf, .docx, .txt, .srt

    Args:
        content: Raw bytes content of the file
        filename: Original filename to determine file type

    Returns:
        Extracted text as string
    """
    filename_lower = filename.lower()

    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(content)
    elif filename_lower.endswith('.docx'):
        return extract_text_from_docx(content)
    elif filename_lower.endswith('.srt'):
        return extract_text_from_srt(content)
    elif filename_lower.endswith('.txt'):
        return extract_text_from_txt(content)
    else:
        raise ValueError(
            f"Unsupported file format. Supported formats: .pdf, .docx, .txt, .srt"
        )
