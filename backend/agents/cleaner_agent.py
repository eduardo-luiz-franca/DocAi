import re
import unicodedata

import ftfy

from backend.agents.base_agent import BaseAgent
from backend.models.models import Chunk


class CleanerAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="CleanerAgent")

    def run(self, chunk: Chunk) -> Chunk:
        self.log("Iniciando limpeza do chunk...")

        text = chunk.raw_text

        # Corrige encoding quebrado, mojibake e ligaduras de OCR (ex: ﬁ → fi)
        text = ftfy.fix_text(text)

        # Normaliza formas Unicode equivalentes (NFKC: ex: ＡＢＣ → ABC)
        text = unicodedata.normalize("NFKC", text)

        # Remove caracteres nulos e de controle (exceto \n e \t)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Colapsa espaços e tabs múltiplos em um único espaço
        text = re.sub(r"[ \t]+", " ", text)

        # Reduz mais de 2 quebras de linha consecutivas para 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        chunk.clean_text = text.strip()

        self.log("Limpeza concluída.")
        return chunk
