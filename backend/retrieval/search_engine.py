from backend.models.models import RetrievalLog, SearchResult

class SearchEngine:
    def __init__(self, llm, optmizer, vectorStore):
        self.llm = llm
        self.optimizer = optmizer
        self.vector_store = vectorStore


    def search(self, query):
        optimized = self.optimizer.optimize(query)
        results = self.vector_store.search(optimized["rewritten"])

        prompt = f"""Você é um assistente de análise documental.
        Responda a pergunta abaixo com base nos trechos de documentos fornecidos.
        Seja objetivo e cite qual trecho embasou sua resposta.

        Pergunta: {query}

        Trechos relevantes:
        {results}"""

        answer = self.llm.invoke(prompt)

        log = RetrievalLog(
            original_query=query,
            rewritten_query=optimized["rewritten"],
            technique_applied="Query Rewriting + Query Expansion",
            reasoning=f"Query reescrita para '{optimized['rewritten']}' e expandida com: {optimized['expanded']}",
            chunks_retrieved=len(results),
)

        return SearchResult(answer=answer, source_chunks=results, retrieval_log=log)
