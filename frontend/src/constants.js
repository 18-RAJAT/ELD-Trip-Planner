export const STATUS_ROWS = [
  { key: "off_duty", label: "1. Off Duty" },
  { key: "sleeper_berth", label: "2. Sleeper Berth" },
  { key: "driving", label: "3. Driving" },
  { key: "on_duty", label: "4. On Duty (not driving)" },
];

export const STATUS_LABELS = {
  off_duty: "Off duty",
  sleeper_berth: "Sleeper berth",
  driving: "Driving",
  on_duty: "On duty",
};

export const STOP_STYLES = {
  current: { color: "#2563eb", glyph: "S" },
  pickup: { color: "#16a34a", glyph: "P" },
  dropoff: { color: "#dc2626", glyph: "D" },
  fuel: { color: "#d97706", glyph: "F" },
  break: { color: "#7c3aed", glyph: "B" },
  rest: { color: "#0891b2", glyph: "R" },
  restart: { color: "#0891b2", glyph: "R" },
};

export function formatHours(value) {
  const hours = Math.floor(value);
  const minutes = Math.round((value - hours) * 60);
  if (minutes === 0) {
    return `${hours}h`;
  }
  return `${hours}h ${minutes}m`;
}