# app/llm.py
import requests
import re

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-r1"

def strip_think_tags(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def get_deepseek_response(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    try:
        res = requests.post(OLLAMA_URL, json=payload)
        full_reply = res.json()["message"]["content"]
        return strip_think_tags(full_reply).strip()
    except Exception as e:
        return f"❌ LLM error: {e}"