# Production-Grade RAG System

A document question-answering backend built from two services:

- **Backend API** — an Express and Prisma service for account management, authentication, and document metadata.
- **RAG service** — a FastAPI service containing PDF extraction, chunking, embedding, hybrid retrieval, reranking, and answer-generation components.

The repository currently contains the backend services only; there is no web or mobile frontend.

## Current status

The RAG components and backend APIs are present, but the document flow is not yet connected end to end:

- The authenticated backend upload endpoint stores an allowed file in `backend/uploads` and records its metadata in PostgreSQL. It does not call the RAG ingestion endpoint.
- The RAG service accepts PDF files directly at `/api/ingestion/process`, but that handler currently references `document_id` and `chunks` before initializing them. Ingestion must be fixed before relying on that endpoint.
- The RAG endpoint expects a RAG document ID. The backend does not currently create or synchronize that ID with its PostgreSQL document record.
- The backend upload filter accepts PDF, Markdown, and plain-text MIME types, while RAG ingestion currently accepts PDFs only.

As a result, uploading a document through the backend does not currently make it available for question answering.

## Architecture

```text
Client
  |
  v
Express API (default port 5000) ---- PostgreSQL via Prisma
  |                                      |
  | asks questions                      | accounts, documents, chats
  v
FastAPI RAG service (default port 8000)
  |
  +-- PDF text extraction (pypdf)
  +-- overlapping word chunks
  +-- embeddings (all-MiniLM-L6-v2)
  +-- vector storage (persistent ChromaDB)
  +-- BM25 retrieval + reciprocal-rank fusion
  +-- cross-encoder reranking
  +-- answer generation (Ollama, llama3.2:latest)
  +-- source metadata
```

The RAG service stores vector data in `rag-service/chroma_db` and BM25 indexes in `rag-service/bm25_indexes`, relative to its working directory. These are local persistent stores, not shared or managed services.

## Requirements

- Node.js and npm
- Python and pip
- PostgreSQL
- Ollama, with the `llama3.2:latest` model available

The RAG embedding and reranker models are loaded through Sentence Transformers and may be downloaded the first time they are used.

## Setup

### 1. Configure PostgreSQL and the backend

Create a PostgreSQL database, then create `backend/.env` from the example:

```powershell
cd backend
Copy-Item .env.example .env
```

Set the values in `backend/.env`:

```dotenv
PORT=5000
DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/DATABASE_NAME?schema=public"
JWT_SECRET=replace_with_a_long_random_secret
NODE_ENV=development

# Used to construct password-reset links:
FRONTEND_URL=http://localhost:3000

# Optional: configure SMTP to email password-reset links.
# Without these, the reset URL is printed in the backend terminal.
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=

# Optional; defaults to http://localhost:8000.
RAG_SERVICE_URL=http://localhost:8000
```

`JWT_SECRET` should be a strong, private value. The backend currently sets JWT expiration to seven days in code; `JWT_EXPIRES_IN` in the example environment file is not used by the implementation.

Install dependencies and apply the checked-in Prisma migrations:

```powershell
npm install
npx prisma generate
npx prisma migrate deploy
```

### 2. Install RAG service dependencies

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Install and start Ollama separately, then fetch the configured generation model:

```powershell
ollama pull llama3.2:latest
```

The RAG service also uses the model names declared in its embedding and reranking service modules. Those models are retrieved by their libraries when needed.

## Run locally

Start the RAG service from its directory:

```powershell
cd rag-service
uvicorn app.main:app --reload --port 8000
```

In a second terminal, start the backend:

```powershell
cd backend
npm run dev
```

The backend starts on `http://localhost:5000` by default and connects to PostgreSQL before listening. The RAG service starts on `http://localhost:8000`.

Interactive RAG API documentation is available at `http://localhost:8000/docs`.

## API overview

### Backend (`http://localhost:5000`)

| Method | Path | Authentication | Purpose |
|---|---|---|---|
| `GET` | `/` | No | Backend welcome response |
| `POST` | `/api/auth/register` | No | Create an account |
| `POST` | `/api/auth/login` | No | Log in and receive a bearer token |
| `GET` | `/api/auth/me` | Bearer token | Return the authenticated user |
| `POST` | `/api/auth/forgot-password` | No | Request a password-reset link |
| `POST` | `/api/auth/reset-password` | No | Reset a password using a token |
| `POST` | `/api/auth/change-password` | Bearer token | Change the authenticated user's password |
| `POST` | `/api/documents/upload` | Bearer token | Store an uploaded file and its metadata |
| `GET` | `/api/documents` | Bearer token | List the authenticated user's documents |
| `GET` | `/api/documents/:id` | Bearer token | Get one of the user's documents |
| `DELETE` | `/api/documents/:id` | Bearer token | Delete a user's document and stored file |
| `POST` | `/api/documents/:documentId/ask` | Bearer token | Ask the RAG service about a document |

Send authenticated backend requests with:

```http
Authorization: Bearer <token>
```

Document uploads use `multipart/form-data` with a field named `file`. The backend accepts PDF, Markdown, and plain text uploads up to 10 MB.

### RAG service (`http://localhost:8000`)

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Health response |
| `POST` | `/api/ingestion/process` | Accept a PDF for extraction and indexing |
| `POST` | `/api/retrieval/search` | Retrieve relevant chunks for a document |
| `POST` | `/api/rag/ask` | Retrieve context and generate an answer with sources |
| `GET` | `/docs` | Interactive OpenAPI documentation |

Retrieval and question requests use JSON in this form:

```json
{
  "document_id": "<rag-document-id>",
  "query": "What does the document say about ...?",
  "top_k": 5
}
```

`top_k` is optional and defaults to `5`. Ingestion expects a PDF file upload using a multipart field named `file`.

## Repository layout

```text
.
├── backend/
│   ├── prisma/             # PostgreSQL schema and migrations
│   ├── src/
│   │   ├── controllers/    # HTTP request handlers
│   │   ├── middleware/     # Authentication and file upload
│   │   ├── routes/         # Express route definitions
│   │   └── services/       # Auth, document, and RAG client logic
│   └── uploads/            # Local uploaded files
├── rag-service/
│   └── app/
│       ├── api/            # FastAPI route handlers
│       └── services/       # Extraction, indexing, retrieval, and generation
├── requirements.txt        # Python dependencies
└── README.md
```

## Notes

- Uploaded files, ChromaDB data, and BM25 indexes are stored locally; configure persistent storage and backups before deploying.
- Keep `.env` files and credentials out of source control.
- There are no automated test scripts currently declared in `backend/package.json`.