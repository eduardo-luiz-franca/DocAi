import chromadb

class VectorStore:
    def __init__(self, collection_name):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)

    def add(self, chunk):
        self.collection.add(
        ids=[chunk.id],
        embeddings=[chunk.embedding],
        documents=[chunk.clean_text],
)
    def search(self, query):
        return self.collection.query(
        query_texts=[query],
        n_results=5)