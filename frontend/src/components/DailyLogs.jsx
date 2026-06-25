import LogSheet from "./LogSheet";

export default function DailyLogs({ logs, locations }) {
  const trip = {
    from: locations.current.label,
    to: locations.dropoff.label,
    totalDays: logs.length,
  };
  return (
    <div className="daily-logs">
      {logs.map((log) => (
        <LogSheet key={log.day} log={log} trip={trip} />
      ))}
    </div>
  );
}