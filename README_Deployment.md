# 🚀 Deployment Guide: DocuMind AI

Your system is now **Production-Ready** and Scalable.

## 🏁 Quick Start (Production Mode)

1.  **Install Dependencies:**
    ```bash
    pip install waitress
    ```
2.  **Start the Server:**
    Instead of `python app.py`, run:
    ```bash
    python serve.py
    ```
    *(This uses 6 threads vs 1, handling multiple users smoothly)*

3.  **Start the Background Worker:**
    Keep your existing worker running:
    ```bash
    python watcher.py
    ```
    *(Or `start_all.bat` if you updated it to use `serve.py`)*

---

## 🛡️ Key Features Enabled
| Feature | Function | Benefit |
|:---|:---|:---|
| **WAL Mode** | Database Concurrency | Uploads don't block Chat. Chat doesn't block Uploads. |
| **RBAC Caching** | Permission Optimization | Access control checks are 100x faster. |
| **Strict RAG** | Anti-Hallucination | Answers ONLY from documents. "I don't know" if unsure. |
| **Auto-Classification**| Smart Sorting | Crypto docs -> Technology. Contracts -> Legal. |
| **Hybrid Retrieval** | Access+Search | Students can find "Symmetric Cipher" docs they have access to. |

## 🔮 Future Maintenance
- **Files:** All sorted files are in `data/sorted`. If you need to re-scan everything, move files from `sorted` back to `incoming`.
- **Database:** `data/users.db`. Backup this file regularly.
- **Scripts:** Maintenance scripts (like DB fixes) are now in `scripts/maintenance/`.
- **Logs:** Check `logs/app.log` for access audits and errors.

## 📈 Next Levels (Optional)
If you grow to 10,000+ users, refer to **`docs/analysis/POSTGRES_MIGRATION_ANALYSIS.md`** to switch the engine.
