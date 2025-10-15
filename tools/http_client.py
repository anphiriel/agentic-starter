import requests
from typing import Dict, Any

def post(url: str, json: Dict[str, Any]) -> Dict[str, Any]:
    resp = requests.post(url, json=json, timeout=10)
    return {"status_code": resp.status_code, "json": safe_json(resp)}

def get(url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    resp = requests.get(url, params=params or {}, timeout=10)
    return {"status_code": resp.status_code, "json": safe_json(resp)}

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {"text": resp.text}