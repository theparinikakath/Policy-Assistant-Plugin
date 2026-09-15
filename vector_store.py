from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import config

_client = None

def get_client():
    global _client
    if _client is None:
        _client = QdrantClient(path=config.VECTOR_DB_PATH)
    return _client


def recreate_collection(vector_size: int):
    client = get_client()
    if client.collection_exists(config.COLLECTION_NAME):
        client.delete_collection(config.COLLECTION_NAME)
    client.create_collection(
        collection_name=config.COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )


def store_chunks(chunks_with_embeddings):
    """chunks_with_embeddings: list of (text, source, embedding)"""
    client = get_client()
    points = [
        PointStruct(
            id=i,
            vector=embedding,
            payload={"text": text, "source": source}
        )
        for i, (text, source, embedding) in enumerate(chunks_with_embeddings)
    ]
    client.upsert(collection_name=config.COLLECTION_NAME, points=points)


def search(query_embedding, top_k: int):
    client = get_client()
    results = client.query_points(
        collection_name=config.COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    ).points
    docs = [point.payload["text"] for point in results]
    sources = [point.payload["source"] for point in results]
    return docs, sources
