import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json

def scrape_laptops(search_term="laptop", max_pages=5, out_file="raw_products.csv"):
    """
    Scrape Daraz for laptop products.
    
    Args:
        search_term (str): Product search term
        max_pages (int): Number of pages to scrape
        out_file (str): Output CSV filename
    
    Returns:
        int: Number of products scraped
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    rows = []

    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        url = f"https://www.daraz.pk/catalog/?q={search_term}&page={page}&ajax=true"

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
    df.to_csv(out_file, index=False)
    print(f"✅ Saved {len(df)} products to {out_file}")
    
    return len(df)


# Allow script to run standalone
if __name__ == "__main__":
    num_products = scrape_laptops(search_term="laptop", max_pages=5, out_file="raw_products.csv")
    print(f"Total products scraped: {num_products}")