import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const client = axios.create({ baseURL, timeout: 40000 });

export async function planTrip(payload) {
  const { data } = await client.post("/trips/plan/", payload);
  return data;
}

export async function searchLocations(query) {
  const { data } = await client.get("/locations/search/", { params: { q: query } });
  return data;
}