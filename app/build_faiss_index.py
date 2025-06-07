# app/build_faiss_index.py

import os
import json
from tqdm import tqdm
import pickle

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

RAG_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data", "rag")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def build_index_for_file(rag_path):
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    base_filename = os.path.splitext(os.path.basename(rag_path))[0]
    out_folder = os.path.join(RAG_FOLDER, base_filename)

    os.makedirs(out_folder, exist_ok=True)

    # Load RAG data
    docs = []
    with open(rag_path, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            text = entry["content"]
            metadata = entry.get("metadata", {})
            docs.append(Document(page_content=text, metadata=metadata))

    if not docs:
        print(f"⚠️ No entries in {rag_path}")
        return

    # Build FAISS vector store and save it
    db = FAISS.from_documents(docs, embedding_model)
    db.save_local(out_folder)
    print(f"✅ FAISS index saved to: {out_folder}")

def build_all_indexes():
    for file in os.listdir(RAG_FOLDER):
        if file.endswith(".jsonl"):
            rag_path = os.path.join(RAG_FOLDER, file)
            build_index_for_file(rag_path)

if __name__ == "__main__":
    build_all_indexes()