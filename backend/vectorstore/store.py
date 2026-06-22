import os
import chromadb
from langchain_community.embeddings import OllamaEmbeddings


class VectorStore:
    def __init__(self, collection_name):
        host = os.getenv("CHROMA_HOST", "localhost")
        port = int(os.getenv("CHROMA_PORT", "8000"))
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection = self.client.get_or_create_collection(collection_name)

        # Mesmo modelo/endpoint usado pelo IndexerAgent ao gerar embeddings —
        # garante consistência de dimensão na busca.
        self.embedder = OllamaEmbeddings(
            model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    def add(self, chunk):
        meta = chunk.metadata.model_dump() if chunk.metadata else {}
        # Chroma não aceita None nos metadados — remove campos vazios
        meta = {k: v for k, v in meta.items() if v is not None}
        self.collection.add(
            ids=[chunk.id],
            embeddings=[chunk.embedding],
            documents=[chunk.clean_text],
            metadatas=[meta],
        )

    def search(self, query: str, n_results: int = 5, filters=None) -> list[dict]:
        query_embedding = self.embedder.embed_query(query)
        raw = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filters if filters else None,
        )
        # Normaliza o resultado do Chroma (listas de listas, índice 0 = primeiro query)
        ids = raw["ids"][0]
        docs = raw["documents"][0]
        distances = raw["distances"][0]
        return [
            {"id": ids[i], "text": docs[i], "score": round(1 - distances[i], 4)}
            for i in range(len(ids))
        ]
