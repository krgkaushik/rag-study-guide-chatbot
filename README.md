# Study Guide Chatbot

A Retrieval-Augmented Generation (RAG) based study assistant that answers questions using content stored in a local vector database. The app uses a FastAPI backend, a Chroma vector database, and Gemini LLM for answer generation.

## Features

- Web-based chat interface for asking questions
- Semantic search over stored research content
- RAG pipeline combining retrieval + LLM response generation
- Uses Hugging Face embeddings and Chroma for similarity search
- Generates answers grounded in the retrieved documents

## Project Structure

```text
Rag_system/
├── main.py                 # FastAPI app and chat logic
├── Bedrock.py              # AWS Bedrock example integration
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration
├── research_chroma/        # Persisted Chroma database files
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
└── README.md
```

## Tech Stack

- Python
- FastAPI
- Jinja2 templates
- Chroma
- LangChain
- Hugging Face embeddings
- Google Gemini API
- Tailwind CSS

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Linux/macOS
venv\Scripts\activate      # On Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables:

Create a `.env` file in the project root and add:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

4. Run the app:

```bash
uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## How It Works

1. The user submits a question through the frontend chat UI.
2. The app queries the Chroma vector database for relevant document chunks.
3. The retrieved context is passed into a Gemini prompt.
4. Gemini answers using only the supplied context, reducing hallucinations and grounding responses in the stored research material.

## API Endpoint

### POST /api/chat

Request body:

```json
{
  "message": "What is the main idea of this document?"
}
```

Response:

```json
{
  "response": "...answer...",
  "status": "success"
}
```

## Notes

- The project expects the vector database to already exist in `./research_chroma/content/research_chroma`.
- If the database is empty or not populated, question answering may return weak or empty results.
- The app is intended for educational/research document Q&A use cases.

## License

This project is provided as-is for educational and development purposes.
