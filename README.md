# Doclify

Doclify is a PDF question-answering application. Users create accounts, upload one or more PDF files into a chat, and ask questions about the uploaded documents. The backend stores users, chats, messages, and document processing state in PostgreSQL, indexes extracted PDF chunks in ChromaDB, and uses a LangGraph RAG workflow with Groq for contextualized answers.

> The repository is an active development project. This README describes the code that currently exists, including operational requirements and known gaps.

## Features

### Authentication

- User registration with username, email, and password validation.
- User login with bcrypt password verification.
- JWT bearer access tokens with configurable expiry.
- Persisted frontend authentication state through Zustand.
- Protected user and chat endpoints.
- Current-user endpoint at `GET /api/users/me`.

### PDF chats

- Create a chat by uploading one or more PDF files.
- Files are limited by `MAX_UPLOAD_SIZE` and stored under `backend/uploads/` using generated UUID filenames.
- PDF pages are loaded with `PyPDFLoader` and split into chunks of 1,000 characters with 100-character overlap.
- Each chat has its own Chroma collection named `chat_<chat_id>`.
- Documents expose `processing`, `ready`, or `failed` status and an optional processing error.
- Multiple documents can belong to one chat.
- Chats can be listed, opened, and deleted.
- Deleting a chat removes its local PDF files, database records, and Chroma collection.

### Retrieval-augmented chat

- Conversation history is loaded before answering.
- Follow-up questions can be rewritten into standalone questions by the LLM.
- A classifier decides whether a question needs document retrieval.
- Document questions use Chroma retrieval through LangChain's vector-store wrapper.
- Retrieval uses maximal marginal relevance (MMR), with configurable `top_k`, `fetch_k`, and `lambda_mult` parameters in `retrieve`.
- Retrieved chunks are included in a guarded prompt that tells the model to use document context as its source of truth and avoid inventing facts.
- General questions can bypass document retrieval and use a general assistant prompt.
- Assistant responses are rendered as GitHub-Flavored Markdown in the frontend.

### Conversation management

- Recent chat history is limited by `CHAT_HISTORY_LIMIT`.
- Older conversation content can be summarized asynchronously after `SUMMARY_THRESHOLD` new messages.
- Summaries are stored on the chat and included when contextualizing future questions.
- Celery tasks handle PDF embedding and chat summarization.

### Frontend experience

- Login and registration screens.
- Protected main application layout with a chat sidebar.
- New-chat flow with multiple PDF selection, removal, and upload.
- Processing indicators while PDFs are indexed.
- Chat input disabled until all attached documents are ready.
- Enter sends a message; Shift+Enter creates a new line.
- Optimistic display of the pending user message and an animated typing indicator.
- Chat history list, active-chat state, chat deletion, and logout.
- React Query caching and invalidation for chats and messages.
- Zod validation for API request and response payloads.
- Axios bearer-token injection for authenticated requests.

## Technology Stack

### Backend

- Python
- FastAPI and Uvicorn
- SQLAlchemy 2 async ORM
- PostgreSQL
- Alembic migrations
- Pydantic schemas
- JWT with `python-jose`
- Passlib with bcrypt
- Celery with Redis broker/result backend
- ChromaDB persistent vector database
- Sentence Transformers, using `all-MiniLM-L6-v2`
- LangChain Community integrations and text splitters
- LangGraph for the RAG workflow
- Groq's LangChain client with model `openai/gpt-oss-20b`
- PyPDF for PDF parsing

### Frontend

- React 18
- Vite
- React Router
- TanStack React Query
- Axios
- Zustand with persisted storage
- Zod
- React Markdown and Remark GFM
- Lucide React icons
- CSS with Google Fonts (`DM Sans` and `Fraunces`)

## Architecture

```text
Browser
  |
  | React + Vite
  | Axios /api client
  v
FastAPI API
  |
  +--> PostgreSQL: users, chats, messages, documents
  |
  +--> Redis: Celery broker and result backend
  |       |
  |       +--> PDF embedding task
  |       +--> conversation summary task
  |
  +--> ChromaDB: per-chat embedded PDF chunks
  |
  +--> LangGraph RAG workflow
          |
          +--> contextualize follow-up question
          +--> classify document need
          +--> retrieve with MMR, or answer directly
          +--> call Groq
```

### PDF processing flow

1. The client submits one or more PDFs to `POST /api/chats/documents`.
2. The API validates the MIME type, creates a chat, saves the files, and creates document rows with `processing` status.
3. A Celery `embed_file` task is queued for each document.
4. The worker loads PDF pages, splits them into chunks, and writes the chunks plus metadata to the chat's Chroma collection.
5. The worker marks the document `ready`, or records `failed` and an error message.
6. The frontend polls the chat while any document is still processing.

