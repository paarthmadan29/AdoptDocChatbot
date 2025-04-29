import json, re, pathlib, pickle, faiss, tiktoken
from tqdm import tqdm
import numpy as np
from openai import OpenAI

client = OpenAI()

DATA_PATH   = pathlib.Path("src/data/data.json")
OUT_INDEX   = pathlib.Path("src/index/faiss.index")
OUT_META    = pathlib.Path("src/index/meta.pkl")
CHUNK_TOKS  = 512
OVERLAP     = 64
MODEL_NAME = "text-embedding-3-large"

docs = json.loads(DATA_PATH.read_text())

def clean(text: str) -> str:
    trash = [
        r"Jump to Content.*?Start typing to search…",   # nav bar
        r"Updated about \d+ .*?ago",                    # footer stamps
    ]
    for pat in trash:
        text = re.sub(pat, "", text, flags=re.S)
    return re.sub(r"\s+", " ", text).strip()

docs = {url: clean(md) for url, md in docs.items()}

enc = tiktoken.encoding_for_model("gpt-3.5-turbo")     # fast, local

def split_to_chunks(text: str):
    tokens = enc.encode(text)
    for i in range(0, len(tokens), CHUNK_TOKS - OVERLAP):
        yield enc.decode(tokens[i : i + CHUNK_TOKS])

chunks, metas = [], []
for url, md in docs.items():
    for chunk in split_to_chunks(md):
        metas.append({"url": url, "text": chunk})
        chunks.append(chunk)

print(f"Prepared {len(chunks)} chunks from {len(docs)} pages")

def embed(batch):
    return [client.embeddings.create(input=b, model=MODEL_NAME).data[0].embedding for b in batch]
    
BATCH = 64
vecs = []
for i in tqdm(range(0, len(chunks), BATCH), desc="embedding"):
    vecs.extend(embed(chunks[i : i + BATCH]))
vecs_np = np.vstack(vecs)
dim = vecs_np.shape[1]

index = faiss.IndexFlatIP(dim)        # cosine-ready because we normalise
index.add(vecs_np)
faiss.write_index(index, str(OUT_INDEX))
pickle.dump(metas, OUT_META.open("wb"))
print(f"Saved FAISS index ({index.ntotal} vectors) + metadata")
pickle.dump(metas, OUT_META.open("wb"))