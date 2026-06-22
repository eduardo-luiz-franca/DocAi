from fastapi import FastAPI, UploadFile
from typing import List
from backend.models.models import SearchQuery

from backend.llm import OllamaLLM
from backend.vectorstore.store import VectorStore
from backend.ingestion.parser import PDFParser
from backend.ingestion.orchestrator import IngestionOrchestrator
from backend.agents.cleaner_agent import CleanerAgent
from backend.agents.context_agent import ContextAgent
from backend.agents.indexer_agent import IndexerAgent
from backend.retrieval.query_optimizer import QueryOptimizer
from backend.retrieval.search_engine import SearchEngine
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from backend.document_store import DocumentStore

document_store = DocumentStore()


class LoginRequest(BaseModel):
    username: str
    password: str


load_dotenv()

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instâncias dos módulos
llm = OllamaLLM()
vectorstore = VectorStore(collection_name="documentos")
parser = PDFParser(chunk_size=1000, chunk_overlap=200)

# Agentes
cleaner = CleanerAgent(llm=llm)
context = ContextAgent(llm=llm)
indexer = IndexerAgent(llm=llm, vectorstore=vectorstore)

# Pipeline de agentes
def agent_pipeline(chunk):
    chunk = cleaner.run(chunk)
    chunk = context.run(chunk)
    chunk = indexer.run(chunk)
    return chunk

# Orchestrator e SearchEngine
orchestrator = IngestionOrchestrator(batch_size=10, parser=parser, agent_pipeline=agent_pipeline)
optimizer = QueryOptimizer(llm=llm)
search_engine = SearchEngine(llm=llm, optmizer=optimizer, vectorStore=vectorstore)

# Rota de health check — confirma que a API está rodando
@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/auth/login")
def login(credentials: LoginRequest):
    valid_username = os.getenv("ADMIN_USERNAME")
    valid_password = os.getenv("ADMIN_PASSWORD")

    if credentials.username == valid_username and credentials.password == valid_password:
        return {"status": "ok"}
    return {"status": "error", "message": "Usuário ou senha incorretos"}

# Rota de ingestão — recebe uma lista de PDFs e inicia o pipeline
import shutil

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/ingest")
def ingest(files: List[UploadFile], batch_size: int = 10):
    file_paths = []

    for file in files:
        saved_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(saved_path)

    orchestrator.batch_size = batch_size
    report = orchestrator.run(file_paths)

    for i, document in enumerate(report["document_objects"]):
        chunks_count = report["documents"][i]["chunks_generated"]
        document_store.add(document, chunks_generated=chunks_count)

    return report

# Rota de busca — recebe a pergunta e retorna resposta + log CoT
@app.post("/search")
def search(query: SearchQuery):
    result = search_engine.search(query.query)
    return result

@app.get("/documents")
def list_documents():
    return {
        "documents": document_store.list_all(),
        "total_documents": document_store.total_documents(),
        "total_chunks": document_store.total_chunks(),
    }