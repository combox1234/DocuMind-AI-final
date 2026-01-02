# Testing Guide: Redis & Celery Integration

> [!IMPORTANT]
> **Redis Server Missing**: The system check shows that **Redis is NOT running** on your computer (`localhost:6379`). You must start it before the new updates will work.

## Step 1: Start Redis Server (Required)
Since you are on Windows, you have two easy options:

### Option A: Use Memurai (Native Windows Redis) - **Recommended**
1.  Download **Memurai Developer (Free)** from [memurai.com](https://www.memurai.com/get-memurai).
2.  Install it. It usually starts automatically as a Windows Service.
3.  Verify: Open a terminal and run `.\venv\Scripts\python -c "import redis; print(redis.Redis(host='localhost').ping())"` -> Should print `True`.

### Option B: Use WSL (Linux Subsystem)
1.  Open Ubuntu/WSL terminal.
2.  Run: `sudo apt install redis-server`
3.  Run: `sudo service redis-server start`

---

## Step 2: Start the Worker (The "Librarian")
Open a **new terminal** in your project folder and run:
```powershell
.\venv\Scripts\celery -A worker.celery_app worker --pool=solo -l info
```
*Note: Keep this terminal open. You should see logs like `[tasks] . worker.process_file_task`.*

---

## Step 3: Start the Watcher (The "Inbox")
Open a **second new terminal** in your project folder and run:
```powershell
.\venv\Scripts\python watcher.py
```
*Note: It should say "Async Watcher Started".*

---

## Step 4: Perform the Test
1.  Copy a PDF or Text file into `data/incoming/`.
2.  **Check Watcher Terminal**: It should instantly say `Queued file: ...`.
3.  **Check Worker Terminal**: It should scroll logs saying `Picking up task` -> `Processing` -> `Move to Sorted`.
4.  If successful, the file will move to `data/sorted/DOMAIN/CATEGORY/...`.
