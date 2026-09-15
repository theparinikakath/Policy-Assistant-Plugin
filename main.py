import os
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Policy Assistant Chatbot")

# Load embedding model + qdrant collection once at startup
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
qdrant_client = QdrantClient(path="qdrant_db")
COLLECTION_NAME = "dpw_policies"

# Configure Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "Policy Assistant Chatbot is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


def retrieve_chunks(question: str, top_k: int = 3):
    query_embedding = embed_model.encode(question).tolist()
    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    ).points

    docs = [point.payload["text"] for point in results]
    sources = [{"source": point.payload["source"]} for point in results]
    return docs, sources


def generate_answer(question: str, context_chunks: list):
    context_text = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are a DPW Policy Assistant. Answer the employee's question ONLY using the policy content provided below. If the answer is not present in the provided content, say clearly that you don't have that information and suggest they contact the IT/Security team. Do not make up policy details. Keep answers concise and professional.

Policy content:
{context_text}

Employee question: {question}

Answer based only on the policy content above."""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text


@app.post("/api/chat")
def chat(request: ChatRequest):
    question = request.question

    # Step 1: retrieve relevant policy chunks
    chunks, sources = retrieve_chunks(question, top_k=3)

    if not chunks:
        return {
            "question": question,
            "answer": "I don't have policy information on this topic yet. Please contact the IT/Security team.",
            "sources": []
        }

    # Step 2: generate grounded answer using Gemini
    answer = generate_answer(question, chunks)

    # Step 3: return answer + sources
    source_files = list(set([s.get("source", "unknown") for s in sources]))

    return {
        "question": question,
        "answer": answer,
        "sources": source_files
    }
