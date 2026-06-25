import { STATUS_ROWS } from "../constants";

const LEFT = 168;
const GRID_W = 744;
const TOP = 34;
const ROW_H = 34;
const RIGHT_W = 78;
const WIDTH = LEFT + GRID_W + RIGHT_W;
const HEIGHT = TOP + ROW_H * STATUS_ROWS.length + 8;

const ROW_INDEX = {
  off_duty: 0,
  sleeper_berth: 1,
  driving: 2,
  on_duty: 3,
};

const HOUR_LABELS = ["Mid", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, "Noon", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, "Mid"];

function minuteToX(minute) {
  return LEFT + (minute / 1440) * GRID_W;
}

function rowCenter(index) {
  return TOP + index * ROW_H + ROW_H / 2;
}

function buildPoints(entries) {
  const points = [];
  entries.forEach((entry) => {
    const y = rowCenter(ROW_INDEX[entry.status]);
    points.push(`${minuteToX(entry.start_minute)},${y}`);
    points.push(`${minuteToX(entry.end_minute)},${y}`);
  });
  return points.join(" ");
}

export default function LogSheet({ log, trip }) {
  const hourLines = Array.from({ length: 25 }, (_, hour) => hour);
  const quarters = Array.from({ length: 24 * 4 }, (_, index) => index);

  return (
    <article className="log-sheet">
      <header className="log-sheet-header">
        <div>
          <h3>Driver&apos;s Daily Log</h3>
          <span className="log-sheet-sub">Day {log.day} of {trip.totalDays}</span>
        </div>
        <span className="log-sheet-date">{log.date}</span>
      </header>
      <div className="log-sheet-meta">
        <Meta label="From" value={trip.from} />
        <Meta label="To" value={trip.to} />
        <Meta label="Miles driving today" value={`${log.driving_miles} mi`} />
      </div>
      <svg className="log-grid" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label={`Log grid for day ${log.day}`}>
        {hourLines.map((hour) => (
          <g key={`hour-${hour}`}>
            <line
              x1={minuteToX(hour * 60)}
              y1={TOP}
              x2={minuteToX(hour * 60)}
              y2={TOP + ROW_H * STATUS_ROWS.length}
              className="grid-line"
            />
            <text x={minuteToX(hour * 60)} y={TOP - 12} className="hour-label">
              {HOUR_LABELS[hour]}
            </text>
          </g>
        ))}
        {quarters.flatMap((index) => {
          const minute = index * 15;
          const isHalf = index % 4 === 2;
          if (index % 4 === 0) {
            return [];
          }
          return STATUS_ROWS.map((_, rowIndex) => (
            <line
              key={`tick-${index}-${rowIndex}`}
              x1={minuteToX(minute)}
              y1={TOP + rowIndex * ROW_H + (isHalf ? ROW_H * 0.3 : ROW_H * 0.62)}
              x2={minuteToX(minute)}
              y2={TOP + rowIndex * ROW_H + ROW_H}
              className="tick-line"
            />
          ));
        })}
        {STATUS_ROWS.map((row, index) => (
          <g key={row.key}>
            <line
              x1={LEFT}
              y1={TOP + index * ROW_H}
              x2={LEFT + GRID_W}
              y2={TOP + index * ROW_H}
              className="grid-line"
            />
            <text x={LEFT - 10} y={rowCenter(index)} className="row-label">
              {row.label}
            </text>
            <text x={LEFT + GRID_W + RIGHT_W / 2} y={rowCenter(index)} className="row-total">
              {log.totals[row.key].toFixed(2)}
            </text>
          </g>
        ))}
        <line
          x1={LEFT}
          y1={TOP + ROW_H * STATUS_ROWS.length}
          x2={LEFT + GRID_W}
          y2={TOP + ROW_H * STATUS_ROWS.length}
          className="grid-line"
        />
        <text x={LEFT + GRID_W + RIGHT_W / 2} y={TOP - 12} className="hour-label">
          Total
        </text>
        <polyline points={buildPoints(log.entries)} className="status-line" />
      </svg>
    </article>
  );
}

function Meta({ label, value }) {
  return (
    <div className="log-meta-item">
      <span className="log-meta-label">{label}</span>
      <span className="log-meta-value">{value}</span>
    </div>
  );
}