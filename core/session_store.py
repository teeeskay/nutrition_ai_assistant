import json
from pathlib import Path

SESSION_PATH = Path("data/session_store.json")

def load_session():
    if SESSION_PATH.exists():
        return json.loads(SESSION_PATH.read_text())
    return {}

def save_session(data):
    SESSION_PATH.write_text(json.dumps(data, indent=2))
