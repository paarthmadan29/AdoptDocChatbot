import os, pickle, pathlib, json, numpy as np, faiss, uvicorn
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import tiktoken

from prompts import ctx_prompt
from utils import extract_json
EMBED_MODEL   = "text-embedding-3-large"
CHAT_MODEL    = "gpt-4.1-nano-2025-04-14"
TOP_K         = 4
TEMPERATURE   = 0.1
INDEX_PATH    = pathlib.Path("index/faiss.index")
META_PATH     = pathlib.Path("index/meta.pkl")

INDEX = faiss.read_index(str(INDEX_PATH))
META  = pickle.load(META_PATH.open("rb"))

client = OpenAI()                         
enc    = tiktoken.encoding_for_model("gpt-3.5-turbo")

def embed_query(text: str) -> np.ndarray:
    """OpenAI embedding → L2-normalised float32 vector."""
    resp = client.embeddings.create(model=EMBED_MODEL, input=[text])
    vec  = np.array(resp.data[0].embedding, dtype="float32")
    return vec / np.linalg.norm(vec)

def retrieve(q_embed: np.ndarray, k: int = TOP_K):
    D, I = INDEX.search(q_embed[None, :], k)
    return [META[i] for i in I[0]]

def build_prompt(question: str, contexts: List[dict]) -> str:
    ctx_blocks = []
    for idx, c in enumerate(contexts, 1):
        # hard truncate long chunks to ~300 tokens so the prompt stays small
        text_tokens = enc.encode(c["text"])
        ctx_text = enc.decode(text_tokens[:300])
        ctx_blocks.append(f"[{idx}] {ctx_text}\nSOURCE: {c['url']}")
    ctx_section = "\n\n".join(ctx_blocks)
    return ctx_prompt(ctx_section, question)

class Query(BaseModel):
    query: str
    top_k: int | None = None

app = FastAPI()

@app.post("/chat")
def chat(body: Query):
    k     = body.top_k or TOP_K
    q_vec = embed_query(body.query)
    ctx   = retrieve(q_vec, k)

    prompt = build_prompt(body.query, ctx)

    completion = client.chat.completions.create(
        model       = CHAT_MODEL,
        messages    = [{"role": "user", "content": prompt}],
        temperature = TEMPERATURE,
    )

    response = completion.choices[0].message.content
    json_response = json.loads(extract_json(response))
    print(json_response['sources'])
    return {
        "answer"  : json_response['answer'],
        "sources" : json_response['sources'],# [c["url"] for c in ctx],
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
