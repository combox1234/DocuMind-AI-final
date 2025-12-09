# app/main.py — clean UTF-8 copy for your College Document System (offline-chat)
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime

# local imports (must exist)
from app.sorter import process_file, process_all_incoming
from app.db import init_db, list_files, get_conn
from app.indexer import build_index, load_index, search as faiss_search

BASE = Path(__file__).resolve().parents[1]
frontend_dir = BASE / "frontend"
frontend_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="College Document System (offline-chat)")
# serve frontend static folder at /frontend
app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/frontend/index.html")

# initialize DB (creates data/metadata.db if not present)
init_db()

# ensure incoming dir exists
INCOMING = BASE / "data" / "incoming"
INCOMING.mkdir(parents=True, exist_ok=True)

@app.post('/process_all')
def api_process_all():
    """Manually trigger processing of files placed in data/incoming."""
    process_all_incoming()
    return {'status': 'processed'}

@app.post('/build_index')
def api_build_index():
    """Build vector index from already indexed files (calls indexer)."""
    build_index()
    return {'status': 'index_built'}

class ChatRequest(BaseModel):
    message: str
    top_k: int = 5

@app.post('/chat')
def api_chat(req: ChatRequest):
    """
    Offline chat endpoint:
    - Runs semantic search on the query (requires index built)
    - Returns a grounded answer assembled from snippets in DB
    """
    q = req.message
    top_k = req.top_k

    # ensure index loaded; attempt to build if missing
    index, ids = load_index()
    if index is None:
        build_index()
        index, ids = load_index()
    if index is None:
        raise HTTPException(status_code=500, detail="Index not available. Build failed or no files indexed.")

    results = faiss_search(q, top_k=top_k)
    if not results:
        return {'answer': 'Nothing identified.'}

    conn = get_conn()
    cur = conn.cursor()
    hits = []
    for r in results:
        fid = r.get('file_id')
        score = r.get('score')
        cur.execute('SELECT filename, stored_path, department, year, snippet FROM files WHERE id = ?', (fid,))
        row = cur.fetchone()
        if not row:
            continue
        filename, stored_path, department, year, snippet = row
        hits.append({
            'file_id': fid,
            'filename': filename,
            'path': stored_path,
            'department': department,
            'year': year,
            'score': score,
            'snippet': (snippet or '')[:800]
        })
    conn.close()

    if not hits:
        return {'answer': 'Nothing identified.'}

    # Build a simple grounded reply
    lines = []
    lines.append(f"I found {len(hits)} relevant document(s). Top results:")
    for i, h in enumerate(hits, start=1):
        lines.append(f"{i}. {h['filename']} — {h['department']} / {h['year']} (score {h['score']:.3f})")
    lines.append("\nSnippets (from the matched documents):")
    for i, h in enumerate(hits, start=1):
        snippet = (h['snippet'] or '').strip().replace('\n', ' ')
        if len(snippet) > 300:
            snippet = snippet[:300].rsplit(' ', 1)[0] + '...'
        lines.append(f"{i}. {snippet}")
    lines.append("\nIf you want the actual file, use the 'Files' section to download it. If nothing matches, try a simpler query (e.g. '2023 computer engineering marks').")

    answer = "\n".join(lines)
    return {'answer': answer, 'hits': hits}

# Optional: files listing & download endpoints (kept minimal)
@app.get('/files')
def api_list_files(limit: int = 50):
    rows = list_files(limit)
    return {'files': [dict(id=r[0], filename=r[1], path=r[2], department=r[3], year=r[4], file_type=r[5], created_at=r[6]) for r in rows]}

@app.get('/download/{file_id}')
def download(file_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT stored_path, filename FROM files WHERE id = ?', (file_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return JSONResponse({'error': 'not found'}, status_code=404)
    path, fname = row
    p = Path(path)
    if not p.exists():
        return JSONResponse({'error': 'file missing'}, status_code=404)
    # send file directly
    return FileResponse(p, filename=fname)
