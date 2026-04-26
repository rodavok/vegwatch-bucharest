import os
import json
import hashlib
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
BASE_URL = "https://maps.googleapis.com/maps/api/place"
CACHE_DIR = Path(__file__).parent.parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)


def _cache_key(prefix: str, params: dict) -> Path:
    h = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:12]
    return CACHE_DIR / f"{prefix}_{h}.json"


def _cached_get(prefix: str, url: str, params: dict) -> dict:
    cache_file = _cache_key(prefix, params)
    if cache_file.exists():
        return json.loads(cache_file.read_text())

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    cache_file.write_text(json.dumps(data))
    return data


def nearby_restaurants(lat: float, lng: float, radius: int = 1500, max_pages: int = 1) -> list[dict]:
    """Find restaurants near a location. Use max_pages > 1 to get more results (up to 60)."""
    import time

    url = f"{BASE_URL}/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "restaurant",
        "key": API_KEY,
    }

    all_results = []

    for page in range(max_pages):
        if page == 0:
            data = _cached_get(f"nearby_p{page}", url, params)
        else:
            # Need to wait for next_page_token to be valid
            time.sleep(2)
            page_params = {"pagetoken": next_token, "key": API_KEY}
            data = _cached_get(f"nearby_p{page}", url, page_params)

        all_results.extend(data.get("results", []))

        next_token = data.get("next_page_token")
        if not next_token:
            break

    return all_results


def place_details(place_id: str) -> dict:
    """Get details and reviews for a place."""
    url = f"{BASE_URL}/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,reviews,types,formatted_address,geometry",
        "key": API_KEY,
    }
    data = _cached_get("details", url, params)
    return data.get("result", {})


def get_restaurants_with_reviews(lat: float, lng: float, radius: int = 1500) -> list[dict]:
    """Get restaurants with their reviews for an area."""
    restaurants = nearby_restaurants(lat, lng, radius)
    results = []
    for r in restaurants:
        place_id = r.get("place_id")
        if place_id:
            details = place_details(place_id)
            results.append(details)
    return results


if __name__ == "__main__":
    # Test with Bucharest center
    BUCHAREST_LAT = 44.4268
    BUCHAREST_LNG = 26.1025

    print("Fetching nearby restaurants...")
    restaurants = nearby_restaurants(BUCHAREST_LAT, BUCHAREST_LNG, radius=500)
    print(f"Found {len(restaurants)} restaurants\n")

    if restaurants:
        first = restaurants[0]
        print(f"Getting details for: {first.get('name')}")
        details = place_details(first["place_id"])

        print(f"Rating: {details.get('rating')}")
        print(f"Total ratings: {details.get('user_ratings_total')}")
        print(f"Types: {details.get('types')}")

        reviews = details.get("reviews", [])
        print(f"\nReviews ({len(reviews)}):")
        for review in reviews[:2]:
            print(f"  - {review.get('rating')}★: {review.get('text', '')[:100]}...")
