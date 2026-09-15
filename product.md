# Policy Assistant — Product Overview

## What it is

Policy Assistant is an internal tool that lets employees ask natural-language
questions about company policies (e.g. password policy) and get answers
grounded in the organization's own policy documents — without leaving Gmail.

It has two parts:

1. **Backend (this repo's core)** — a Python RAG (Retrieval-Augmented
   Generation) service that retrieves relevant policy text and generates a
   grounded answer using an LLM.
2. **Gmail Add-on ("Apps Script plugin")** — a Google Workspace sidebar add-on
   that gives employees a chat box inside Gmail and talks to the backend.

## How it works (RAG pipeline)

1. **Ingestion** (`ingest.py`, run offline/on-demand)
   - Loads all `.pdf` and `.docx` files from `policy_docs/`.
   - Splits each document into ~800-character chunks (100-char overlap).
   - Embeds each chunk with the `all-MiniLM-L6-v2` sentence-transformer model.
   - Stores chunks + embeddings + source filename in a persistent ChromaDB
     collection named `dpw_policies` (`chroma_db/`), rebuilding it from
     scratch each run.

2. **Serving** (`main.py`, FastAPI app — "Policy Assistant Chatbot")
   - `GET /` — liveness message.
   - `GET /health` — health check.
   - `POST /api/chat` — main endpoint. Accepts `{"question": str}`.
     - Embeds the question, retrieves the top-3 nearest chunks from
       ChromaDB (`retrieve_chunks`).
     - If nothing relevant is found, returns a canned "I don't have policy
       information on this topic yet" response.
     - Otherwise builds a strict grounding prompt (answer only from the
       retrieved policy content, no hallucination, direct the user to
       IT/Security if the answer isn't known) and calls Google Gemini
       (`gemini-3.6-flash` via the `google-genai` SDK) to generate the answer.
     - Returns `{"question", "answer", "sources"}`, where `sources` lists the
       originating policy document(s).

3. **Client** (`apps-script/`)
   - `appsscript.json` — Gmail add-on manifest: OAuth scopes for
     `gmail.addons.execute` and `script.external_request`, a URL whitelist
     restricted to the backend's endpoint, branded "Policy Assistant."
   - `Code.gs`
     - `onHomepage` / `buildHomeCard` — renders a Gmail sidebar card with a
       text input and "Ask" button.
     - `askPolicy` — sends the typed question to the backend's `/api/chat`
       endpoint via `UrlFetchApp`, then renders the answer and sources in a
       new card (HTML-escaped).
     - `showErrorCard` — surfaces backend/connection errors to the user.

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector store | ChromaDB (persistent, local) |
| LLM | Google Gemini (`gemini-3.6-flash` via `google-genai`) |
| Document loading | LangChain (`PyPDFLoader`, `Docx2txtLoader`, recursive text splitter) |
| Config | `python-dotenv` (`.env` → `GEMINI_API_KEY`) |
| Client | Google Apps Script Gmail Add-on (`CardService`, `UrlFetchApp`) |
| Dev tunneling | ngrok (exposes local backend to the Gmail add-on) |

## Current project state

- **Stage:** early/demo. No pinned dependency manifest (`requirements.txt` /
  `pyproject.toml`), no automated tests, minimal written documentation.
- **Backend URL:** the add-on currently points at a temporary ngrok URL, not
  a stable production deployment.
- **Data:** only one sample policy document is present
  (`policy_docs/Password Policy sample.pdf`); the vector store and ingestion
  pipeline are designed to scale to a full policy library.

## Key files

- `main.py` — FastAPI backend / chat endpoint
- `ingest.py` — builds the ChromaDB vector store from `policy_docs/`
- `policy_docs/` — source policy documents
- `chroma_db/` — generated vector store (rebuildable artifact, gitignored)
- `apps-script/Code.gs`, `apps-script/appsscript.json` — Gmail add-on client
