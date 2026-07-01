import re

import yake


class QueryOptimizer:
    def __init__(self, llm):
        self.llm = llm
        self._kw_extractor = yake.KeywordExtractor(lan="pt", n=2, top=3, dedupLim=0.7)

    def rewrite_query(self, query: str, conversation_history=None) -> str:
        history_context = ""
        if conversation_history:
            history_context = "Histórico da conversa:\n"
            for msg in conversation_history[:-1]:  # Exclui a pergunta atual
                role = "Usuário" if msg["role"] == "user" else "Assistente"
                history_context += f"{role}: {msg['content']}\n"
            history_context += "\n"

        prompt = f"""Reescreva a consulta abaixo de forma mais clara e objetiva, \
levando em conta o histórico da conversa se houver. Retorne apenas a consulta reescrita, sem explicações.

{history_context}Consulta atual: {query}"""
        return self.llm.invoke(prompt).strip()

    def expand_query(self, query: str) -> list[str]:
        """Expansão via YAKE — extrai keywords sem chamar o LLM."""
        keywords = self._kw_extractor.extract_keywords(query)
        return [kw for kw, _ in keywords] if keywords else [query]

    def route(self, query: str) -> str:
        """Classificação via heurística — sem chamada ao LLM."""
        q = query.lower()
        factual_patterns = re.search(
            r"\b\d{4}\b|\b\d+[.,]\d+\b|quant|qual o valor|qual a data|"
            r"quando|onde|quem|qual o nome|qual o código|qual o número",
            q,
        )
        complex_patterns = re.search(
            r",| e (também|além|mais)| além (disso|de)| como (funciona|é feito)",
            q,
        )
        if factual_patterns:
            return "factual"
        if complex_patterns or len(query.split()) > 12:
            return "complexa"
        return "simples"

    def metadata_filter(self, language=None, has_tables=None) -> dict:
        filters = {}
        if language:
            filters["language"] = language
        if has_tables is not None:
            filters["has_tables"] = has_tables
        return filters

    def is_document_related(self, query: str) -> bool:
        """Detecta se a pergunta é sobre documentos ou conversação geral."""
        general_patterns = re.compile(
            r"bo[am]\s+(dia|tarde|noite)|"
            r"ola|olá|oi|opa|e\s+aí|"
            r"(o\s+)?que\s+(vc|você|voce)\s+faz|"
            r"qual\s+(é\s+)?(seu|teu)\s+nome|"
            r"(como|tá|tava)\s+(vc|você|voce)|"
            r"(quem|qual)\s+(é|sou)\s+(vc|você|voce)|"
            r"(qual|qual é)\s+(seu|teu)\s+(propósito|objetivo|função)|"
            r"para\s+que\s+(serve|você serve)|"
            r"obrigad(o|a)|vlw|valeu|thanks|obrigad|"
            r"hello|hi|hey|what\s+do\s+you\s+do|"
            r"(vc|você|voce)\s+(está|tá|estou)\s+aí|"
            r"tudo\s+bem|como\s+vai|e\s+aí|"
            r"retoma|continua|mais",
            re.IGNORECASE
        )
        return not bool(general_patterns.search(query))

    def optimize(self, query: str, conversation_history=None, language=None, has_tables=None) -> dict:
        route = self.route(query)                # Semantic Routing
        rewritten = self.rewrite_query(query, conversation_history)  # Query Rewriting  — 1 chamada LLM
        expanded = self.expand_query(rewritten)  # Query Expansion  — YAKE
        filters = self.metadata_filter(language, has_tables)  # Metadata Pre-filtering

        return {
            "original": query,
            "rewritten": rewritten,
            "expanded": expanded,
            "filters": filters,
            "route": route,
        }
