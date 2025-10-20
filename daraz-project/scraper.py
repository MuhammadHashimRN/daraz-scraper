import requests
from bs4 import BeautifulSoup
import pandas as pd
import time, random, json

SEARCH_TERM = "laptop"
MAX_PAGES = 5
OUT = "raw_products.csv"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

rows = []

for page in range(1, MAX_PAGES + 1):
    print(f"Scraping page {page}...")
    url = f"https://www.daraz.pk/catalog/?q={SEARCH_TERM}&page={page}&ajax=true"

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"❌ Request failed on page {page}: {e}")
        continue

    if r.status_code != 200:
        print(f"⚠️ Skipping page {page} — HTTP {r.status_code}")
        time.sleep(2)
        continue

    try:
        data = r.json()
        items = data.get("mods", {}).get("listItems", [])
        if not items:
            print(f"⚠️ No products found on page {page}")
            continue

        for hit in items:
            rows.append({
                "title": hit.get("name"),
                "brand": hit.get("brandName"),
                "price": hit.get("price"),
                "rating": hit.get("ratingScore"),
                "reviews": hit.get("review"),
                "url": "https:" + hit.get("productUrl", "")
            })
    except json.JSONDecodeError:
        print(f"❌ Failed to parse JSON on page {page}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    time.sleep(random.uniform(1, 2))

# Save to CSV
df = pd.DataFrame(rows)
df.to_csv(OUT, index=False)
print(f"✅ Saved {len(df)} products to {OUT}")
