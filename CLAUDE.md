# VegWatch Bucharest

## Goal
Analyze restaurant reviews in Bucharest to identify:
- Vegetarian option availability by neighborhood
- Geographical zones of quality
- Trend analysis opportunities

## Current State
- 233 restaurants collected across 12 Bucharest neighborhoods
- 1,165 reviews with text analyzed
- 34 restaurants identified as vegetarian-friendly
- Streamlit dashboard for visualization

## Project Structure
```
src/
  google_places.py    # API client with caching
  scan_bucharest.py   # Neighborhood scanner
  dashboard.py        # Streamlit dashboard (VegWatch)
data/
  bucharest_all_neighborhoods.json
  bucharest_vegetarian_analysis.json
docs/
  google-places-api.md
  wolt-api.md
```

## Running the Dashboard

Local:
```bash
.venv/bin/streamlit run src/dashboard.py
```

Deployed: Streamlit Community Cloud
- Repo: github.com/rodavok/vegwatch-bucharest
- Main file: src/dashboard.py

## Data Sources

### Primary: Google Places API
- 10K free calls/month per SKU (Essentials tier)
- Returns up to 5 reviews per place
- API key in `.env` as `GOOGLE_PLACES_API_KEY`
- Responses cached in `.cache/`
- See `docs/google-places-api.md`

### Secondary: Wolt API (formerly Tazz)
- Ratings and location data only (no review text)
- See `docs/wolt-api.md`

### Not viable
- **Yelp Fusion** — minimal Romania presence
- **TripAdvisor** — bot detection blocks scraping
- **Google Maps scraping** — requires login for reviews

## Neighborhoods Covered
Old Town, Floreasca, Dorobanti, Herastrau, Pipera, Titan, Dristor, Tineretului, Militari, Drumul Taberei, Cotroceni, Universitate

## Vegetarian Analysis
Reviews are scanned for vegetarian/vegan keywords and classified as:
- `has_options` — positive vegetarian mentions
- `no_options` — explicitly lacks options
- `no_mention` — no vegetarian references

Top neighborhoods: Dorobanti (30%), Pipera (30%), Cotroceni (25%)
