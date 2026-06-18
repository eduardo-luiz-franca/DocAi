from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"       # documento aguardando processamento
    PROCESSING = "processing" # documento sendo processado
    DONE = "done"             # documento processado com sucesso
    ERROR = "error"           # erro durante o processamento


class Document(BaseModel):
    id: str                   # identificador único do documento
    filename: str             # nome do arquivo PDF
    file_path: str            # caminho do arquivo no sistema
    total_pages: int          # total de páginas do PDF
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChunkMetadata(BaseModel):
    document_id: str          # id do documento de origem
    page_number: int          # inteiro puro — regra de extração numérica
    topic: str                # tema principal do chunk
    summary: str              # resumo breve do chunk
    has_numerical_data: bool  # booleano puro — contém dados numéricos?
    has_tables: bool          # booleano puro — contém tabelas?
    language: str = "pt"      # idioma do chunk


class Chunk(BaseModel):
    id: str                              # identificador único do chunk
    document_id: str                     # id do documento de origem
    raw_text: str                        # texto cru vindo do OCR
    clean_text: Optional[str] = None     # preenchido pelo CleanerAgent
    metadata: Optional[ChunkMetadata] = None  # preenchido pelo ContextAgent
    embedding: Optional[list[float]] = None   # preenchido pelo IndexerAgent


class SearchQuery(BaseModel):
    query: str                              # pergunta do usuário
    top_k: int = 5                          # quantidade de chunks a recuperar
    filter_language: Optional[str] = None   # filtro por idioma
    filter_has_tables: Optional[bool] = None  # filtro por presença de tabelas
    filter_document_id: Optional[str] = None  # filtro por documento específico


class RetrievalLog(BaseModel):
    original_query: str              # pergunta original do usuário
    rewritten_query: Optional[str] = None  # pergunta reescrita pelo optimizer
    technique_applied: str           # técnica de pre-retrieval aplicada
    reasoning: str                   # raciocínio do agente (Chain of Thought)
    chunks_retrieved: int            # quantidade de chunks recuperados


class SearchResult(BaseModel):
    answer: str                      # resposta gerada pelo LLM
    source_chunks: list[Chunk]       # chunks que embasaram a resposta
    retrieval_log: RetrievalLog      # log completo do CoT
    created_at: datetime = Field(default_factory=datetime.utcnow)