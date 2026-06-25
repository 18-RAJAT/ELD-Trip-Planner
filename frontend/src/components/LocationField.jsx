import { useEffect, useRef, useState } from "react";
import { searchLocations } from "../api";

export default function LocationField({ id, label, placeholder, value, onChange, error }) {
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const term = value.label.trim();
    if (value.selected || term.length < 3) {
      setSuggestions([]);
      setLoading(false);
      return undefined;
    }
    setLoading(true);
    const timer = setTimeout(async () => {
      try {
        const results = await searchLocations(term);
        setSuggestions(results);
        setOpen(true);
        setActiveIndex(-1);
      } catch {
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, 350);
    return () => clearTimeout(timer);
  }, [value.label, value.selected]);

  const handleInput = (event) => {
    onChange({ label: event.target.value, lat: null, lng: null, selected: false });
  };

  const handleSelect = (suggestion) => {
    onChange({
      label: suggestion.label,
      lat: suggestion.lat,
      lng: suggestion.lng,
      selected: true,
    });
    setOpen(false);
    setSuggestions([]);
  };

  const handleKeyDown = (event) => {
    if (!open || suggestions.length === 0) {
      return;
    }
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex((index) => (index + 1) % suggestions.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex((index) => (index - 1 + suggestions.length) % suggestions.length);
    } else if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();
      handleSelect(suggestions[activeIndex]);
    } else if (event.key === "Escape") {
      setOpen(false);
    }
  };

  return (
    <div className="field" ref={containerRef}>
      <label htmlFor={id}>{label}</label>
      <div className="autocomplete">
        <input
          id={id}
          className={error ? "input invalid" : "input"}
          placeholder={placeholder}
          value={value.label}
          autoComplete="off"
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          onFocus={() => suggestions.length > 0 && setOpen(true)}
        />
        {loading ? <span className="autocomplete-loading">...</span> : null}
        {open && suggestions.length > 0 ? (
          <ul className="suggestions">
            {suggestions.map((suggestion, index) => (
              <li key={`${suggestion.lat}-${suggestion.lng}`}>
                <button
                  type="button"
                  className={index === activeIndex ? "suggestion active" : "suggestion"}
                  onClick={() => handleSelect(suggestion)}
                >
                  {suggestion.label}
                </button>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
      {error ? <span className="field-error">{error}</span> : null}
    </div>
  );
}