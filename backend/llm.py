import os
from langchain_community.llms import Ollama

class OllamaLLM:
    def __init__(self, model_name=None, temperature=0.7):
        # base_url permite apontar para o container `ollama` no docker-compose.
        # Em execução local cai no default (localhost:11434).
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "llama3")
        self.temperature = temperature
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = Ollama(
            model=self.model_name,
            temperature=temperature,
            base_url=self.base_url,
        )

    def invoke(self, prompt: str) -> str:
        response = self.client.invoke(prompt)
        return response