### Message flow

1. The client submits a chat ID and message to `POST /api/chats/messages`.
2. The API verifies that the chat belongs to the authenticated user.
3. Recent messages and the stored summary are loaded.
4. LangGraph contextualizes the question and classifies whether document retrieval is needed.
5. RAG questions are retrieved with MMR; general questions bypass retrieval.
6. The Groq client generates the answer.
7. User and assistant messages are stored together, and the response returns both messages.
8. A summary task is queued once the unsummarized message threshold is reached.

## Project Structure

```text
.
├── backend/
│   ├── api/
│   │   ├── router.py                         # Root API router
│   │   └── controllers/
│   │       ├── auth_controller.py            # Registration and login
│   │       ├── chat_controller.py            # Chat, upload, message, delete APIs
│   │       └── user_controller.py            # Current-user API
│   ├── alembic/
│   │   ├── env.py                            # Async Alembic environment
│   │   ├── script.py.mako                    # Migration template
│   │   └── versions/                         # Database migration history
│   ├── core/security/                        # Security package placeholder
│   ├── dependencies/auth.py                  # JWT bearer authentication dependency
│   ├── models/
│   │   ├── base.py                           # Shared UUID and created_at fields
│   │   ├── user.py                           # User model
│   │   ├── chat.py                           # Chat model and relationships
│   │   ├── chat_message.py                   # Message model and roles
│   │   └── document.py                       # Uploaded document model
│   ├── schemas/
│   │   ├── user.py                           # User request/response schemas
│   │   ├── login.py                          # Authentication response schema
│   │   └── chat.py                           # Chat, message, and document schemas
│   ├── services/
│   │   ├── auth/
│   │   │   ├── jwt.py                        # Token creation and decoding
│   │   │   └── password.py                   # Password hashing and verification
│   │   ├── chat/
│   │   │   ├── chat_service.py               # Chat/document persistence helpers
│   │   │   └── storage.py                    # Local PDF file storage
│   │   └── llm/
│   │       ├── client.py                     # Groq client and LLM helpers
│   │       ├── embed.py                      # PDF embedding Celery task and Chroma setup
│   │       ├── graph.py                      # LangGraph RAG workflow
│   │       ├── prompt.py                     # RAG and general prompts
│   │       ├── retrieval.py                  # MMR retrieval and RetrievedChunk
│   │       └── summarize.py                  # Conversation summary task
│   ├── tests/test_rag_contract.py            # RAG, contextualization, and upload tests
│   ├── celery_app.py                         # Celery application
│   ├── config.py                             # Environment-backed configuration
│   ├── database.py                           # Async SQLAlchemy engine/session
│   ├── requirements.txt                      # Python dependencies
│   ├── alembic.ini                           # Alembic configuration
│   └── server.py                             # FastAPI application and CORS
├── frontend/
│   ├── src/
│   │   ├── api/                              # Axios client, interceptors, API functions
│   │   ├── assets/icons/                     # SVG UI assets
│   │   ├── hooks/                             # Auth and chat React Query hooks
│   │   ├── lib/queryClient.js                # React Query defaults
│   │   ├── pages/
│   │   │   ├── login/                        # Login screen and styles
│   │   │   ├── register/                     # Registration screen and styles
│   │   │   ├── mainPage/                     # Protected shell
│   │   │   ├── sidebar/                      # Chat navigation and logout
│   │   │   ├── chatPage/                     # New-chat upload and chat view
│   │   │   └── chatMessage/                  # Message and typing indicator
│   │   ├── schemas/                          # Zod API schemas
│   │   ├── stores/authStore.js               # Persisted auth state
│   │   ├── App.jsx                           # Route definitions and guards
│   │   ├── App.css                            # Global design tokens and auth styles
│   │   └── main.jsx                           # React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── chroma_data/                              # Persistent Chroma data created at runtime
└── README.md
```

## Requirements

Install or run the following services before starting the application:

- Python 3.10+ with a virtual environment.
- Node.js and npm.
- PostgreSQL database.
- Redis server at `localhost:6379`, unless `backend/celery_app.py` is changed.
- A Groq API key.
- A working build environment for Sentence Transformers and its model dependencies.

The backend uses two database URLs:

- `DATABASE_URL` is used by the async FastAPI SQLAlchemy engine and Alembic.
- `CELERY_DATABASE_URL` is used by synchronous Celery tasks and must be compatible with SQLAlchemy's synchronous engine.

For PostgreSQL, a typical pair is:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/doclify
CELERY_DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/doclify
```

## Setup

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd pdf-website
```

