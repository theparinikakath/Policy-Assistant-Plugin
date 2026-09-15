import os
from dotenv import load_dotenv

load_dotenv()

# ---- Embedding model ----
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# sentence-transformers/all-MiniLM-L6-v2

# ---- Vector DB settings ----
VECTOR_DB_PATH = "qdrant_db"
COLLECTION_NAME = "dpw_policies"

# ---- Chunking settings ----
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# ---- LLM settings ----
GEMINI_MODEL_NAME = "gemini-3.6-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---- Retrieval settings ----
TOP_K = 3

# ---- Folders ----
DOCS_FOLDER = "policy_docs"
