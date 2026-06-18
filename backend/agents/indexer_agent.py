from backend.models.models import Chunk
from backend.agents.base_agent import BaseAgent
from langchain_community.embeddings import OllamaEmbeddings


class IndexerAgent(BaseAgent):

    def __init__(self, llm, vectorstore):
        super().__init__(llm, name="IndexerAgent")
        self.embeddings = OllamaEmbeddings(model="llama3-7b")
        self.vectorstore = vectorstore

    def run(self, chunk: Chunk):
        self.log("Iniciando geração de embedding do chunk...")

        chunk.embedding = self.embeddings.embed_query(chunk.clean_text)
        self.vectorstore.add(chunk)

        self.log("Geração de embedding concluída.")
        return chunk