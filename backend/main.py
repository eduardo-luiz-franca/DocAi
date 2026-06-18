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


app = FastAPI()

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

# Rota de ingestão — recebe uma lista de PDFs e inicia o pipeline
@app.post("/ingest")
def ingest(files: List[UploadFile], batch_size: int = 10):
    file_paths = [f.filename for f in files]
    orchestrator.batch_size = batch_size
    report = orchestrator.run(file_paths)
    return report

# Rota de busca — recebe a pergunta e retorna resposta + log CoT
@app.post("/search")
def search(query: SearchQuery):
    result = search_engine.search(query.query)
    return result