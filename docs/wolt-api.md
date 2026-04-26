# Wolt API (formerly Tazz)

Tazz was acquired by Wolt (DoorDash). tazz.ro redirects to wolt.com/ro/rou.

## Working Endpoint

```
GET https://restaurant-api.wolt.com/v1/pages/restaurants?lat={lat}&lon={lon}
```

Optional params: `limit`, likely pagination params.

### Example: Bucharest
```
lat=44.4268&lon=26.1025
```

## Response Structure

Per restaurant:
```json
{
  "name": "McDonald's Unirea",
  "id": "67ed2703c86a467a0cecf40a",
  "slug": "mcdonalds-unirea-67ed2703c86a467a0cecf40a",
  "address": "...",
  "location": [longitude, latitude],
  "rating": {
    "score": 0-10,
    "volume": number_of_ratings,
    "rating": 1-5
  },
  "tags": ["pizza", "burger", "kebab"],
  "price_range": 1-4,
  "estimate": delivery_minutes,
  "estimate_range": "min-max",
  "online": boolean,
  "delivers": boolean,
  "image": "imageproxy.wolt.com/...",
  "short_description": "...",
  "country": "ROU",
  "currency": "RON"
}
```

## Limitations

- **No review text** — only aggregate ratings
- Individual venue endpoints (v1/pages/venue/slug/...) return 404
- Menu data not accessible via this endpoint
- No dietary tags (vegetarian/vegan) in listing data

## Useful For

- Quality zone mapping (ratings + coordinates)
- Cuisine distribution analysis (tags)
- Price range analysis
- Delivery coverage analysis

## Not Useful For

- Review sentiment analysis (no text)
- Vegetarian option detection (no menu/dietary data)
