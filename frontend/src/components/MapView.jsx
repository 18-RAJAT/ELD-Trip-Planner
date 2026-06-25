import { useEffect, useMemo } from "react";
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import { STOP_STYLES } from "../constants";

function markerIcon(type) {
  const style = STOP_STYLES[type] || STOP_STYLES.fuel;
  return L.divIcon({
    className: "map-marker",
    html: `<span style="background:${style.color}">${style.glyph}</span>`,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
  });
}

function FitBounds({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [map, bounds]);
  return null;
}

export default function MapView({ route, locations, stops }) {
  const line = useMemo(
    () => route.geometry.map((point) => [point[1], point[0]]),
    [route.geometry]
  );

  const bounds = useMemo(() => (line.length ? L.latLngBounds(line) : null), [line]);

  const baseMarkers = [
    { type: "current", title: "Start", location: locations.current },
    { type: "pickup", title: "Pickup", location: locations.pickup },
    { type: "dropoff", title: "Dropoff", location: locations.dropoff },
  ];

  const routeStops = stops.filter((stop) => stop.type !== "pickup" && stop.type !== "dropoff");

  const markerLayers = [
    ...routeStops.map((stop, index) => ({
      key: `${stop.type}-${index}`,
      position: [stop.lat, stop.lng],
      type: stop.type,
      popup: (
        <>
          <strong>{stop.label}</strong>
          <br />
          Day {stop.day} at {stop.clock}
        </>
      ),
      zIndex: 100,
    })),
    ...baseMarkers.map((marker) => ({
      key: marker.type,
      position: [marker.location.lat, marker.location.lng],
      type: marker.type,
      popup: (
        <>
          <strong>{marker.title}</strong>
          <br />
          {marker.location.label}
        </>
      ),
      zIndex: marker.type === "dropoff" ? 300 : marker.type === "pickup" ? 250 : 200,
    })),
  ];

  return (
    <MapContainer className="map" center={[39.5, -98.35]} zoom={4} scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {line.length ? <Polyline positions={line} color="#ff5a1f" weight={4} /> : null}
      {markerLayers.map((marker) => (
        <Marker
          key={marker.key}
          position={marker.position}
          icon={markerIcon(marker.type)}
          zIndexOffset={marker.zIndex}
        >
          <Popup>{marker.popup}</Popup>
        </Marker>
      ))}
      <FitBounds bounds={bounds} />
    </MapContainer>
  );
}