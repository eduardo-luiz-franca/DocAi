from langchain_community.llms import Ollama

class OllamaLLM:
    def __init__(self, model_name="llama3-7b", temperature=0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.client = Ollama(model=model_name, temperature=temperature)
 
    def invoke(self, prompt: str) -> str:
        response = self.client(prompt)
        return response