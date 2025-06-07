import json
import os
from datetime import datetime



DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "journal_entries.jsonl")

def save_entry(text, analysis, db_path=DB_PATH):
    entry = {
        "text": text,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat()
    }

    # Save to main journal file
    with open(db_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"✅ Entry saved at {entry['timestamp']}")

    # Save RAG entry to /data/rag/
    rag_folder = os.path.join(os.path.dirname(db_path), "rag")
    os.makedirs(rag_folder, exist_ok=True)

    rag_path = os.path.join(rag_folder, f"rag_{os.path.basename(db_path)}")

    rag_doc = {
        "content": text,
        "metadata": {
            "timestamp": entry["timestamp"],
            "themes": analysis.get("themes", []),
            "emotions": analysis.get("emotions", [])
        }
    }

    with open(rag_path, "a") as f:
        f.write(json.dumps(rag_doc) + "\n")
    print(f"🧠 Appended to RAG file: {rag_path}")


def load_entries():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        return [json.loads(line.strip()) for line in f.readlines()]
