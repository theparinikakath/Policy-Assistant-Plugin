import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import config
import vector_store


def load_documents():
    docs = []
    for filename in os.listdir(config.DOCS_FOLDER):
        path = os.path.join(config.DOCS_FOLDER, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(path)
            docs.extend(loader.load())
        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(path)
            docs.extend(loader.load())
    return docs


def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    return splitter.split_documents(docs)


def build_vector_store():
    print("Loading documents...")
    docs = load_documents()
    print(f"{len(docs)} pages loaded")

    print("Chunking...")
    chunks = chunk_documents(docs)
    print(f"{len(chunks)} chunks created")

    print("Loading embedding model...")
    model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
    vector_size = model.get_embedding_dimension()

    vector_store.recreate_collection(vector_size)

    print("Embedding + storing chunks...")
    chunks_with_embeddings = []
    for chunk in chunks:
        embedding = model.encode(chunk.page_content).tolist()
        source = os.path.basename(chunk.metadata.get("source", "unknown"))
        chunks_with_embeddings.append((chunk.page_content, source, embedding))

    vector_store.store_chunks(chunks_with_embeddings)

    print("Done! Vector store ready.")


if __name__ == "__main__":
    build_vector_store()
    