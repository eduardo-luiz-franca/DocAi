# TO DO: importar LLM do Ollama quando integrar


class QueryOptimizer:
    def __init__(self, llm):
        self.llm = llm

    def rewrite_query(self, query):
       prompt = f"""Você é um assistente de otimização de consultas, reescreva a 
       seguinte consulta de forma mais clara e objetiva,
       mantendo o mesmo significado:
       consulta: {query}"""
       optimized_query = self.llm.invoke(prompt)
       return optimized_query.strip()
    
    def expand_query(self, query):
        prompt = f"""Você é um assistente de expansão de consultas.
        Dado a consulta abaixo, gere 3 termos ou frases relacionadas
        que possam enriquecer a busca semântica.
        Retorne apenas os termos separados por vírgula, sem explicações.

        Consulta: {query}"""

        expanded_queries = self.llm.invoke(prompt)
        return [q.strip() for q in expanded_queries.split(",") if q.strip()]
    
    def optimize(self, query):
        rewritten = self.rewrite_query(query)
        expanded = self.expand_query(rewritten)
        return {
            "original": query,
            "rewritten": rewritten,
            "expanded": expanded,
        }