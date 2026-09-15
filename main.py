from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from google import genai
import config
import vector_store

app = FastAPI(title="Policy Assistant Chatbot")

embed_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
client = genai.Client(api_key=config.GEMINI_API_KEY)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "Policy Assistant Chatbot is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


def retrieve_chunks(question: str):
    query_embedding = embed_model.encode(question).tolist()
    return vector_store.search(query_embedding, top_k=config.TOP_K)


def generate_answer(question: str, context_chunks: list):
    context_text = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are a DPW Policy Assistant. Answer the employee's question ONLY using the policy content provided below. If the answer is not present in the provided content, say clearly that you don't have that information and suggest they contact the IT/Security team. Do not make up policy details. Keep answers concise and professional.

Policy content:
{context_text}

Employee question: {question}

Answer based only on the policy content above."""

    response = client.models.generate_content(
        model=config.GEMINI_MODEL_NAME,
        contents=prompt
    )
    return response.text


@app.post("/api/chat")
def chat(request: ChatRequest):
    question = request.question
    chunks, sources = retrieve_chunks(question)

    if not chunks:
        return {
            "question": question,
            "answer": "I don't have policy information on this topic yet. Please contact the IT/Security team.",
            "sources": []
        }

    answer = generate_answer(question, chunks)
    source_files = list(set(sources))

    return {
        "question": question,
        "answer": answer,
        "sources": source_files
    }
