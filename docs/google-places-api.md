# Google Places API

## Overview

Best option for review text analysis in Romania. Requires Google Cloud account with billing enabled.

## Pricing (as of March 2025)

- Old $200/month credit replaced with free calls per SKU
- **Essentials tier: 10K free calls/month per SKU**
- Reviews fall under "Atmosphere" billing tier

## Endpoints

### 1. Nearby Search
Find restaurants in an area.

```
GET https://maps.googleapis.com/maps/api/place/nearbysearch/json
  ?location={lat},{lng}
  &radius={meters}
  &type=restaurant
  &key={API_KEY}
```

Returns: place_id, name, rating, user_ratings_total, types, geometry, price_level

### 2. Place Details
Get reviews for a specific place.

```
GET https://maps.googleapis.com/maps/api/place/details/json
  ?place_id={place_id}
  &fields=name,rating,reviews,types
  &key={API_KEY}
```

Returns up to **5 reviews** per place:
```json
{
  "reviews": [
    {
      "author_name": "...",
      "rating": 1-5,
      "text": "Review content...",
      "time": unix_timestamp,
      "relative_time_description": "2 months ago",
      "language": "ro"
    }
  ]
}
```

## Workflow

```
1. Nearby Search (area) → list of place_ids
2. Place Details (each place_id) → reviews, full data
```

## Field Categories (billing)

- **Basic**: name, geometry, place_id, types (cheapest)
- **Contact**: phone, website, opening_hours
- **Atmosphere**: reviews, rating, price_level (additional cost)

## Limitations

- Max 5 reviews per place
- No historical review access
- Requires billing-enabled account

## Useful For

- Review sentiment analysis (has actual text)
- Vegetarian detection (parse review text + place types)
- Quality zone mapping
- Full Romania coverage
