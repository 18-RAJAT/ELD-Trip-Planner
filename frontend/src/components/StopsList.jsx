import { STOP_STYLES, formatHours } from "../constants";

export default function StopsList({ stops }) {
  return (
    <ul className="stops-list">
      {stops.map((stop, index) => {
        const style = STOP_STYLES[stop.type] || STOP_STYLES.fuel;
        return (
          <li className="stop-item" key={`${stop.type}-${index}`}>
            <span className="stop-badge" style={{ background: style.color }}>
              {style.glyph}
            </span>
            <div className="stop-details">
              <span className="stop-label">{stop.label}</span>
              <span className="stop-meta">
                Day {stop.day} at {stop.clock} for {formatHours(stop.duration_hours)}
              </span>
            </div>
          </li>
        );
      })}
    </ul>
  );
}