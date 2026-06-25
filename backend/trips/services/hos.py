DRIVE_LIMIT = 11 * 60
WINDOW_LIMIT = 14 * 60
DRIVE_BEFORE_BREAK = 8 * 60
BREAK_DURATION = 30
REST_DURATION = 10 * 60
RESTART_DURATION = 34 * 60
CYCLE_LIMIT = 70 * 60
FUEL_INTERVAL_MILES = 1000
FUEL_DURATION = 15
PICKUP_DURATION = 60
DROPOFF_DURATION = 60
DAY_MINUTES = 24 * 60

OFF_DUTY = "off_duty"
SLEEPER_BERTH = "sleeper_berth"
DRIVING = "driving"
ON_DUTY = "on_duty"


class TripPlanner:
    def __init__(self, current_cycle_used_hours, start_offset_minutes=8 * 60):
        self.cycle_used = max(0, round(current_cycle_used_hours * 60))
        self.time = start_offset_minutes
        self.window_start = start_offset_minutes
        self.drive_in_shift = 0
        self.drive_since_break = 0
        self.miles_since_fuel = 0
        self.total_miles = 0
        self.segments = []
        self.events = []

    def _add_segment(self, status, duration, miles=0):
        if duration <= 0:
            return
        start = self.time
        self.segments.append(
            {
                "status": status,
                "start_minute": start,
                "end_minute": start + duration,
                "miles_start": self.total_miles,
                "miles_end": self.total_miles + miles,
            }
        )
        self.time += duration
        self.total_miles += miles

    def _record_event(self, event_type, start, duration):
        self.events.append(
            {
                "type": event_type,
                "start_minute": start,
                "duration_minute": duration,
                "miles": self.total_miles,
            }
        )

    def _take_rest(self):
        self._record_event("rest", self.time, REST_DURATION)
        self._add_segment(SLEEPER_BERTH, REST_DURATION)
        self.drive_in_shift = 0
        self.drive_since_break = 0
        self.window_start = self.time

    def _take_restart(self):
        self._record_event("restart", self.time, RESTART_DURATION)
        self._add_segment(OFF_DUTY, RESTART_DURATION)
        self.cycle_used = 0
        self.drive_in_shift = 0
        self.drive_since_break = 0
        self.window_start = self.time

    def _take_break(self):
        self._record_event("break", self.time, BREAK_DURATION)
        self._add_segment(OFF_DUTY, BREAK_DURATION)
        self.drive_since_break = 0

    def _fuel(self):
        self._record_event("fuel", self.time, FUEL_DURATION)
        self._on_duty_activity(FUEL_DURATION)
        self.miles_since_fuel = 0

    def _on_duty_activity(self, duration):
        if self.cycle_used + duration > CYCLE_LIMIT:
            self._take_restart()
        self._add_segment(ON_DUTY, duration)
        self.cycle_used += duration
        if duration >= BREAK_DURATION:
            self.drive_since_break = 0

    def pickup(self):
        self._record_event("pickup", self.time, PICKUP_DURATION)
        self._on_duty_activity(PICKUP_DURATION)

    def dropoff(self):
        self._record_event("dropoff", self.time, DROPOFF_DURATION)
        self._on_duty_activity(DROPOFF_DURATION)

    def drive(self, distance_miles, duration_minutes):
        if distance_miles <= 0 or duration_minutes <= 0:
            return
        minutes_per_mile = duration_minutes / distance_miles
        remaining = duration_minutes
        while remaining > 0:
            window_used = self.time - self.window_start
            if self.cycle_used >= CYCLE_LIMIT:
                self._take_restart()
                continue
            if self.drive_in_shift >= DRIVE_LIMIT or window_used >= WINDOW_LIMIT:
                self._take_rest()
                continue
            if self.drive_since_break >= DRIVE_BEFORE_BREAK:
                self._take_break()
                continue
            if self.miles_since_fuel >= FUEL_INTERVAL_MILES:
                self._fuel()
                continue
            fuel_allowance = (FUEL_INTERVAL_MILES - self.miles_since_fuel) * minutes_per_mile
            chunk = min(
                remaining,
                DRIVE_LIMIT - self.drive_in_shift,
                WINDOW_LIMIT - window_used,
                DRIVE_BEFORE_BREAK - self.drive_since_break,
                CYCLE_LIMIT - self.cycle_used,
                fuel_allowance,
            )
            chunk = max(1, round(chunk))
            chunk = min(chunk, remaining)
            chunk_miles = chunk / minutes_per_mile
            self._add_segment(DRIVING, chunk, chunk_miles)
            self.drive_in_shift += chunk
            self.drive_since_break += chunk
            self.cycle_used += chunk
            self.miles_since_fuel += chunk_miles
            remaining -= chunk

    def finalize(self):
        merged = self._merge_segments()
        return {
            "segments": merged,
            "events": self.events,
            "total_minutes": self.time,
            "total_miles": round(self.total_miles, 1),
        }

    def _merge_segments(self):
        merged = []
        for segment in self.segments:
            if merged and merged[-1]["status"] == segment["status"] and merged[-1]["end_minute"] == segment["start_minute"]:
                merged[-1]["end_minute"] = segment["end_minute"]
                merged[-1]["miles_end"] = segment["miles_end"]
            else:
                merged.append(dict(segment))
        return merged


def plan_trip(legs, current_cycle_used_hours, start_offset_minutes=8 * 60):
    planner = TripPlanner(current_cycle_used_hours, start_offset_minutes)
    planner.drive(legs[0]["distance_miles"], legs[0]["duration_minutes"])
    planner.pickup()
    planner.drive(legs[1]["distance_miles"], legs[1]["duration_minutes"])
    planner.dropoff()
    return planner.finalize()