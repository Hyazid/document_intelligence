# Document Intelligence API

A production-quality RAG (Retrieval-Augmented Generation) system built with FastAPI, pgvector, and local LLMs via LM Studio. Upload documents, ask questions, get grounded answers — fully streamed via SSE.

---

## Architecture

```
Document Upload
      ↓
Text Extraction (PyMuPDF)
      ↓
Chunking (RecursiveCharacterTextSplitter, 512 tokens / 64 overlap)
      ↓
Embedding (nomic-embed-text-v1.5 via LM Studio)
      ↓
Storage (PostgreSQL + pgvector, HNSW index)

Query
      ↓
Embed Question → Vector Search (cosine similarity)
                + Keyword Search (PostgreSQL tsvector)
                → Hybrid Merge (Reciprocal Rank Fusion)
      ↓
Prompt Construction (top-k chunks as context)
      ↓
LLM Generation (Meta-Llama-3.1-8B-Instruct via LM Studio)
      ↓
Streaming Response (SSE)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI (async) |
| Database | PostgreSQL 16 + pgvector |
| Embeddings | nomic-embed-text-v1.5 (768 dims) |
| LLM | Meta-Llama-3.1-8B-Instruct (Q4_K_M) |
| Local inference | LM Studio |
| ORM | SQLAlchemy (async) |
| Containerization | Docker + Docker Compose |
| Eval | Custom eval pipeline + Ragas-compatible |

---

## Prerequisites

- Docker + Docker Compose
- [LM Studio](https://lmstudio.ai/) with the following models loaded:
  - `nomic-embed-text-v1.5` (embeddings)
  - `meta-llama-3.1-8b-instruct` (generation)
- LM Studio local server running on `http://localhost:1234`

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourname/document_intelligence.git
cd document_intelligence
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql://user:password@db:5432/docdb
LM_STUDIO_URL=http://host.docker.internal:1234/v1
LM_STUDIO_API_KEY=lm-studio
LLM_MODEL=meta-llama-3.1-8b-instruct
EMBED_MODEL=nomic-embed-text-v1.5
EMBED_DIMENSIONS=768
CHUNK_SIZE=512
CHUNK_OVERLAP=64
RETRIEVAL_TOP_K=5
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=512
LLM_CONTEXT_LENGTH=4096
```

### 3. Start LM Studio

- Open LM Studio → Local Server tab
- Load `nomic-embed-text-v1.5` and `meta-llama-3.1-8b-instruct`
- Start the server

### 4. Start the stack

```bash
docker-compose up --build
```

API available at `http://localhost:8000`  
Swagger UI at `http://localhost:8000/docs`

---

## API Reference

### Health

```
GET /health
```
```json
{"status": "ok"}
```

---

### Ingest a Document

```
POST /ingest
Content-Type: multipart/form-data
```

| Field | Type | Description |
|---|---|---|
| file | File | PDF or plain text file |

**Response:**
```json
{
  "document_id": "uuid",
  "filename": "report.pdf",
  "chunks": 42,
  "message": "Document ingested successfully"
}
```

---

### Query (Streaming)

```
POST /query
Content-Type: application/json
```

```json
{
  "question": "What are the main findings?",
  "top_k": 5
}
```

**Response:** `text/event-stream`
```
data: The
data:  main
data:  findings
data:  are...
```

---

### Retrieve Chunks (Raw)

```
POST /retrieve
Content-Type: application/json
```

```json
{
  "question": "What are the main findings?",
  "top_k": 5
}
```

**Response:**
```json
{
  "chunks": [
    {"content": "...", "score": 0.0312},
    {"content": "...", "score": 0.0287}
  ]
}
```

---

### List Documents

```
GET /documents
```

**Response:**
```json
[
  {
    "id": "uuid",
    "filename": "report.pdf",
    "created_at": "2026-08-13T00:00:00Z",
    "chunk_count": 42
  }
]
```

---

### Delete a Document

```
DELETE /documents/{document_id}
```

Deletes the document and all its associated chunks (cascade).

**Response:** `204 No Content`

---

## Project Structure

```
document_intelligence/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings via pydantic-settings
│   ├── database.py              # Async SQLAlchemy engine + session
│   ├── models/
│   │   └── document.py          # ORM models: Document, Chunk
│   ├── schemas/
│   │   └── document.py          # Pydantic schemas
│   ├── api/
│   │   ├── ingest.py            # POST /ingest
│   │   ├── query.py             # POST /query, POST /retrieve
│   │   └── documents.py         # GET /documents, DELETE /documents/{id}
│   └── services/
│       ├── chunker.py           # Text splitting
│       ├── embedder.py          # Embedding via LM Studio
│       ├── retriever.py         # Hybrid search (vector + BM25 + RRF)
│       └── generator.py         # LLM streaming generation
├── evals/
│   ├── golden_dataset.json      # Ground truth Q&A pairs
│   ├── run_evals.py             # Eval pipeline
│   └── results.json             # Latest eval results
├── migrations/
│   └── init.sql                 # pgvector schema + indexes
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Evaluation

Run the eval pipeline against a golden dataset:

```bash
# From project root
python evals/run_evals.py
```

Metrics computed:
- **Answer accuracy** — LLM answer contains expected keywords
- **Context recall** — Retrieved chunks contain the expected answer

Results saved to `evals/results.json`.

---

## Key Design Decisions

**Hybrid search over pure vector search**
Pure semantic search misses exact terms (names, codes, article numbers). Combining pgvector cosine similarity with PostgreSQL full-text search and merging via Reciprocal Rank Fusion gives significantly better recall.

**Local inference only**
All models run locally via LM Studio. No data leaves the machine. Suitable for sensitive documents.

**Streaming responses**
LLM responses stream token by token via SSE. No waiting for full generation — latency feels immediate to the user.

**HNSW indexing**
pgvector's HNSW index gives approximate nearest neighbor search in O(log n) time. Far faster than exact search at scale, with minimal quality loss.

---

## Hardware Requirements

Tested on:
- GPU: NVIDIA RTX 2060 (6GB VRAM)
- RAM: 16GB
- OS: Windows 11 + Docker Desktop (WSL2)

Models loaded simultaneously:
- `nomic-embed-text-v1.5` (~300MB VRAM)
- `meta-llama-3.1-8b-instruct Q4_K_M` (~4.7GB VRAM)
- Total: ~5GB — fits within 6GB with headroom

---

## License

MIT