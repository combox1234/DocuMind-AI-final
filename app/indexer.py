import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from pathlib import Path
import pickle
from app.db import get_conn

BASE = Path(__file__).resolve().parents[1]
MODELPATH = BASE / 'models' / 'all-MiniLM-L6-v2'
INDEX_PATH = BASE / 'data' / 'faiss.index'
MAPPING_PATH = BASE / 'data' / 'faiss_mapping.pkl'

# load model: user must download model into models/ folder for offline use
model = SentenceTransformer(str(MODELPATH))

def build_index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, snippet FROM files')
    rows = cur.fetchall()
    conn.close()
    texts = []
    ids = []
    for r in rows:
        fid, snippet = r
        if snippet:
            texts.append(snippet)
            ids.append(fid)

    if not texts:
        print('no texts to index')
        return

    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    faiss.write_index(index, str(INDEX_PATH))
    with open(MAPPING_PATH, 'wb') as f:
        pickle.dump({'ids': ids}, f)
    print('index built')

def load_index():
    if not INDEX_PATH.exists():
        return None, None
    index = faiss.read_index(str(INDEX_PATH))
    with open(MAPPING_PATH, 'rb') as f:
        m = pickle.load(f)
    return index, m['ids']

def search(query, top_k=5):
    index, ids = load_index()
    if index is None:
        return []
    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0: continue
        file_id = ids[idx]
        results.append({'file_id': int(file_id), 'score': float(score)})
    return results
