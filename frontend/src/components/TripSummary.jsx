import { formatHours } from "../constants";

export default function TripSummary({ summary }) {
  const cards = [
    { label: "Total distance", value: `${summary.total_distance_miles.toLocaleString()} mi` },
    { label: "Driving time", value: formatHours(summary.driving_hours) },
    { label: "Total trip time", value: formatHours(summary.duration_hours) },
    { label: "Log sheets", value: summary.days },
    { label: "Fuel stops", value: summary.fuel_stops },
    { label: "Rest periods", value: summary.rest_stops },
  ];
  return (
    <div className="summary-grid">
      {cards.map((card) => (
        <div className="summary-card" key={card.label}>
          <span className="summary-value">{card.value}</span>
          <span className="summary-label">{card.label}</span>
        </div>
      ))}
    </div>
  );
}