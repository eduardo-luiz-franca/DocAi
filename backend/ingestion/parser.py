from unstructured.partition.auto import partition
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.models.models import Chunk, Document

import uuid

class PDFParser:
    def __init__(self, chunk_size, chunk_overlap):
        self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def _extract_text(self, file_path):
       elements = partition(filename=file_path)
       text = "\n".join([el.text for el in elements if el.text])
       return text
    
    def parse(self, document: Document):
        chunks = []
        self.extracted_text = self._extract_text(document.file_path)
        raw_chunks = self.splitter.split_text(self.extracted_text)
        for raw_text in raw_chunks:
            chunk = Chunk(
            id=str(uuid.uuid4()),
            document_id=document.id,
            raw_text=raw_text,
)
            chunks.append(chunk)
        return chunks
