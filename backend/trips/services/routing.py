from math import asin, cos, radians, sin, sqrt

import requests
from django.conf import settings

from .errors import RoutingError

METERS_PER_MILE = 1609.344
EARTH_RADIUS_MILES = 3958.7613


def get_route(coordinates, waypoints):
    path = ";".join(f"{lng},{lat}" for lng, lat in coordinates)
    url = f"{settings.OSRM_BASE_URL}/route/v1/driving/{path}"
    params = {"overview": "full", "geometries": "geojson", "steps": "false"}
    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as exc:
        raise RoutingError("Unable to reach the routing service.") from exc
    try:
        data = response.json()
    except ValueError as exc:
        raise RoutingError("Unable to reach the routing service.") from exc
    if response.status_code != 200 or data.get("code") != "Ok" or not data.get("routes"):
        if data.get("code") == "NoRoute":
            raise RoutingError(
                "No drivable route connects these locations. Use specific US cities such as Amarillo, TX, USA."
            )
        raise RoutingError("Could not calculate a route between the provided locations.")
    route = data["routes"][0]
    legs = [
        {
            "distance_miles": round(leg["distance"] / METERS_PER_MILE, 2),
            "duration_minutes": round(leg["duration"] / 60, 2),
        }
        for leg in route["legs"]
    ]
    geometry = [[point[0], point[1]] for point in route["geometry"]["coordinates"]]
    snapped = [waypoint["location"] for waypoint in data.get("waypoints", [])]
    _validate_route_endpoints(geometry, snapped, waypoints)
    return {
        "geometry": geometry,
        "legs": legs,
        "distance_miles": round(route["distance"] / METERS_PER_MILE, 2),
        "duration_minutes": round(route["duration"] / 60, 2),
    }


def _validate_route_endpoints(geometry, snapped, waypoints):
    if not geometry:
        raise RoutingError("No drivable route connects these locations.")
    tolerance = settings.ROUTE_ENDPOINT_TOLERANCE_MILES
    origin = waypoints[0]
    pickup = waypoints[1]
    dropoff = waypoints[2]
    checks = [
        (geometry[0], origin, "the current location"),
        (geometry[-1], dropoff, "the dropoff location"),
    ]
    if len(snapped) >= 2:
        checks.insert(1, (snapped[1], pickup, "the pickup location"))
    else:
        checks.insert(1, (_closest_point(geometry, pickup), pickup, "the pickup location"))
    for route_point, target, label in checks:
        gap = _haversine_miles(route_point, (target["lng"], target["lat"]))
        if gap > tolerance:
            raise RoutingError(
                f"The route does not reach {label}. Use specific drivable US locations such as City, ST, USA."
            )


def _closest_point(geometry, target):
    target_point = (target["lng"], target["lat"])
    return min(geometry, key=lambda point: _haversine_miles(point, target_point))


def _haversine_miles(start, end):
    lng1, lat1 = radians(start[0]), radians(start[1])
    lng2, lat2 = radians(end[0]), radians(end[1])
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    inner = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * asin(sqrt(inner))


def point_at_miles(geometry, target_miles):
    if not geometry:
        return None
    if target_miles <= 0:
        return {"lng": geometry[0][0], "lat": geometry[0][1]}
    traveled = 0
    for index in range(len(geometry) - 1):
        start = geometry[index]
        end = geometry[index + 1]
        span = _haversine_miles(start, end)
        if span == 0:
            continue
        if traveled + span >= target_miles:
            ratio = (target_miles - traveled) / span
            return {
                "lng": start[0] + (end[0] - start[0]) * ratio,
                "lat": start[1] + (end[1] - start[1]) * ratio,
            }
        traveled += span
    last = geometry[-1]
    return {"lng": last[0], "lat": last[1]}