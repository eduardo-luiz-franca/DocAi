# DocAI — Plataforma de Análise Documental com RAG

Sistema de análise e pesquisa documental inteligente com pipeline de agentes LangChain, LLM local via Ollama e busca semântica com ChromaDB.

---

## Tecnologias

| Tecnologia | Função |
|---|---|
| **FastAPI** | API do backend |
| **LangChain** | Orquestração do pipeline de agentes |
| **Ollama** | LLM local (`llama3.2:3b`) com suporte a GPU NVIDIA |
| **ChromaDB** | Banco vetorial persistente (serviço dedicado) |
| **Unstructured** | OCR e extração de texto de PDFs digitais e escaneados |
| **ftfy** | Correção de encoding e artefatos de OCR (CleanerAgent) |
| **YAKE** | Extração de keywords sem LLM (ContextAgent + QueryOptimizer) |
| **Sumy / LSA** | Sumarização extrativa em português (ContextAgent) |
| **Pydantic** | Validação de saídas estruturadas dos agentes |
| **Next.js 16** | Frontend |
| **Docker Compose** | Orquestração dos serviços com suporte a GPU NVIDIA |

---

## Como rodar

### Pré-requisitos
- Docker Desktop instalado e rodando
- (Opcional) NVIDIA GPU + `nvidia-container-toolkit` para aceleração

### 1. Configure as credenciais

```bash
cp .env.example .env
```

Edite o `.env` com seu usuário e senha:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=sua_senha
```

### 2. Suba os serviços

```bash
docker compose up --build
```

Na primeira execução os modelos `llama3.2:3b` (~2 GB) e `nomic-embed-text` (~270 MB) são baixados automaticamente. Nas execuções seguintes o cache é reaproveitado.

### 3. Acesse

| Serviço | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| ChromaDB | http://localhost:8001 |
| Ollama | http://localhost:11434 |

---

## Estrutura de Pastas

```
desafioAcellerai/
├── backend/
│   ├── agents/
│   │   ├── base_agent.py        # Classe base com log() e run() abstrato
│   │   ├── cleaner_agent.py     # Agente 1: ftfy + regex (sem LLM)
│   │   ├── context_agent.py     # Agente 2: YAKE + Sumy LSA + Pydantic (sem LLM)
│   │   └── indexer_agent.py     # Agente 3: OllamaEmbeddings → ChromaDB
│   ├── ingestion/
│   │   ├── parser.py            # OCR via Unstructured + RecursiveCharacterTextSplitter
│   │   └── orchestrator.py      # Controle de batch_size e loop de documentos
│   ├── models/
│   │   └── models.py            # Schemas Pydantic do sistema
│   ├── retrieval/
│   │   ├── query_optimizer.py   # Pre-retrieval: Routing, Rewriting, Expansion, Filtering
│   │   └── search_engine.py     # Busca vetorial + geração de resposta + RetrievalLog
│   ├── vectorstore/
│   │   └── store.py             # ChromaDB HttpClient (serviço externo)
│   ├── document_store.py        # Store in-memory de documentos processados
│   ├── llm.py                   # Wrapper OllamaLLM (lê OLLAMA_BASE_URL do ambiente)
│   ├── main.py                  # Entrypoint FastAPI: rotas, CORS, instâncias
│   └── Dockerfile
├── front-end-novo/
│   ├── app/
│   │   ├── page.tsx             # Rota raiz → Login
│   │   └── dashboard/page.tsx   # Dashboard principal
│   ├── components/
│   │   ├── login-form.tsx       # POST /auth/login
│   │   ├── dashboard-header.tsx
│   │   ├── stats-cards.tsx      # Total docs, chunks, status do pipeline
│   │   ├── documents-panel.tsx  # Tabela paginada + upload + batch size
│   │   └── chat-panel.tsx       # Chat RAG + painel Chain of Thought
│   ├── components/ui/           # Button, Input, Label
│   ├── lib/
│   │   ├── api.ts               # API_URL (NEXT_PUBLIC_API_URL)
│   │   ├── utils.ts             # cn() — merge de classes Tailwind
│   │   └── docai-data.ts        # Tipos TypeScript compartilhados
│   └── Dockerfile               # Build multi-stage Node 20 Alpine
├── uploads/                     # PDFs recebidos pelo backend
├── docker-compose.yml
├── requirements.txt
├── .env                         # Credenciais reais (não commitado)
└── .env.example                 # Template com todas as variáveis
```

---

## Pipeline de Ingestão

```
Upload de PDFs (POST /ingest?batch_size=N)
    │
    ├─ IngestionOrchestrator  →  respeita batch_size
    │
    ├─ PDFParser
    │   ├─ Unstructured (OCR + extração de texto)
    │   └─ RecursiveCharacterTextSplitter  →  list[Chunk]
    │
    └─ Para cada Chunk:
        ├─ CleanerAgent   →  ftfy + regex  →  chunk.clean_text
        ├─ ContextAgent   →  YAKE + Sumy LSA + Pydantic  →  chunk.metadata
        └─ IndexerAgent   →  OllamaEmbeddings  →  ChromaDB.add()
