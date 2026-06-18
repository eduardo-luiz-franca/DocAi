from backend.models.models import Chunk
from backend.agents.base_agent import BaseAgent


class CleanerAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="CleanerAgent")

    def run(self, chunk: Chunk) -> Chunk:
        self.log("Iniciando limpeza do chunk...")

        prompt = f"""Você é um assistente de limpeza de texto.
        Corrija caracteres quebrados, espaços errados e formatação desconfigurada.
        Retorne apenas o texto corrigido, sem explicações.

        Texto:
        {chunk.raw_text}"""

        result = self.llm.invoke(prompt)
        chunk.clean_text = result

        self.log("Limpeza concluída.")
        return chunk