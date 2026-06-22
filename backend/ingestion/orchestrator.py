import uuid

from backend.models.models import Document, Chunk, ProcessingStatus
from backend.ingestion.parser import PDFParser


class IngestionOrchestrator:
    """
    Controla o pipeline de ingestão de documentos.
    Responsabilidades:
    - Receber lista de arquivos PDF
    - Respeitar o limite de lote (batch_size)
    - Instanciar o PDFParser e obter os chunks
    - Repassar os chunks para o pipeline de agentes
    - Atualizar o status do Document durante o processo
    """

    def __init__(self, batch_size: int, parser: PDFParser, agent_pipeline):
        # batch_size: quantidade máxima de documentos processados por vez
        # parser: instância do PDFParser
        # agent_pipeline: pipeline LangChain com os 3 agentes (Cleaner → Context → Indexer)
        self.batch_size = batch_size
        self.parser = parser
        self.agent_pipeline = agent_pipeline

    def _build_document(self, file_path: str) -> Document:
        from unstructured.partition.auto import partition

        elements = partition(filename=file_path)
        pages = {el.metadata.page_number for el in elements if el.metadata.page_number}
        total_pages = len(pages) if pages else 1

        return Document(
            id=str(uuid.uuid4()),
            filename=file_path.split("/")[-1],
            file_path=file_path,
            total_pages=total_pages,
        )

    def _process_document(self, document: Document) -> list[Chunk]:
        """
        Processa um único documento:
        1. Atualiza status para PROCESSING
        2. Extrai chunks via PDFParser
        3. Passa cada chunk pelo pipeline de agentes
        4. Atualiza status para DONE ou ERROR
        """
        document.status = ProcessingStatus.PROCESSING

        try:
            chunks = self.parser.parse(document)

            processed_chunks = []
            for chunk in chunks:
                result = self.agent_pipeline(chunk)
                processed_chunks.append(result)

            document.status = ProcessingStatus.DONE
            return processed_chunks

        except Exception as e:
            document.status = ProcessingStatus.ERROR
            raise RuntimeError(f"Erro ao processar documento {document.filename}: {e}")

    def run(self, file_paths: list[str]) -> dict:
        """
        Método principal. Recebe lista de caminhos de PDFs,
        respeita o batch_size e processa cada documento em sequência.
        Retorna um relatório com documentos processados e total de chunks gerados.
        """
        # Aplica o limite de lote
        batch = file_paths[:self.batch_size]

        report = {
            "total_files_received": len(file_paths),
            "total_files_processed": 0,
            "total_chunks_generated": 0,
            "documents": [],
            "document_objects": [],
        }

        for file_path in batch:
            document = self._build_document(file_path)

            chunks = self._process_document(document)

            report["total_files_processed"] += 1
            report["total_chunks_generated"] += len(chunks)
            report["documents"].append({
                "id": document.id,
                "filename": document.filename,
                "status": document.status,
                "chunks_generated": len(chunks),
            })
            report["document_objects"].append(document)

        return report