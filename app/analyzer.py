import re
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-r1"

SYSTEM_PROMPT = """
You are a compassionate mental health assistant. Your job is to analyze journal entries and return:
- a gentle one-sentence summary
- primary emotions (max 3)
- cognitive distortions (max 3, e.g. catastrophizing, self-blame)
- core themes (max 3, like work stress, relationships, personal growth)
Respond ONLY in raw JSON with keys: summary, emotions, patterns, themes. Do NOT include explanations or markdown.
"""

def analyze_entry(text):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    raw_output = response.json()["message"]["content"]

    think_block = re.search(r"<think>(.*?)</think>", raw_output, re.DOTALL)
    ai_thoughts = think_block.group(1).strip() if think_block else None
    cleaned = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL).strip()

    try:
        json_block = re.search(r"{.*?}", cleaned, re.DOTALL).group(0)
        analysis = json.loads(json_block)
        return {
            "summary": analysis["summary"],
            "emotions": analysis["emotions"],
            "patterns": analysis["patterns"],
            "themes": analysis["themes"],
            "ai_thoughts": ai_thoughts,
            "raw_output": raw_output
        }
    except:
        return {
            "summary": "Could not parse summary.",
            "emotions": [],
            "patterns": [],
            "themes": [],
            "ai_thoughts": ai_thoughts,
            "raw_output": raw_output
        }
