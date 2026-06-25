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


def _allowed_countries():
    codes = settings.GEOCODER_COUNTRY_CODES
    if not codes:
        return set()
    return {code.strip().lower() for code in codes.split(",") if code.strip()}


def _search_nominatim(query, limit):
    url = f"{settings.NOMINATIM_BASE_URL}/search"
    params = {"q": query, "format": "json", "limit": limit, "addressdetails": 1}
    codes = settings.GEOCODER_COUNTRY_CODES
    if codes:
        params["countrycodes"] = codes
    headers = {"User-Agent": settings.GEOCODER_USER_AGENT}
    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    return [
        {
            "label": item.get("display_name", query),
            "lat": float(item["lat"]),
            "lng": float(item["lon"]),
        }
        for item in response.json()
    ]


def _photon_label(properties, fallback):
    parts = []
    for key in ("name", "city", "county", "state", "country"):
        value = properties.get(key)
        if value and value not in parts:
            parts.append(value)
    return ", ".join(parts) if parts else fallback


def _search_photon(query, limit):
    url = f"{settings.PHOTON_BASE_URL}/api/"
    params = {"q": query, "limit": limit, "lang": "en"}
    headers = {"User-Agent": settings.GEOCODER_USER_AGENT}
    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    allowed = _allowed_countries()
    results = []
    for feature in response.json().get("features", []):
        properties = feature.get("properties", {})
        if allowed and properties.get("countrycode", "").lower() not in allowed:
            continue
        coordinates = feature.get("geometry", {}).get("coordinates")
        if not coordinates:
            continue
        results.append(
            {
                "label": _photon_label(properties, query),
                "lat": float(coordinates[1]),
                "lng": float(coordinates[0]),
            }
        )
    return results


def _provider_search(query, limit):
    try:
        if settings.GEOCODER_PROVIDER == "nominatim":
            return _search_nominatim(query, limit)
        return _search_photon(query, limit)
    except requests.RequestException as exc:
        raise GeocodingError("Unable to reach the geocoding service.") from exc


def search_locations(query, limit=5):
    if not query or len(query.strip()) < 2:
        return []
    return _provider_search(query.strip(), limit)


def geocode(query):
    if _is_vague_location(query):
        raise GeocodingError(
            f"'{query}' is too vague. Use a specific city and state, such as Dallas, TX, USA."
        )
    results = _provider_search(query, 1)
    if not results:
        raise GeocodingError(
            f"Could not find a US location for '{query}'. Try City, ST, USA."
        )
    return results[0]


def resolve_location(location):
    lat = location.get("lat")
    lng = location.get("lng")
    query = location["query"]
    if lat is not None and lng is not None:
        return {"label": location.get("label") or query, "lat": float(lat), "lng": float(lng)}
    return geocode(query)