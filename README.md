# AdoptDocChatbot

A simple document-based QnA chatbot using LLMs and RAG (Retrieval-Augmented Generation).

## How to Run

### 1. Direct LLM Context Method (`app.py`)
This runs a Streamlit app where the full documentation (`data.json`) is directly provided to the LLM.

```bash
streamlit run app.py
```

- Initialize the bot from the sidebar after launching.
- Ask your questions directly.

### 2. RAG-based Method (`app_rag.py` + `st_app.py`)
This uses embeddings + FAISS index for retrieval before querying the LLM.

**Step 1:** Start the FastAPI server
```bash
python app_rag.py
```
This runs a server at http://localhost:8000/chat.

**Step 2:** Start the Streamlit frontend
```bash
streamlit run st_app.py
```
- Ask questions through the UI.
- Answers are retrieved using vector search over document chunks.

## Requirements
- Python 3.9+

Install dependencies:
```bash
pip install streamlit fastapi uvicorn faiss-cpu openai tiktoken requests pydantic numpy
```

Make sure you have:
- `OPENAI_API_KEY` set in your environment.
- Prebuilt FAISS index and metadata under `src/index/`.
