import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from google_places import nearby_restaurants, place_details

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Bucharest neighborhoods with coordinates
NEIGHBORHOODS = {
    "Old Town": (44.4316, 26.0973),
    "Floreasca": (44.4620, 26.0970),
    "Dorobanți": (44.4530, 26.0850),
    "Herăstrău": (44.4750, 26.0780),
    "Pipera": (44.4900, 26.1100),
    "Titan": (44.4130, 26.1550),
    "Dristor": (44.4150, 26.1300),
    "Tineretului": (44.4050, 26.1000),
    "Militari": (44.4300, 26.0100),
    "Drumul Taberei": (44.4200, 25.9900),
    "Cotroceni": (44.4350, 26.0550),
    "Universitate": (44.4350, 26.1020),
}


def scan_neighborhood(name: str, lat: float, lng: float, top_n: int = 10, max_pages: int = 1) -> list[dict]:
    """Get top restaurants with reviews for a neighborhood."""
    print(f"\n{'='*50}")
    print(f"Scanning: {name} ({lat}, {lng})")
    print("="*50)

    restaurants = nearby_restaurants(lat, lng, radius=1500, max_pages=max_pages)
    print(f"Found {len(restaurants)} restaurants")

    # Filter and sort by rating
    rated = [r for r in restaurants if r.get("rating") and r.get("user_ratings_total", 0) > 50]
    top = sorted(rated, key=lambda x: (-x["rating"], -x.get("user_ratings_total", 0)))[:top_n]

    results = []
    for i, r in enumerate(top, 1):
        print(f"  [{i}/{len(top)}] {r['name'][:35]} - {r['rating']}★")

        details = place_details(r["place_id"])

        location = details.get("geometry", {}).get("location", {})

        results.append({
            "name": details.get("name"),
            "place_id": r["place_id"],
            "rating": details.get("rating"),
            "total_reviews": details.get("user_ratings_total"),
            "address": details.get("formatted_address"),
            "types": details.get("types"),
            "lat": location.get("lat"),
            "lng": location.get("lng"),
            "neighborhood": name,
            "reviews": details.get("reviews", []),
        })

    return results


def scan_all_neighborhoods(top_n: int = 20, max_pages: int = 3):
    """Scan all neighborhoods and save results."""
    all_results = []

    for name, (lat, lng) in NEIGHBORHOODS.items():
        results = scan_neighborhood(name, lat, lng, top_n=top_n, max_pages=max_pages)
        all_results.extend(results)

    # Save combined results
    output_file = DATA_DIR / "bucharest_all_neighborhoods.json"
    output_file.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))

    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print("="*50)
    print(f"Neighborhoods scanned: {len(NEIGHBORHOODS)}")
    print(f"Total restaurants: {len(all_results)}")
    print(f"Total reviews collected: {sum(len(r['reviews']) for r in all_results)}")
    print(f"Saved to: {output_file}")

    return all_results


if __name__ == "__main__":
    scan_all_neighborhoods()
