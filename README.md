# Doclify

Doclify is a FastAPI, React, PostgreSQL, Chroma, LangGraph, and Groq PDF chat application. A chat can contain multiple PDFs, and each submission may contain a message, PDFs, or both.

## Requirements

- Python 3.13+
- Node.js 20+
- PostgreSQL
- Redis
- A Groq API key

## Backend setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set the values in `backend/.env`. Never commit `.env` or put user API keys in the database.

Apply migrations and start the API:

```powershell
alembic upgrade head
uvicorn backend.server:app --reload
```

In another terminal, from the repository root, start the worker:

```powershell
celery -A backend.celery_app worker --loglevel=info --pool=solo
```

## Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The New Chat action creates an empty chat. Inside a chat, attach one or more PDFs, type a message, or submit both together.

## RAG behavior

PDFs are loaded with `PyPDFLoader`, split into overlapping chunks, embedded with `all-MiniLM-L6-v2`, and stored in the persistent repository-level `chroma_data` collection. Retrieval is filtered by chat id. Follow-up questions are contextualized from recent PostgreSQL chat history before retrieval.

The upload limit defaults to 20 MiB and can be changed with `MAX_UPLOAD_SIZE`. Failed ingestion is reflected in each document's status and error message.