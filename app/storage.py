import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "journal_entries.jsonl")

def save_entry(text, analysis):
    entry = {
        "text": text,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat()
    }
    with open(DB_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"✅ Entry saved at {entry['timestamp']}")


def load_entries():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        return [json.loads(line.strip()) for line in f.readlines()]
