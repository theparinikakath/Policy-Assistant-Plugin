import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

DOCS_FOLDER = "policy_docs"
QDRANT_PATH = "qdrant_db"
COLLECTION_NAME = "dpw_policies"

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
    vector_size = model.get_sentence_embedding_dimension()

    # local, file-based Qdrant (no server needed to run separately)
    client = QdrantClient(path=QDRANT_PATH)

    # recreate collection fresh each time we re-run ingestion
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )

    print("Embedding + storing chunks...")
    points = []
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk.page_content).tolist()
        points.append(
            PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "text": chunk.page_content,
                    "source": os.path.basename(chunk.metadata.get("source", "unknown"))
                }
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)

    print("Done! Vector store ready.")

if __name__ == "__main__":
    build_vector_store()