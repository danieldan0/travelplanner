import requests
from fastapi import HTTPException

def validate_artwork(external_id: int) -> dict:
    url = f"https://api.artic.edu/api/v1/artworks/{external_id}"
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Place not found in external API")
    return r.json()["data"]