from backend.models.models import RetrievalLog, SearchResult


class SearchEngine:
    def __init__(self, llm, optmizer, vectorStore):
        self.llm = llm
        self.optimizer = optmizer
        self.vector_store = vectorStore

    def search(self, query: str, conversation_history = None) -> SearchResult:
        history_text = ""
        if conversation_history:
            for msg in conversation_history:
                role = "você" if msg['role'] == 'assistant' else "User"
                history_text+= f"{role}: {msg['content']}\n"
        is_document_related = self.optimizer.is_document_related(query)
        if not is_document_related:
            prompt = f"""Você é um assistente especializado em análise de documentos. Você pode:
- Responder perguntas sobre arquivos PDF que o usuário anexou.
- Extrair informações e dados dos documentos
- Buscar informações específicas em seus arquivos
- Conversar normalmente sobre outros assuntos

Responda em português brasileiro, breve e natural (máximo 2 ou 3 frases).

Histórico da conversa:
{history_text}

Pergunta: {query}

Resposta:"""

            answer = self.llm.invoke(prompt)
            log = RetrievalLog(
                original_query=query,
                rewritten_query=query,
                technique_applied="Conversação Geral (sem busca documental)",
                reasoning="Pergunta não está relacionada a documentos indexados.",
                chunks_retrieved=0,
            )
            return SearchResult(answer=answer, source_chunks=[], retrieval_log=log)

        optimized = self.optimizer.optimize(query, conversation_history=conversation_history)

        results = self.vector_store.search(
            optimized["rewritten"],
            filters=optimized["filters"] if optimized["filters"] else None,
        )

        context = "\n\n".join(
            f"[{i+1}] (score {r['score']}) {r['text']}"
            for i, r in enumerate(results)
        )

        prompt = f"""Você é um assistente de análise de documentos. Responda em português brasileiro, breve e natural (máximo 2 ou 3 frases).

Histórico da conversa:
{history_text}

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
