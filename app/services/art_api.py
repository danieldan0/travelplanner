import requests
from fastapi import HTTPException
import time

_CACHE: dict[int, tuple[float, dict]] = {}
_TTL_SECONDS = 300

def validate_artwork(external_id: int) -> dict:
    now = time.time()
    cached = _CACHE.get(external_id)
    if cached and (now - cached[0]) < _TTL_SECONDS:
        return cached[1]

    url = f"https://api.artic.edu/api/v1/artworks/{external_id}"
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Place not found in external API")

    data = r.json()["data"]
    _CACHE[external_id] = (now, data)
    return data