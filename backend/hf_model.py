import os
import requests
import json

HF_API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-1.5B-Instruct"
HF_HEADERS = {}

def init_hf():
    """Optionally read HF token from env; works without token but slower."""
    token = os.environ.get("HF_API_TOKEN") or os.environ.get("HF_TOKEN")
    if token:
        HF_HEADERS["Authorization"] = f"Bearer {token}"
    HF_HEADERS["Content-Type"] = "application/json"

def hf_socratic(prompt: str, max_new_tokens: int = 48) -> str:
    """Call the free HF Inference API (text-generation) with a constrained prompt."""
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": 0.2,
            "top_p": 0.9,
            "repetition_penalty": 1.08,
            "return_full_text": False,
            "do_sample": True
        }
    }
    try:
        r = requests.post(HF_API_URL, headers=HF_HEADERS, data=json.dumps(payload), timeout=30)
        r.raise_for_status()
        data = r.json()
        # HF returns list or dict depending on backend
        if isinstance(data, list) and data and "generated_text" in data[0]:
            text = data[0]["generated_text"]
        elif isinstance(data, dict) and "generated_text" in data:
            text = data["generated_text"]
        else:
            # TGI-style
            text = data[0]["generated_text"] if isinstance(data, list) and data else ""
        # Keep only first question
        if "?" in text:
            text = text.split("?")[0].strip() + "?"
        return text.strip()
    except Exception:
        return "What specific molecule or checkpoint is involved?"
