import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

DOCS_FOLDER = "policy_docs"
CHROMA_PATH = "chroma_db"

def load_documents():
    docs = []
    for filename in os.listdir(DOCS_FOLDER):
        path = os.path.join(DOCS_FOLDER, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(path)
            docs.extend(loader.load())
        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(path)
            docs.extend(loader.load())
    return docs

def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    return splitter.split_documents(docs)

def build_vector_store():
    print("Loading documents...")
    docs = load_documents()
    print(f"{len(docs)} pages loaded")

    print("Chunking...")
    chunks = chunk_documents(docs)
    print(f"{len(chunks)} chunks created")

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(name="dpw_policies")
    except Exception:
        pass
    collection = client.create_collection(name="dpw_policies")

    print("Embedding + storing chunks...")
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk.page_content).tolist()
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[embedding],
            documents=[chunk.page_content],
            metadatas=[{"source": os.path.basename(chunk.metadata.get("source", "unknown"))}]
        )

    print("Done! Vector store ready.")

if __name__ == "__main__":
    build_vector_store()