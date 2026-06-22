import re

import yake
from pydantic import BaseModel, Field
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer

from backend.agents.base_agent import BaseAgent
from backend.models.models import Chunk, ChunkMetadata


class ChunkMetadataOutput(BaseModel):
    """Schema Pydantic que valida e tipifica os metadados extraídos.
    Regras do desafio:
    - page_number: inteiro puro.
    - has_numerical_data / has_tables: booleano puro.
    """
    topic: str = Field(description="Tema principal do chunk em poucas palavras")
    summary: str = Field(description="Resumo objetivo do conteúdo do chunk")
    page_number: int = Field(description="Número inteiro da página de origem")
    has_numerical_data: bool = Field(description="true se o texto contém dados numéricos")
    has_tables: bool = Field(description="true se o texto contém tabelas")
    language: str = Field(default="pt", description="Código ISO do idioma predominante")


_NUMERIC_PATTERN = re.compile(
    r"\b\d{4,}\b"           # números longos (anos, IDs, valores)
    r"|\b\d+[.,]\d+\b"      # decimais (1.234 / 3,14)
    r"|R\$\s*\d"            # valores monetários em BRL
    r"|\d+\s*%"             # percentuais
)

_TABLE_PATTERN = re.compile(
    r"\|.+\|"               # linhas com pipes (tabelas markdown/texto)
    r"|\t.+\t.+\t"          # colunas separadas por tab
    r"|[-=]{3,}\s*\n"       # separadores horizontais de tabela
)


class ContextAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="ContextAgent")
        self._kw_extractor = yake.KeywordExtractor(
            lan="pt", n=3, top=1, dedupLim=0.7
        )
        self._summarizer = LsaSummarizer()

    def _extract_topic(self, text: str) -> str:
        try:
            keywords = self._kw_extractor.extract_keywords(text)
            return keywords[0][0] if keywords else "geral"
        except Exception:
            return "geral"

    def _extract_summary(self, text: str, sentences: int = 2) -> str:
        try:
            parser = PlaintextParser.from_string(text, Tokenizer("portuguese"))
            parser.document.language = "portuguese"
            result = self._summarizer(parser.document, sentences)
            return " ".join(str(s) for s in result) or text[:300]
        except Exception:
            return text[:300]

    def run(self, chunk: Chunk) -> Chunk:
        self.log("Iniciando extração de contexto do chunk...")

        text = chunk.clean_text or chunk.raw_text

        topic = self._extract_topic(text)
        self.log(f"Chain of Thought — topic extraído via YAKE: '{topic}'")

        summary = self._extract_summary(text)
        self.log(f"Chain of Thought — summary gerado via LSA Sumy: '{summary[:80]}...'")

        has_numerical_data: bool = bool(_NUMERIC_PATTERN.search(text))
        has_tables: bool = bool(_TABLE_PATTERN.search(text))
        self.log(
            f"Chain of Thought — has_numerical_data: {has_numerical_data} | "
            f"has_tables: {has_tables} (detecção via regex)"
        )

        # Valida e tipifica com Pydantic — garante int puro e bool puro
        parsed = ChunkMetadataOutput(
            topic=topic,
            summary=summary,
            page_number=1,
            has_numerical_data=has_numerical_data,
            has_tables=has_tables,
        )

        chunk.metadata = ChunkMetadata(
            document_id=chunk.document_id,
            page_number=parsed.page_number,
            topic=parsed.topic,
            summary=parsed.summary,
            has_numerical_data=parsed.has_numerical_data,
            has_tables=parsed.has_tables,
            language=parsed.language,
        )

        self.log(
            f"Metadados extraídos — topic: '{parsed.topic}' | "
            f"has_tables: {parsed.has_tables} | has_numerical_data: {parsed.has_numerical_data}"
        )
        return chunk
