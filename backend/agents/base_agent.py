#classe base para os agentes, que define a estrutura básica e os métodos comuns a todos os agentes. 
# Cada agente específico irá herdar desta classe e implementar o método run() de acordo 
# com suas necessidades.

class BaseAgent:   
    def __init__(self, llm, name: str): # llm: modelo de linguagem (ex: OpenAI, HuggingFace) que o agente irá usar para processar os chunks
        self.llm = llm                  # name: nome do agente para fins de logging e identificação (ex: "CleanerAgent", "ContextAgent", "IndexerAgent")
        self.name = name               

    def log(self, message: str):       # método de logging simples para imprimir mensagens com o nome do agente como prefixo     
        print(f"[{self.name}] {message}")
    
    def run(self, chunk):
        raise NotImplementedError("Subclasses devem implementar o método run()")
