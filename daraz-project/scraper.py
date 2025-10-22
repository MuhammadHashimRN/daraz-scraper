# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import time
# import random
# import json

# def scrape_laptops(search_term="laptop", max_pages=5, out_file="raw_products.csv"):
#     """
#     Scrape Daraz for laptop products.
    
#     Args:
#         search_term (str): Product search term
#         max_pages (int): Number of pages to scrape
#         out_file (str): Output CSV filename
    
#     Returns:
#         int: Number of products scraped
#     """
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
#     }

#     rows = []

#     for page in range(1, max_pages + 1):
#         print(f"Scraping page {page}...")
#         url = f"https://www.daraz.pk/catalog/?q={search_term}&page={page}&ajax=true"

#         try:
#             r = requests.get(url, headers=headers, timeout=10)
#         except Exception as e:
#             print(f"❌ Request failed on page {page}: {e}")
#             continue

#         if r.status_code != 200:
#             print(f"⚠️ Skipping page {page} — HTTP {r.status_code}")
#             time.sleep(2)
#             continue

#         try:
#             data = r.json()
#             items = data.get("mods", {}).get("listItems", [])
#             if not items:
#                 print(f"⚠️ No products found on page {page}")
#                 continue

#             for hit in items:
#                 rows.append({
#                     "title": hit.get("name"),
#                     "brand": hit.get("brandName"),
#                     "price": hit.get("price"),
#                     "rating": hit.get("ratingScore"),
#                     "reviews": hit.get("review"),
#                     "url": "https:" + hit.get("productUrl", "")
#                 })
#         except json.JSONDecodeError:
#             print(f"❌ Failed to parse JSON on page {page}")
#         except Exception as e:
#             print(f"❌ Unexpected error: {e}")

#         time.sleep(random.uniform(1, 2))

#     # Save to CSV
#     df = pd.DataFrame(rows)
#     df.to_csv(out_file, index=False)
#     print(f"✅ Saved {len(df)} products to {out_file}")
    
#     return len(df)


# # Allow script to run standalone
# if __name__ == "__main__":
#     num_products = scrape_laptops(search_term="laptop", max_pages=5, out_file="raw_products.csv")
#     print(f"Total products scraped: {num_products}")

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
import os
from datetime import datetime
import hashlib

def download_image(url, product_id, images_dir="static/images"):
    """Download product image and return local path"""
    try:
        os.makedirs(images_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"{product_id}_{hashlib.md5(url.encode()).hexdigest()[:8]}.jpg"
        filepath = os.path.join(images_dir, filename)
        
        # Skip if already downloaded
        if os.path.exists(filepath):
            return f"/images/{filename}"
        
        # Download image
        response = requests.get(url, timeout=10, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return f"/images/{filename}"
    except Exception as e:
        print(f"Failed to download image: {e}")
    return None

def save_price_history(products, history_file="price_history.csv"):
    """Track price changes over time"""
    timestamp = datetime.now()
    
    # Load existing history
    if os.path.exists(history_file):
        history_df = pd.read_csv(history_file)
    else:
        history_df = pd.DataFrame()
    
    # Add new entries
    for product in products:
        new_entry = {
            'timestamp': timestamp,
            'product_id': product.get('url', '').split('/')[-1].split('.')[0],
            'title': product.get('title'),
            'price': product.get('price'),
            'rating': product.get('rating'),
            'brand': product.get('brand')
        }
        history_df = pd.concat([history_df, pd.DataFrame([new_entry])], ignore_index=True)
    
    history_df.to_csv(history_file, index=False)
    return history_df

def get_price_changes(history_file="price_history.csv"):
    """Analyze price changes over time"""
    if not os.path.exists(history_file):
        return []
    
    df = pd.read_csv(history_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    changes = []
    for product_id in df['product_id'].unique():
        product_data = df[df['product_id'] == product_id].sort_values('timestamp')
        if len(product_data) > 1:
            latest = product_data.iloc[-1]
            previous = product_data.iloc[-2]
            price_change = latest['price'] - previous['price']
            
            if abs(price_change) > 0:
                changes.append({
                    'title': latest['title'],
                    'old_price': previous['price'],
                    'new_price': latest['price'],
                    'change': price_change,
                    'change_percent': (price_change / previous['price']) * 100,
                    'timestamp': latest['timestamp']
                })
    
    return sorted(changes, key=lambda x: abs(x['change_percent']), reverse=True)

def scrape_laptops(search_term="laptop", max_pages=5, out_file="raw_products.csv", download_images=True):
    """
    Scrape Daraz for laptop products with image downloading and price tracking.
    
    Args:
        search_term (str): Product search term
        max_pages (int): Number of pages to scrape
        out_file (str): Output CSV filename
        download_images (bool): Whether to download product images
    
    Returns:
        int: Number of products scraped
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }
    
    os.makedirs("static/images", exist_ok=True) 
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

            for idx, hit in enumerate(items):
                product_id = f"p{page}_{idx}"
                image_url = hit.get("image", "")
                
                # Download image if enabled
                local_image_path = None
                if download_images and image_url:
                    local_image_path = download_image(image_url, product_id)
                
                rows.append({
                    "product_id": product_id,
                    "title": hit.get("name"),
                    "brand": hit.get("brandName"),
                    "price": hit.get("price"),
                    "rating": hit.get("ratingScore"),
                    "reviews": hit.get("review"),
                    "url": "https:" + hit.get("productUrl", ""),
                    "image_url": image_url,
                    "local_image": local_image_path or "",
                    "scraped_at": datetime.now().isoformat()
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
    
    # Track price history
    save_price_history(rows)
    
    return len(df)


# Allow script to run standalone
if __name__ == "__main__":
    num_products = scrape_laptops(search_term="laptop", max_pages=5, out_file="raw_products.csv")
    print(f"Total products scraped: {num_products}")
    
    # Show price changes
    changes = get_price_changes()
    if changes:
        print("\n📊 Price Changes Detected:")
        for change in changes[:5]:
            print(f"  {change['title']}: ${change['old_price']} → ${change['new_price']} ({change['change_percent']:+.1f}%)")