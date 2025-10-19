import requests
from bs4 import BeautifulSoup
import pandas as pd
import time, random, json

SEARCH_TERM = "laptop"  # Change this keyword to scrape different product categories
MAX_PAGES = 5            # Number of search pages to scrape
OUT = "raw_products.csv"
headers = {"User-Agent": "Mozilla/5.0"}

rows = []

for page in range(1, MAX_PAGES + 1):
    url = f"https://www.daraz.pk/catalog/?q={SEARCH_TERM}&page={page}"
    r = requests.get(url, headers=headers, timeout=10)

    if r.status_code != 200:
        time.sleep(2)
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    # Attempt to extract items using CSS selectors
    items = soup.select("div.c2prKC") or soup.select("div.info--ifj7U")

    # If no items found, try parsing embedded JSON data
    if not items:
        scripts = soup.select("script")
        text = ""
        for s in scripts:
            if "window.pageData" in s.text:
                text = s.text
                break
        if not text:
            continue
        start = text.find("{")
        try:
            data = json.loads(text[start:text.rfind("}") + 1])
            for hit in data.get("mods", {}).get("listItems", []):
                rows.append({
                    "title": hit.get("title"),
                    "price": hit.get("price"),
                    "rating": hit.get("rating")
                })
            continue
        except Exception:
            pass

    # Basic HTML fallback scraping
    for it in items:
        title = it.select_one("a").get_text().strip() if it.select_one("a") else ""
        price = it.select_one("span").get_text().strip() if it.select_one("span") else ""
        rows.append({"title": title, "price": price})

    time.sleep(random.uniform(1, 2))  # Be polite to avoid blocking

# Save scraped results
df = pd.DataFrame(rows)
df.to_csv(OUT, index=False)
print("Saved", OUT)
