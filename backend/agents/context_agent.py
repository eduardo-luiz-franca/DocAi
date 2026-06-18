from backend.agents.base_agent import BaseAgent
from backend.models.models import Chunk, ChunkMetadata

class ContextAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="ContextAgent")

    def run(self, chunk: Chunk):
        self.log("Iniciando extração de contexto do chunk...")

        prompt = f"""Você é um assistente de extração de metadados.
Analise o texto abaixo e retorne exatamente:
- Tema principal (topic)
- Resumo breve (summary)
- Contém dados numéricos? (has_numerical_data): true ou false
- Contém tabelas? (has_tables): true ou false

Texto:
{chunk.clean_text}"""
        
        result = self.llm.invoke(prompt)
        chunk.metadata = ChunkMetadata(
        document_id=chunk.document_id,
        page_number=1,
        topic="a extrair",
        summary=str(result),
        has_numerical_data=False,
        has_tables=False,
)

        self.log("Extração de contexto concluída.")
        return chunk
