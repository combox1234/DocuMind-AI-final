
import os
import shutil
from pathlib import Path

# Paths
ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = ROOT / "scripts" / "maintenance"
DOCS_DIR = ROOT / "docs" / "analysis"
ARCHIVE_DIR = ROOT / "archive"
LOGS_DIR = ROOT / "logs"

# Ensure dirs exist
for d in [SCRIPTS_DIR, DOCS_DIR, ARCHIVE_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Define Moves
moves = {
    "scripts": {
        "dest": SCRIPTS_DIR,
        "files": [
            "add_test_user.py", "fix_admin_permission.py", "fix_admin_wildcard.py",
            "fix_delete_incoming.py", "fix_delete_search.py", "fix_file_display.py",
            "fix_indent.py", "fix_path_sep.py", "fix_permissions_syntax.py",
            "fix_rbac_domain.py", "fix_syntax.py", "fix_users_db.py",
            "generate_test_files.py", "init_db.py", "inspect_chunks.py",
            "inspect_databases.py", "manual_fix_delete.py", "rebuild_db.py",
            "test_enhancements.py", "test_permissions_quick.py", "test_retrieval.py",
            "update_list_files.py", "update_ui_columns.py", "verify_fix.py",
            "verify_index.py", "verify_pipeline.py"
        ]
    },
    "docs": {
        "dest": DOCS_DIR,
        "files": [
            "CHAT_FIX_TESTING.md", "DEBUG_UPLOAD_BUTTONS.md", "POSTGRES_MIGRATION_ANALYSIS.md",
            "TESTING_RECENT_CHANGES.md", "TEST_USER_PERMISSIONS.md", "UPLOAD_DELETE_TESTING.md",
            "auth_method.txt", "quota_endpoint.txt", "run.md", "TEST_QUESTIONS.txt", "response.txt"
        ]
    },
    "archive": {
        "dest": ARCHIVE_DIR,
        "files": ["modal_functions.js", "upload_functions.js", "upload_modals.html"]
    },
    "logs": {
        "dest": LOGS_DIR,
        "files": ["app.log"]
    }
}

print("Starting Cleanup...")

for category, data in moves.items():
    dest = data["dest"]
    for filename in data["files"]:
        src = ROOT / filename
        if src.exists():
            try:
                shutil.move(str(src), str(dest / filename))
                print(f"Moved {filename} -> {dest.name}/")
            except Exception as e:
                print(f"Error moving {filename}: {e}")

print("Cleanup Complete.")
