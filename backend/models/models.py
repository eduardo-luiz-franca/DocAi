from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class Document(BaseModel):
    id: str
    filename: str
    file_path: str
    total_pages: int
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    chunks_generated: int = 0


class ChunkMetadata(BaseModel):
    document_id: str
    page_number: int          # inteiro puro — regra de extração numérica
    topic: str
    summary: str
    has_numerical_data: bool  # booleano puro — contém dados numéricos?
    has_tables: bool          # booleano puro — contém tabelas?
    language: str = "pt"


class Chunk(BaseModel):
    id: str
    document_id: str
    raw_text: str
    clean_text: Optional[str] = None
    metadata: Optional[ChunkMetadata] = None
    embedding: Optional[list[float]] = None


class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    filter_language: Optional[str] = None
    filter_has_tables: Optional[bool] = None
    filter_document_id: Optional[str] = None


class RetrievalLog(BaseModel):
    original_query: str
    rewritten_query: Optional[str] = None
    technique_applied: str
    reasoning: str
    chunks_retrieved: int


class SearchResult(BaseModel):
    answer: str
    # Cada item: {"id": str, "text": str, "score": float}
    source_chunks: list[dict[str, Any]]
    retrieval_log: RetrievalLog
    created_at: datetime = Field(default_factory=datetime.utcnow)