```

## Pipeline de Busca (Chat RAG)

```
Pergunta (POST /search)
    │
    ├─ QueryOptimizer
    │   ├─ route()            →  Semantic Routing: simples | complexa | factual (heurística)
    │   ├─ rewrite_query()    →  Query Rewriting via LLM
    │   ├─ expand_query()     →  Query Expansion via YAKE (sem LLM)
    │   └─ metadata_filter()  →  Metadata Pre-filtering
    │
    ├─ VectorStore.search()
    │   ├─ OllamaEmbeddings.embed_query()
    │   └─ ChromaDB.query(query_embeddings)  →  list[{id, text, score}]
    │
    ├─ OllamaLLM.invoke(prompt + contexto)
    │
    └─ SearchResult
        ├─ answer          →  resposta do LLM (máx. 3 parágrafos)
        ├─ source_chunks   →  chunks recuperados
        └─ retrieval_log   →  técnica aplicada + raciocínio (Chain of Thought)
```

---

## Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Health check |
| POST | `/auth/login` | Autenticação via credenciais do `.env` |
| POST | `/ingest` | Ingestão de PDFs (`?batch_size=N`) |
| POST | `/search` | Busca semântica e resposta do LLM |
| GET | `/documents` | Lista documentos processados |

---

## Variáveis de Ambiente

| Variável | Padrão (Docker) | Descrição |
|---|---|---|
| `ADMIN_USERNAME` | — | Usuário de acesso à plataforma |
| `ADMIN_PASSWORD` | — | Senha de acesso à plataforma |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Endpoint do Ollama |
| `OLLAMA_MODEL` | `llama3.2:3b` | Modelo LLM para geração de resposta |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Modelo de embeddings |
| `OLLAMA_KEEP_ALIVE` | `10m` | Tempo que o modelo fica na VRAM após última requisição |
| `CHROMA_HOST` | `chroma` | Host do ChromaDB |
| `CHROMA_PORT` | `8000` | Porta do ChromaDB |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | URL da API consumida pelo browser |

---

## Serviços Docker

| Container | Imagem | Porta | Descrição |
|---|---|---|---|
| `rag-ollama` | `ollama/ollama:latest` | 11434 | LLM local com GPU |
| `rag-ollama-pull` | `ollama/ollama:latest` | — | One-shot: baixa os modelos na primeira execução |
| `rag-chroma` | `chromadb/chroma:0.5.23` | 8001 | Banco vetorial persistente |
| `rag-backend` | build local | 8000 | API FastAPI |
| `rag-frontend` | build local | 3000 | Interface Next.js |

Ordem de subida: `ollama` healthy → `ollama-pull` completa → `chroma` healthy → `backend` → `frontend`.

---

## Atualizar sem rebuild

| Mudança | Comando |
|---|---|
| Código Python (sem nova dependência) | `docker compose restart backend` |
| Frontend (CSS, componentes) | `docker compose up --build frontend` |
| Nova dependência ou Dockerfile | `docker compose up --build` |
