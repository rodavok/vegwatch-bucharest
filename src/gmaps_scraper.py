import json
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, Page

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def search_restaurants(page: Page, query: str = "restaurants in Bucharest") -> list[dict]:
    """Search Google Maps and return list of restaurant URLs."""
    page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
    time.sleep(2)

    # Accept cookies if prompted
    try:
        page.click("text=Accept all", timeout=3000)
    except:
        pass

    time.sleep(2)

    # Scroll the results panel to load more
    results_selector = 'div[role="feed"]'
    for _ in range(5):
        page.evaluate(f'''
            document.querySelector('{results_selector}')?.scrollBy(0, 1000)
        ''')
        time.sleep(1)

    # Extract restaurant links
    links = page.query_selector_all('a[href*="/maps/place/"]')
    restaurants = []
    seen = set()

    for link in links:
        href = link.get_attribute("href")
        if href and href not in seen:
            seen.add(href)
            name = link.get_attribute("aria-label") or ""
            restaurants.append({"name": name, "url": href})

    return restaurants


def extract_reviews(page: Page, url: str, max_reviews: int = 50) -> dict:
    """Extract reviews from a restaurant page."""
    page.goto(url)
    time.sleep(2)

    # Debug: save screenshot
    page.screenshot(path=str(DATA_DIR / "debug_page.png"))

    # Get basic info
    name = ""
    rating = None
    total_reviews = None
    address = ""

    try:
        name = page.query_selector("h1")
        name = name.inner_text() if name else ""
    except:
        pass

    try:
        rating_el = page.query_selector('div[role="img"][aria-label*="stars"]')
        if rating_el:
            label = rating_el.get_attribute("aria-label")
            rating = float(re.search(r"([\d.]+)", label).group(1))
    except:
        pass

    try:
        review_btn = page.query_selector('button[aria-label*="Reviews"]')
        if review_btn:
            label = review_btn.get_attribute("aria-label")
            match = re.search(r"([\d,]+)", label.replace(",", ""))
            if match:
                total_reviews = int(match.group(1).replace(",", ""))
    except:
        pass

    # Click reviews tab
    try:
        reviews_tab = page.query_selector('button[aria-label*="Reviews"]')
        if reviews_tab:
            reviews_tab.click()
            time.sleep(2)
    except:
        pass

    # Scroll to load more reviews
    reviews_panel = 'div[role="main"]'
    for _ in range(max_reviews // 5):
        page.evaluate(f'''
            document.querySelector('{reviews_panel}')?.scrollBy(0, 1000)
        ''')
        time.sleep(0.5)

    # Expand "More" buttons in reviews
    try:
        more_buttons = page.query_selector_all('button[aria-label="See more"]')
        for btn in more_buttons[:20]:
            try:
                btn.click()
                time.sleep(0.1)
            except:
                pass
    except:
        pass

    # Extract review data
    reviews = []
    review_elements = page.query_selector_all('div[data-review-id]')

    for el in review_elements[:max_reviews]:
        try:
            review = {}

            # Reviewer name
            name_el = el.query_selector('button[data-review-id] > div')
            review["author"] = name_el.inner_text() if name_el else ""

            # Rating
            stars_el = el.query_selector('span[role="img"]')
            if stars_el:
                label = stars_el.get_attribute("aria-label")
                match = re.search(r"(\d)", label)
                review["rating"] = int(match.group(1)) if match else None

            # Text
            text_el = el.query_selector('span[data-expandable-section]')
            review["text"] = text_el.inner_text() if text_el else ""

            # Time
            time_el = el.query_selector('span[class*="rsqaWe"]')
            review["time"] = time_el.inner_text() if time_el else ""

            if review.get("text"):
                reviews.append(review)
        except:
            continue

    # Get coordinates from URL
    lat, lng = None, None
    try:
        current_url = page.url
        match = re.search(r"@([-\d.]+),([-\d.]+)", current_url)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
    except:
        pass

    return {
        "name": name,
        "rating": rating,
        "total_reviews": total_reviews,
        "address": address,
        "lat": lat,
        "lng": lng,
        "reviews": reviews,
        "url": url,
    }


def scrape_bucharest_restaurants(limit: int = 10, reviews_per: int = 30, headless: bool = True):
    """Main scraper function."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = context.new_page()

        print("Searching for restaurants...")
        restaurants = search_restaurants(page, "restaurants in Bucharest Romania")
        print(f"Found {len(restaurants)} restaurants")

        results = []
        for i, rest in enumerate(restaurants[:limit]):
            print(f"[{i+1}/{limit}] Scraping: {rest['name'][:40]}...")
            try:
                data = extract_reviews(page, rest["url"], max_reviews=reviews_per)
                results.append(data)
                print(f"  → {len(data['reviews'])} reviews, rating: {data['rating']}")
            except Exception as e:
                print(f"  → Error: {e}")
            time.sleep(1)

        context.close()
        browser.close()

        # Save results
        output_file = DATA_DIR / "bucharest_restaurants.json"
        output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"\nSaved {len(results)} restaurants to {output_file}")

        return results


if __name__ == "__main__":
    scrape_bucharest_restaurants(limit=5, reviews_per=20)
