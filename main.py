import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import FastAPI
from langchain_chroma import Chroma

app = FastAPI(title="Study Guide Chatbot")
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)


class GeminiEmbeddings:
    """Generate embeddings using Google's API instead of local PyTorch."""

    def embed_documents(self, texts):
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
            config=types.EmbedContentConfig(
                output_dimensionality=768
            ),
        )
        return [item.values for item in result.embeddings]

    def embed_query(self, text):
        return self.embed_documents([text])[0]


embedding_model = GeminiEmbeddings()

vector_db = Chroma(
    persist_directory="./research_chroma/content/research_chroma",
    embedding_function=embedding_model,
)