### 2. Configure the backend

Create `backend/.env` because `backend/config.py` loads that exact file location:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/doclify
CELERY_DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/doclify
JWT_SECRET=replace-with-a-long-random-secret
ALGORITHM=HS256
JWT_EXPIRY_TIME=7
FRONTEND_URL=http://localhost:5173
GROQ_API_KEY=replace-with-your-groq-api-key
MAX_UPLOAD_SIZE=10485760
LLM_TOP_K=4
SUMMARY_LIMIT=20
SUMMARY_THRESHOLD=10
CHAT_HISTORY_LIMIT=12
```

Do not commit this file. Use a strong random value for `JWT_SECRET` and keep the Groq key private.

### 3. Install backend dependencies

From the project root on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

### 4. Prepare PostgreSQL and run migrations

Create the configured PostgreSQL database, then run migrations from the project root:

```bash
alembic -c backend/alembic.ini upgrade head
```

The migration history creates users, chats, chat messages, documents, chat summary fields, and message counts. The repository includes older duplicate/branch revisions and a merge revision, so inspect the migration state before applying migrations to an existing database.

### 5. Start Redis

Start Redis using the installation method appropriate for your operating system. The current Celery configuration expects:

```text
redis://localhost:6379/0
```

### 6. Start the backend API

From the project root:

```bash
python -m uvicorn backend.server:app --reload --port 8000
```

The API is available at `http://localhost:8000`. FastAPI's development documentation is available at `http://localhost:8000/docs`.

### 7. Start a Celery worker

From the project root with the virtual environment active:

```bash
celery -A backend.celery_app.celery_app worker --loglevel=info
```

The worker is required for PDF embedding and asynchronous chat summaries. On Windows, if the default worker pool causes issues, use Celery's solo pool for local development:

```bash
celery -A backend.celery_app.celery_app worker --pool=solo --loglevel=info
```

### 8. Install and start the frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite development server normally runs at `http://localhost:5173`.

## Configuration Reference

All backend configuration is read from `backend/.env`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | none | Async PostgreSQL URL for FastAPI and Alembic |
| `CELERY_DATABASE_URL` | none | Sync database URL for Celery tasks |
| `JWT_SECRET` | none | JWT signing secret |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_EXPIRY_TIME` | `7` | Token lifetime in days |
| `FRONTEND_URL` | unset | Allowed CORS origin; unset allows `*` |
| `GROQ_API_KEY` | none | Groq authentication used by LangChain Groq |
| `MAX_UPLOAD_SIZE` | `10485760` | Maximum PDF size in bytes, default 10 MiB |
| `LLM_TOP_K` | `4` | Number of document chunks returned to the answer prompt |
| `SUMMARY_LIMIT` | `20` | Number of recent messages folded into a summary task |
| `SUMMARY_THRESHOLD` | `10` | Message-count delta that triggers summarization |
| `CHAT_HISTORY_LIMIT` | `12` | Recent messages sent into the RAG workflow |

MMR tuning is currently implemented in `backend/services/llm/retrieval.py` with these defaults:

```python
retrieve(
    chat_id,
    question,
    top_k=4,
    fetch_k=20,
    lambda_mult=0.5,
)
```

`top_k` is the final number of chunks, `fetch_k` is the candidate pool size, and `lambda_mult` balances relevance against diversity. The graph currently configures only `top_k` from `LLM_TOP_K`; `fetch_k` and `lambda_mult` use the function defaults.

## API Reference

All routes are prefixed with `/api`. Protected routes require:

```http
Authorization: Bearer <access_token>
```

### Authentication

| Method | Path | Auth | Behavior |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register` | No | Creates a user and returns a JWT plus user data |
| `POST` | `/api/auth/login` | No | Verifies credentials and returns a JWT plus user data |

Registration expects `username`, `email`, and `password`. Usernames are 3-25 characters, emails are validated with `EmailStr`, and passwords are 8-128 characters.

### Users

| Method | Path | Auth | Behavior |
| --- | --- | --- | --- |
| `GET` | `/api/users/me` | Yes | Returns the authenticated user |

### Chats and documents

| Method | Path | Auth | Behavior |
| --- | --- | --- | --- |
| `GET` | `/api/chats` | Yes | Lists the user's chats, newest activity first |
| `GET` | `/api/chats/{chat_id}` | Yes | Returns one owned chat with messages and documents |
| `POST` | `/api/chats/documents` | Yes | Creates a chat and queues one embedding task per PDF |
| `POST` | `/api/chats/messages` | Yes | Runs the RAG workflow and stores user/assistant messages |
| `DELETE` | `/api/chats/{chat_id}` | Yes | Deletes the chat, files, database children, and embeddings |

