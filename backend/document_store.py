from backend.models.models import Document


class DocumentStore:
    """
    Guarda os documentos processados em memória durante a execução do servidor.
    Permite listar e atualizar o status dos documentos entre requisições.
    """

    def __init__(self):
        self.documents: list[Document] = []

    def add(self, document: Document, chunks_generated: int = 0):
        document.chunks_generated = chunks_generated
        self.documents.append(document)

    def list_all(self) -> list[Document]:
        return self.documents

    def total_documents(self) -> int:
        return len(self.documents)

    def total_chunks(self) -> int:
        return sum(getattr(doc, "chunks_generated", 0) for doc in self.documents)