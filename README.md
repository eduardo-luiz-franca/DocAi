# DocAI — Plataforma de Análise Documental com RAG

Sistema de análise e pesquisa documental inteligente com pipeline de agentes LangChain, LLM local via Ollama e busca semântica com ChromaDB.

---

## Tecnologias Utilizadas

| Tecnologia | Função |
|---|---|
| **FastAPI** | Framework web para a API do backend |
| **LangChain** | Orquestração dos agentes e pipeline de processamento |
| **Ollama** | LLM local (modelo llama3) para processamento de texto |
| **ChromaDB** | Banco de dados vetorial para busca semântica |
| **Unstructured** | Extração de texto de PDFs (digitais e escaneados) |
| **Pydantic** | Validação e tipagem dos dados |
| **Next.js** | Framework do frontend |

---

## Estrutura de Pastas

```
project/
├── backend/
│   ├── agents/
│   │   ├── base_agent.py        # Classe base para todos os agentes
│   │   ├── cleaner_agent.py     # Agente de limpeza do texto OCR
│   │   ├── context_agent.py     # Agente de extração de metadados
│   │   └── indexer_agent.py     # Agente de geração de embedding e indexação
│   ├── ingestion/
│   │   ├── parser.py            # Extração de texto dos PDFs via Unstructured
│   │   └── orchestrator.py      # Controle de lote e coordenação do pipeline
│   ├── models/
│   │   └── models.py            # Modelos Pydantic de dados
│   ├── retrieval/
│   │   ├── query_optimizer.py   # Otimização da query do usuário
│   │   └── search_engine.py     # Motor de busca e geração de resposta
│   ├── vectorstore/
│   │   └── store.py             # Abstração do ChromaDB
│   ├── llm.py                   # Wrapper do Ollama
│   └── main.py                  # Entry point da API FastAPI
└── frontend/
    ├── app/
    │   ├── page.tsx             # Tela de login
    │   └── dashboard/
    │       └── page.tsx         # Tela de dashboard
    └── components/              # Componentes reutilizáveis
```

---

## Modelos de Dados

- **Document** — representa o PDF original ingerido no sistema
- **Chunk** — unidade de texto que percorre o pipeline de agentes
- **ChunkMetadata** — metadados extraídos de cada chunk (tema, resumo, flags booleanas)
- **SearchQuery** — pergunta do usuário com filtros opcionais
- **RetrievalLog** — log do raciocínio do sistema (Chain of Thought)
- **SearchResult** — resposta final com chunks fonte e log CoT

---

## Pipeline de Agentes

Todos os agentes herdam de `BaseAgent` e seguem a mesma interface: `run(chunk) -> chunk`.

```
CleanerAgent → ContextAgent → IndexerAgent
```

1. **CleanerAgent** — corrige caracteres quebrados e formatação do OCR
2. **ContextAgent** — extrai tema, resumo e metadados estruturados do chunk
3. **IndexerAgent** — gera embedding via Ollama e persiste no ChromaDB

---

## Fluxos do Sistema

### Indexação
```
Upload de PDFs → PDFParser (OCR) → Chunking → Agentes → ChromaDB
```

### Chat
```
Pergunta → QueryOptimizer → ChromaDB.search() → Ollama LLM → Resposta + Log CoT
```

### Autenticação
```
Login → Validação via .env → Acesso ao Dashboard
```

---

## Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Health check |
| POST | `/ingest` | Ingestão de PDFs |
| POST | `/search` | Busca semântica e chat |

---

## Decisões Técnicas

**Por que Unstructured para OCR?**
Combina múltiplas estratégias automaticamente — PyMuPDF para PDFs digitais e Tesseract para PDFs escaneados — com pré-processamento de imagem para documentos de baixa qualidade.

**Por que ChromaDB?**
Suporte nativo a filtros por metadados, persistência em disco automática e integração plug-and-play com LangChain. Ideal para o escopo do projeto.

**Por que Ollama?**
Permite rodar LLMs localmente sem depender de APIs externas, com suporte a GPU via Docker.

**Por que Pydantic?**
Garante tipagem estrita nas saídas dos agentes — números como inteiros puros e booleanos sem texto adicional, conforme exigido pelo desafio.