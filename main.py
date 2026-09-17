
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import os
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from google import genai


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(title="Study Guide Chatbot")


# ============================================================
# Templates and Static Files
# ============================================================

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ============================================================
# Google Gemini API
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set."
    )

client = genai.Client(api_key=api_key)


# ============================================================
# Chroma Vector Database
# ============================================================

db_path = "./research_chroma/content/research_chroma"


# Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Load Chroma database
vector_db = Chroma(
    persist_directory=db_path,
    embedding_function=embedding_model
)


# ============================================================
# Request Model
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# Home Page
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the frontend chat interface.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ============================================================
# Chat API
# ============================================================

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Handle user messages and return AI responses.
    """

    user_query = request.message.strip()

    if not user_query:
        return {
            "response": "Please enter a question.",
            "status": "error"
        }

    try:

        # ----------------------------------------------------
        # 1. Search Chroma database
        # ----------------------------------------------------

        results = vector_db.similarity_search(
            user_query,
            k=3
        )


        # ----------------------------------------------------
        # 2. Create context
        # ----------------------------------------------------

        context = "\n\n".join(
            result.page_content
            for result in results
        )


        # ----------------------------------------------------
        # 3. Create prompt
        # ----------------------------------------------------

        prompt = f"""
You are a helpful research assistant.

Answer the user's question using ONLY the information
provided in the context below.

If the answer is not present in the context, say:

"I could not find this information in the provided documents."

Do not make up information.

Context:
{context}

Question:
{user_query}
"""


        # ----------------------------------------------------
        # 4. Ask Gemini
        # ----------------------------------------------------

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        # ----------------------------------------------------
        # 5. Return response
        # ----------------------------------------------------

        return {
            "response": response.text,
            "status": "success"
        }


    except Exception as e:

        print("ERROR:", str(e))

        return {
            "response": "An error occurred while processing your question.",
            "status": "error"
        }
