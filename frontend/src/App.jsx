import { useState } from "react";
import { planTrip } from "./api";
import TripForm from "./components/TripForm";
import MapView from "./components/MapView";
import TripSummary from "./components/TripSummary";
import StopsList from "./components/StopsList";
import DailyLogs from "./components/DailyLogs";

function readError(error) {
  const data = error.response?.data;
  if (data?.detail) {
    return data.detail;
  }
  if (data && typeof data === "object") {
    const first = Object.values(data)[0];
    if (Array.isArray(first)) {
      return first[0];
    }
  }
  return "Something went wrong while planning the trip. Please try again.";
}

export default function App() {
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (payload) => {
    setLoading(true);
    setError("");
    try {
      const data = await planTrip(payload);
      setTrip(data.result);
    } catch (requestError) {
      setError(readError(requestError));
      setTrip(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-bar">
        <div className="app-bar-inner">
          <h1>ELD Trip Planner</h1>
          <p>Route planning and electronic logs for property-carrying drivers on the 70 hour / 8 day cycle.</p>
        </div>
      </header>
      <main className="layout">
        <aside className="sidebar">
          <section className="panel">
            <h2>Trip details</h2>
            <TripForm onSubmit={handleSubmit} loading={loading} />
          </section>
          <section className="panel assumptions">
            <h2>Assumptions</h2>
            <ul>
              <li>US locations only, use City, ST, USA format</li>
              <li>70 hour / 8 day cycle, no adverse conditions</li>
              <li>1 hour each for pickup and dropoff</li>
              <li>Fueling at least every 1,000 miles</li>
              <li>10 hour reset after 11 driving or 14 on-duty hours</li>
            </ul>
          </section>
        </aside>
        <section className="content">
          {loading ? <StateMessage title="Planning your route" body="Geocoding stops and building duty logs." spinner /> : null}
          {!loading && error ? <StateMessage title="Unable to plan trip" body={error} tone="error" /> : null}
          {!loading && !error && !trip ? (
            <StateMessage
              title="Plan a trip to begin"
              body="Enter the current, pickup, and dropoff locations along with cycle hours used to generate a route and daily logs."
            />
          ) : null}
          {!loading && !error && trip ? <Results trip={trip} /> : null}
        </section>
      </main>
    </div>
  );
}

function Results({ trip }) {
  return (
    <div className="results">
      <TripSummary summary={trip.summary} />
      <section className="panel">
        <h2>Route and stops</h2>
        <div className="route-layout">
          <MapView route={trip.route} locations={trip.locations} stops={trip.stops} />
          <StopsList stops={trip.stops} />
        </div>
      </section>
      <section className="panel">
        <h2>Daily log sheets</h2>
        <DailyLogs logs={trip.daily_logs} locations={trip.locations} />
      </section>
    </div>
  );
}

function StateMessage({ title, body, tone, spinner }) {
  return (
    <div className={tone === "error" ? "state-message error" : "state-message"}>
      {spinner ? <span className="spinner" aria-hidden="true" /> : null}
      <h2>{title}</h2>
      <p>{body}</p>
    </div>
  );
}