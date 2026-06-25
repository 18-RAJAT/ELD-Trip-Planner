import { useState } from "react";
import LocationField from "./LocationField";

const EMPTY_LOCATION = { label: "", lat: null, lng: null, selected: false };

const EMPTY_FORM = {
  current: { ...EMPTY_LOCATION },
  pickup: { ...EMPTY_LOCATION },
  dropoff: { ...EMPTY_LOCATION },
  current_cycle_used: "",
};

function validateLocation(location) {
  if (!location.label.trim()) {
    return "This location is required.";
  }
  if (!location.selected || location.lat === null || location.lng === null) {
    return "Select a location from the suggestions.";
  }
  return null;
}

function validate(form) {
  const errors = {};
  const current = validateLocation(form.current);
  if (current) {
    errors.current = current;
  }
  const pickup = validateLocation(form.pickup);
  if (pickup) {
    errors.pickup = pickup;
  }
  const dropoff = validateLocation(form.dropoff);
  if (dropoff) {
    errors.dropoff = dropoff;
  }
  const cycle = Number(form.current_cycle_used);
  if (form.current_cycle_used === "" || Number.isNaN(cycle)) {
    errors.current_cycle_used = "Enter the cycle hours used.";
  } else if (cycle < 0 || cycle > 70) {
    errors.current_cycle_used = "Cycle hours must be between 0 and 70.";
  }
  return errors;
}

export default function TripForm({ onSubmit, loading }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});

  const handleLocationChange = (field) => (location) => {
    setForm((previous) => ({ ...previous, [field]: location }));
  };

  const handleCycleChange = (event) => {
    setForm((previous) => ({ ...previous, current_cycle_used: event.target.value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const validationErrors = validate(form);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) {
      return;
    }
    onSubmit({
      current_location: form.current.label,
      current_lat: form.current.lat,
      current_lng: form.current.lng,
      pickup_location: form.pickup.label,
      pickup_lat: form.pickup.lat,
      pickup_lng: form.pickup.lng,
      dropoff_location: form.dropoff.label,
      dropoff_lat: form.dropoff.lat,
      dropoff_lng: form.dropoff.lng,
      current_cycle_used: Number(form.current_cycle_used),
    });
  };

  return (
    <form className="trip-form" onSubmit={handleSubmit} noValidate>
      <LocationField
        id="current_location"
        label="Current location"
        placeholder="Dallas, TX"
        value={form.current}
        onChange={handleLocationChange("current")}
        error={errors.current}
      />
      <LocationField
        id="pickup_location"
        label="Pickup location"
        placeholder="Oklahoma City, OK"
        value={form.pickup}
        onChange={handleLocationChange("pickup")}
        error={errors.pickup}
      />
      <LocationField
        id="dropoff_location"
        label="Dropoff location"
        placeholder="Denver, CO"
        value={form.dropoff}
        onChange={handleLocationChange("dropoff")}
        error={errors.dropoff}
      />
      <div className="field">
        <label htmlFor="current_cycle_used">Current cycle used (hours)</label>
        <input
          id="current_cycle_used"
          className={errors.current_cycle_used ? "input invalid" : "input"}
          type="number"
          step="0.25"
          min="0"
          max="70"
          placeholder="0"
          value={form.current_cycle_used}
          onChange={handleCycleChange}
        />
        {errors.current_cycle_used ? (
          <span className="field-error">{errors.current_cycle_used}</span>
        ) : null}
      </div>
      <button type="submit" className="primary-button" disabled={loading}>
        {loading ? "Planning route..." : "Plan trip"}
      </button>
    </form>
  );
}