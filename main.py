
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
from google.genai import types

load_dotenv()

app = FastAPI(title="Study Guide Chatbot")

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=api_key)

db_path = "./research_chroma/content/research_chroma"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = Chroma(
    persist_directory=db_path,
    embedding_function=embedding_model
)

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):

    user_query = request.message.strip()

    if not user_query:
        return {
            "response": "Please enter a question.",
            "status": "error"
        }

    try:
        results = vector_db.similarity_search(
            user_query,
            k=5
        )

        context = "\n\n".join(
            result.page_content
            for result in results
        )

        prompt = f"""
You are a helpful and detailed educational research assistant.

Answer the user's question using ONLY the information provided
in the context below.

Give a detailed and complete answer.
Do not give an unnecessarily short answer.
Explain concepts clearly and step by step when appropriate.
If the question asks "why", explain the reasoning.
If the question asks "how", explain the process step by step.
If the question asks for a definition, provide the definition
and explain it in simple language.
Include relevant examples from the context when available.
Use headings, bullet points, and numbered lists when useful.
For simple questions, keep the answer reasonably concise.
For complex questions, provide a detailed explanation.
Do not repeat information unnecessarily.
Do not use information that is not present in the context.
Never invent or assume information.

If the answer cannot be found in the context, say:

"I could not find this information in the provided documents."

Make the answer easy for a student to understand.

Context:
{context}

Question:
{user_query}

Provide the most complete educational answer possible based
strictly on the provided context.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=1000,
                temperature=0.7
            )
        )

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