The upload endpoint accepts multipart form data with one or more fields named `files`. Only `application/pdf` content types are accepted.

Message requests have this shape:

```json
{
  "chat_id": "00000000-0000-0000-0000-000000000000",
  "content": "What does the document say about ...?"
}
```

## Data Model

- `users`: username, email, bcrypt password hash, UUID, and creation time.
- `chats`: title, owner, optional conversation summary, summarized message position, message count, and creation time.
- `chat_messages`: role (`user`, `assistant`, or `system`), content, chat relationship, UUID, and creation time.
- `documents`: chat relationship, original filename, generated storage path, processing status, optional error, UUID, and creation time.

User-to-chat, chat-to-message, and chat-to-document relationships cascade on deletion. Documents are stored on the local filesystem; their vector representations are stored separately in persistent Chroma data.

## Database Migrations

Migration files are under `backend/alembic/versions/`. The current history includes:

- `c40345c2fa71_initial_schema.py`: initial users table.
- `572db7af7328_create_chats_chat_messages_tables.py`: historical cleanup revision.
- `e7d2cb22bfc7_removed_updated_at.py`: historical no-op cleanup revision.
- `48013cf3f1d2_add_chats_and_chat_messages_tables.py`: chats and chat messages tables.
- `819dfcb0d26d_added_document_and_document_.py`: earlier document migration.
- `0f3bd1d22b20_added_document_and_document_.py`: document table and relationship revision.
- `7ad66bdd1253_add_documents_table.py`: historical no-op document revision.
- `b5d9a8e3f1c2_allow_multiple_documents_per_chat.py`: removes the single-document constraint and adds a chat index.
- `6e25ec79d56a_allow_multiple_documents_per_chat.py`: historical follow-up no-op revision.
- `f2a1b8c4d6e0_add_chat_summary_fields.py`: chat summary columns.
- `a4c7e9f1b2d3_add_chat_message_count.py`: chat message count column.
- `c8d9e0f1a2b3_merge_chat_schema_heads.py`: merges the chat/document and summary branches.

Use `alembic current`, `alembic heads`, and `alembic history` to inspect the migration state of a database before upgrading it.

## Testing

The current backend test file is `backend/tests/test_rag_contract.py`. It covers:

- Retrieved context being included in the RAG prompt.
- Follow-up question contextualization.
- Upload size enforcement.

Run it from the project root with the backend environment active:

```bash
python -m pytest backend/tests
```

There is currently no frontend test script and no end-to-end test suite in the repository.

## Development Commands

### Backend

```bash
python -m uvicorn backend.server:app --reload --port 8000
celery -A backend.celery_app.celery_app worker --loglevel=info
alembic -c backend/alembic.ini upgrade head
python -m pytest backend/tests
```

### Frontend

```bash
cd frontend
npm install
npm run dev
npm run build
npm run preview
```

## Current Limitations and Operational Notes

- Redis URLs are hardcoded in `backend/celery_app.py`; they are not environment-configurable yet.
- The Groq model name is hardcoded in `backend/services/llm/client.py`.
- `GROQ_API_KEY` is loaded into configuration and consumed by the LangChain Groq client through its environment integration.
- The frontend Axios client currently uses the hardcoded base URL `http://localhost:8000/api`. The Vite `/api` proxy is configured, but the Axios client does not currently use a relative `/api` base URL.
- The frontend includes `remember_me` in auth requests, but the backend schemas and JWT implementation do not use that field; token persistence is controlled by the Zustand persisted store.
- The upload check trusts the multipart content type and does not inspect PDF magic bytes.
- Uploaded files and Chroma data are local disk state and need a separate persistence/backup strategy for production.
- CORS allows every origin when `FRONTEND_URL` is unset. Set `FRONTEND_URL` explicitly outside local development.
- The application assumes the Celery worker is running; without it, documents remain in `processing` and chat input stays disabled.
- The current test suite does not cover authentication, API routes, migrations, Celery tasks, vector retrieval, frontend behavior, or browser workflows.
- Dependency versions are mostly unpinned, so production deployments should use a lockfile or constraints file.
- The migration history contains older duplicate/no-op revisions. Review it carefully before using the project against an existing database.

## Security Notes

- Never commit `backend/.env`, JWT secrets, Groq keys, database passwords, or Redis credentials.
- Use HTTPS and secure deployment-specific secret storage in production.
- Replace the development CORS fallback with an explicit allowlist.
- Restrict PostgreSQL and Redis network access.
- Store uploaded files outside publicly served directories.
- Add rate limiting, structured audit logging, and stronger file validation before exposing the API publicly.

## License

No license file is currently included in the repository.
