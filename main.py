import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types
from langchain_chroma import Chroma

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Study Guide Chatbot")

# Templates and static files
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(static_dir)),
        name="static",
    )

# Gemini configuration
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=api_key)


class GeminiEmbeddings:
    """Generate embeddings through Google's API."""

    def embed_documents(self, texts):
        if not texts:
            return []

        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
            config=types.EmbedContentConfig(
                # Match the vector dimension already stored in the local
                # Chroma collection to avoid collection mismatch errors.
                output_dimensionality=384,
            ),
        )
        return [item.values for item in result.embeddings]

    def embed_query(self, text):
        return self.embed_documents([text])[0]


# IMPORTANT:
# This database must contain vectors generated using the same
# Gemini embedding model and dimensionality.
db_path = BASE_DIR / "research_chroma" / "content" / "research_chroma"

embedding_model = GeminiEmbeddings()

vector_db = Chroma(
    persist_directory=str(db_path),
    embedding_function=embedding_model,
)


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    user_query = request.message.strip()

    if not user_query:
        return {
            "response": "Please enter a question.",
            "status": "error",
        }

    try:
        results = vector_db.similarity_search(user_query, k=5)

        if not results:
            return {
                "response": (
                    "I could not find this information "
                    "in the provided documents."
                ),
                "status": "success",
            }

        context = "\n\n".join(
            document.page_content for document in results
        )

        prompt = f"""
You are a helpful educational research assistant.

Answer the question using ONLY the supplied context.
Explain concepts clearly and use examples when available.
Never invent facts or assume information not in the context.

If the answer is not in the context, say:
"I could not find this information in the provided documents."

Context:
{context}

Question:
{user_query}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=1000,
                temperature=0.3,
            ),
        )

        return {
            "response": response.text
            or "No response was generated. Please try again.",
            "status": "success",
        }

    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return {
            "response": (
                "An error occurred while processing your question. "
                "Please try again."
            ),
            "status": "error",
        }