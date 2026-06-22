import os

from backend.models.models import Chunk
from backend.agents.base_agent import BaseAgent
from langchain_community.embeddings import OllamaEmbeddings


class IndexerAgent(BaseAgent):

    def __init__(self, llm, vectorstore):
        super().__init__(llm, name="IndexerAgent")
        self.embeddings = OllamaEmbeddings(
            model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
        self.vectorstore = vectorstore

    def run(self, chunk: Chunk):
        self.log("Iniciando geração de embedding do chunk...")

        chunk.embedding = self.embeddings.embed_query(chunk.clean_text)
        self.vectorstore.add(chunk)

        self.log("Geração de embedding concluída.")
        return chunk