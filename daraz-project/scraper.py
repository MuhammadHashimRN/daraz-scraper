# scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time, random, json

def run():
    SEARCH_TERM = "laptop"
    MAX_PAGES = 5
    OUT = "raw_products.csv"
    headers = {"User-Agent": "Mozilla/5.0"}

    rows = []

    for page in range(1, MAX_PAGES + 1):
        print(f"Scraping page {page}...")
        url = f"https://www.daraz.pk/catalog/?q={SEARCH_TERM}&page={page}"
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            time.sleep(2)
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("div.c2prKC") or soup.select("div.info--ifj7U")

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

        for it in items:
            title = it.select_one("a").get_text().strip() if it.select_one("a") else ""
            price = it.select_one("span").get_text().strip() if it.select_one("span") else ""
            rows.append({"title": title, "price": price})

        time.sleep(random.uniform(1, 2))

    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    print(f"✅ Saved {len(rows)} products to {OUT}")
