from math import ceil

from .hos import DAY_MINUTES, DRIVING, OFF_DUTY


def _status_totals():
    return {"off_duty": 0, "sleeper_berth": 0, "driving": 0, "on_duty": 0}


def build_daily_logs(segments, total_minutes):
    if total_minutes <= 0:
        return []
    num_days = ceil(total_minutes / DAY_MINUTES)
    logs = []
    for day in range(num_days):
        day_start = day * DAY_MINUTES
        day_end = day_start + DAY_MINUTES
        entries = []
        for segment in segments:
            start = max(segment["start_minute"], day_start)
            end = min(segment["end_minute"], day_end)
            if end <= start:
                continue
            span = segment["end_minute"] - segment["start_minute"]
            fraction = (end - start) / span if span else 0
            miles = (segment["miles_end"] - segment["miles_start"]) * fraction
            entries.append(
                {
                    "status": segment["status"],
                    "start_minute": start - day_start,
                    "end_minute": end - day_start,
                    "miles": miles,
                }
            )
        entries = _fill_gaps(entries)
        totals = _status_totals()
        driving_miles = 0
        for entry in entries:
            totals[entry["status"]] += entry["end_minute"] - entry["start_minute"]
            if entry["status"] == DRIVING:
                driving_miles += entry["miles"]
        logs.append(
            {
                "day": day + 1,
                "entries": [
                    {
                        "status": entry["status"],
                        "start_minute": entry["start_minute"],
                        "end_minute": entry["end_minute"],
                    }
                    for entry in entries
                ],
                "totals": {key: round(value / 60, 2) for key, value in totals.items()},
                "driving_miles": round(driving_miles, 1),
            }
        )
    return logs


def _fill_gaps(entries):
    entries.sort(key=lambda item: item["start_minute"])
    filled = []
    cursor = 0
    for entry in entries:
        if entry["start_minute"] > cursor:
            filled.append(
                {
                    "status": OFF_DUTY,
                    "start_minute": cursor,
                    "end_minute": entry["start_minute"],
                    "miles": 0,
                }
            )
        filled.append(entry)
        cursor = entry["end_minute"]
    if cursor < DAY_MINUTES:
        filled.append(
            {
                "status": OFF_DUTY,
                "start_minute": cursor,
                "end_minute": DAY_MINUTES,
                "miles": 0,
            }
        )
    return filled