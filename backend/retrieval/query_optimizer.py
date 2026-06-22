import re

import yake


class QueryOptimizer:
    def __init__(self, llm):
        self.llm = llm
        self._kw_extractor = yake.KeywordExtractor(lan="pt", n=2, top=3, dedupLim=0.7)

    def rewrite_query(self, query: str) -> str:
        prompt = f"""Reescreva a consulta abaixo de forma mais clara e objetiva, \
mantendo o mesmo significado. Retorne apenas a consulta reescrita, sem explicações.
Consulta: {query}"""
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

    def optimize(self, query: str, language=None, has_tables=None) -> dict:
        route = self.route(query)                # Semantic Routing — sem LLM
        rewritten = self.rewrite_query(query)    # Query Rewriting  — 1 chamada LLM
        expanded = self.expand_query(rewritten)  # Query Expansion  — YAKE, sem LLM
        filters = self.metadata_filter(language, has_tables)  # Metadata Pre-filtering

        return {
            "original": query,
            "rewritten": rewritten,
            "expanded": expanded,
            "filters": filters,
            "route": route,
        }
