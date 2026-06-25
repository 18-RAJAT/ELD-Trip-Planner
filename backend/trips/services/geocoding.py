import re

import requests
from django.conf import settings

from .errors import GeocodingError

VAGUE_TERMS = {
    "usa",
    "us",
    "u s",
    "u s a",
    "united states",
    "united states of america",
    "america",
    "uk",
    "u k",
    "united kingdom",
    "great britain",
    "britain",
    "england",
    "scotland",
    "wales",
    "canada",
    "mexico",
    "europe",
    "asia",
    "africa",
    "australia",
}


def _normalize_query(query):
    return re.sub(r"[^a-z0-9\s]", " ", query.strip().lower()).strip()


def _is_vague_location(query):
    normalized = _normalize_query(query)
    if not normalized or len(normalized) < 3:
        return True
    if normalized in VAGUE_TERMS:
        return True
    parts = [part.strip() for part in query.split(",") if part.strip()]
    if len(parts) == 1 and _normalize_query(parts[0]) in VAGUE_TERMS:
        return True
    return False


def _request_search(query, limit):
    url = f"{settings.NOMINATIM_BASE_URL}/search"
    params = {"q": query, "format": "json", "limit": limit, "addressdetails": 1}
    if settings.GEOCODER_COUNTRY_CODES:
        params["countrycodes"] = settings.GEOCODER_COUNTRY_CODES
    headers = {"User-Agent": settings.GEOCODER_USER_AGENT}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GeocodingError("Unable to reach the geocoding service.") from exc
    return response.json()


def search_locations(query, limit=5):
    if not query or len(query.strip()) < 2:
        return []
    results = _request_search(query.strip(), limit)
    return [
        {
            "label": item.get("display_name", query),
            "lat": float(item["lat"]),
            "lng": float(item["lon"]),
        }
        for item in results
    ]


def geocode(query):
    if _is_vague_location(query):
        raise GeocodingError(
            f"'{query}' is too vague. Use a specific city and state, such as Dallas, TX, USA."
        )
    results = _request_search(query, 1)
    if not results:
        raise GeocodingError(
            f"Could not find a US location for '{query}'. Try City, ST, USA."
        )
    top = results[0]
    return {
        "label": top.get("display_name", query),
        "lat": float(top["lat"]),
        "lng": float(top["lon"]),
    }


def resolve_location(location):
    lat = location.get("lat")
    lng = location.get("lng")
    query = location["query"]
    if lat is not None and lng is not None:
        return {"label": location.get("label") or query, "lat": float(lat), "lng": float(lng)}
    return geocode(query)