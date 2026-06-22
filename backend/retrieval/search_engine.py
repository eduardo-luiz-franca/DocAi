from backend.models.models import RetrievalLog, SearchResult


class SearchEngine:
    def __init__(self, llm, optmizer, vectorStore):
        self.llm = llm
        self.optimizer = optmizer
        self.vector_store = vectorStore

    def search(self, query: str) -> SearchResult:
        optimized = self.optimizer.optimize(query)

        # results: list[{"id", "text", "score"}]
        results = self.vector_store.search(
            optimized["rewritten"],
            filters=optimized["filters"] if optimized["filters"] else None,
        )

        context = "\n\n".join(
            f"[{i+1}] (score {r['score']}) {r['text']}"
            for i, r in enumerate(results)
        )

        prompt = f"""Você é um assistente de análise documental. Responda à pergunta usando APENAS as informações dos trechos abaixo.

Regras:
- Seja direto e objetivo.
- Se a informação estiver nos trechos, extraia e apresente de forma clara.
- Não invente informações que não estejam nos trechos.
- Responda em português, em no máximo 3 parágrafos curtos.

Pergunta: {query}

Trechos do documento:
{context}

Resposta:"""

        answer = self.llm.invoke(prompt)

        log = RetrievalLog(
            original_query=query,
            rewritten_query=optimized["rewritten"],
            technique_applied=(
                f"Semantic Routing ({optimized['route']}) + "
                "Query Expansion + Metadata Pre-filtering"
            ),
            reasoning=(
                f"Query reescrita para '{optimized['rewritten']}' "
                f"e expandida com: {optimized['expanded']}"
            ),
            chunks_retrieved=len(results),
        )

        return SearchResult(answer=answer, source_chunks=results, retrieval_log=log)
