import json
import os
from datetime import datetime, timedelta

CACHE_DIR = "data"
CACHE_EXPIRY_HOURS = 24

def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")

def _is_expired(filepath: str) -> bool:
    if not os.path.exists(filepath):
        return True
    modified = datetime.fromtimestamp(os.path.getmtime(filepath))
    return datetime.now() - modified > timedelta(hours=CACHE_EXPIRY_HOURS)

def get_cached(key: str):
    filepath = _cache_path(key)
    if _is_expired(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)

def set_cached(key: str, data) -> None:
    filepath = _cache_path(key)
    with open(filepath, "w") as f:
        json.dump(data, f)

def cached_call(key: str, func, *args, **kwargs):
    data = get_cached(key)
    if data is not None:
        print(f"[cache] Serving '{key}' from disk")
        return data
    print(f"[cache] Fetching '{key}' fresh")
    data = func(*args, **kwargs)
    set_cached(key, data)
    return data
