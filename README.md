# ELD Trip Planner

Full stack application that takes trip details and produces route instructions with
stops and rests, plus filled out FMCSA daily log sheets for property carrying drivers
on the 70 hour / 8 day cycle.

## Stack

- Backend: Django, Django REST Framework
- Frontend: React (Vite), Leaflet
- Routing: OSRM (free), Geocoding: Nominatim (free)

## Features

- Location autocomplete backed by Nominatim so trips use confirmed coordinates
- Hours of Service engine: 11 hour driving limit, 14 hour window, 30 minute break,
  70 hour / 8 day cycle, 34 hour restart, fueling every 1,000 miles, 1 hour pickup and dropoff
- Interactive map with route line and color coded stop markers
- Daily log sheets drawn on the standard 24 hour grid, one sheet per day

## Local development

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app runs at http://localhost:5173 and talks to the API at http://localhost:8000/api.

## API

- `GET /api/locations/search/?q=` returns up to 5 matching locations
- `POST /api/trips/plan/` plans a trip and returns the route, stops, and daily logs
- `GET /api/trips/` lists saved trips
- `GET /api/trips/<id>/` returns a single saved trip

## Deployment

### Backend on Render

1. Push this repository to GitHub.
2. In Render, create a new Blueprint from the repo. The included `render.yaml` provisions
   the web service from the `backend` directory.
3. After the first deploy, set `DJANGO_CORS_ALLOWED_ORIGINS` to your Vercel URL,
   for example `https://your-app.vercel.app`.

### Frontend on Vercel

1. In Vercel, import the repo and set the root directory to `frontend`.
2. Add an environment variable `VITE_API_URL` set to your Render API URL,
   for example `https://eld-trip-planner-api.onrender.com/api`.
3. Deploy.

## Assumptions

- Property carrying driver, 70 hours / 8 days, no adverse driving conditions
- Fueling at least once every 1,000 miles
- 1 hour each for pickup and dropoff
- US locations on a connected road network
