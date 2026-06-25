from datetime import date, timedelta

from .geocoding import resolve_location
from .hos import DAY_MINUTES, DRIVING, plan_trip
from .logs import build_daily_logs
from .routing import get_route, point_at_miles

START_OFFSET_MINUTES = 8 * 60

EVENT_LABELS = {
    "pickup": "Pickup",
    "dropoff": "Dropoff",
    "fuel": "Fueling stop",
    "break": "30-minute break",
    "rest": "10-hour rest",
    "restart": "34-hour restart",
}


def _format_clock(minute):
    minute_of_day = minute % DAY_MINUTES
    return f"{minute_of_day // 60:02d}:{minute_of_day % 60:02d}"


def plan(current_location, pickup_location, dropoff_location, current_cycle_used, start_date=None):
    origin = resolve_location(current_location)
    pickup = resolve_location(pickup_location)
    dropoff = resolve_location(dropoff_location)

    waypoints = [origin, pickup, dropoff]
    route = get_route(
        [
            (origin["lng"], origin["lat"]),
            (pickup["lng"], pickup["lat"]),
            (dropoff["lng"], dropoff["lat"]),
        ],
        waypoints,
    )

    legs = [
        {
            "distance_miles": leg["distance_miles"],
            "duration_minutes": round(leg["duration_minutes"]),
        }
        for leg in route["legs"]
    ]
    plan_result = plan_trip(legs, current_cycle_used, START_OFFSET_MINUTES)
    daily_logs = build_daily_logs(plan_result["segments"], plan_result["total_minutes"])

    start = start_date or date.today()
    for log in daily_logs:
        log["date"] = (start + timedelta(days=log["day"] - 1)).isoformat()

    stops = _build_stops(plan_result["events"], route["geometry"], pickup, dropoff)

    driving_minutes = sum(
        segment["end_minute"] - segment["start_minute"]
        for segment in plan_result["segments"]
        if segment["status"] == DRIVING
    )

    summary = {
        "total_distance_miles": route["distance_miles"],
        "driving_hours": round(driving_minutes / 60, 2),
        "duration_hours": round((plan_result["total_minutes"] - START_OFFSET_MINUTES) / 60, 2),
        "days": len(daily_logs),
        "fuel_stops": sum(1 for event in plan_result["events"] if event["type"] == "fuel"),
        "rest_stops": sum(1 for event in plan_result["events"] if event["type"] in ("rest", "restart")),
    }

    return {
        "locations": {
            "current": origin,
            "pickup": pickup,
            "dropoff": dropoff,
        },
        "route": {
            "geometry": route["geometry"],
            "distance_miles": route["distance_miles"],
        },
        "stops": stops,
        "daily_logs": daily_logs,
        "summary": summary,
    }


def _build_stops(events, geometry, pickup, dropoff):
    stops = []
    for event in events:
        if event["type"] == "pickup":
            coordinate = {"lat": pickup["lat"], "lng": pickup["lng"]}
        elif event["type"] == "dropoff":
            coordinate = {"lat": dropoff["lat"], "lng": dropoff["lng"]}
        else:
            coordinate = point_at_miles(geometry, event["miles"])
        if not coordinate:
            continue
        stops.append(
            {
                "type": event["type"],
                "label": EVENT_LABELS[event["type"]],
                "lat": coordinate["lat"],
                "lng": coordinate["lng"],
                "day": event["start_minute"] // DAY_MINUTES + 1,
                "clock": _format_clock(event["start_minute"]),
                "duration_hours": round(event["duration_minute"] / 60, 2),
            }
        )
    return stops