import pandas as pd
import re

IN_FILE = "raw_products.csv"
OUT_FILE = "processed_products.csv"

df = pd.read_csv(IN_FILE, encoding="utf-8")
print(f"Loaded {len(df)} products")

def extract_ram(text):
    text = str(text).lower()
    m = re.search(r"(\d+)\s?gb\s?ram", text)
    if m: return int(m.group(1))
    m = re.search(r"ram\s?(\d+)\s?gb", text)
    return int(m.group(1)) if m else None

def extract_storage(text):
    text = str(text).lower()
    # Check for TB first
    m = re.search(r"(\d+)\s?tb", text)
    if m: return int(m.group(1)) * 1024
    m = re.search(r"(\d+)\s?gb", text)
    return int(m.group(1)) if m else None

def extract_cpu(text):
    t = str(text).lower()
    if "i9" in t: return "i9"
    if "i7" in t: return "i7"
    if "i5" in t: return "i5"
    if "i3" in t: return "i3"
    if "ryzen 9" in t: return "ryzen9"
    if "ryzen 7" in t: return "ryzen7"
    if "ryzen 5" in t: return "ryzen5"
    if "ryzen 3" in t: return "ryzen3"
    return "other"

# Apply extraction
df["ram_gb"] = df["title"].apply(extract_ram)
df["storage_gb"] = df["title"].apply(extract_storage)
df["cpu"] = df["title"].apply(extract_cpu)

# Fill missing numeric values
df["rating"] = df["rating"].fillna(0)
df["reviews"] = df["reviews"].fillna(0)

# Drop rows without price (should be very few)
df = df.dropna(subset=["price"])

# Fill missing numeric values
df["ram_gb"] = df["ram_gb"].fillna(0)
df["storage_gb"] = df["storage_gb"].fillna(0)
df["rating"] = df["rating"].fillna(0)
df["reviews"] = df["reviews"].fillna(0)

df.to_csv(OUT_FILE, index=False, encoding="utf-8")
print(f"✅ Saved processed dataset to {OUT_FILE} ({len(df)} rows)")
print(df.head(5))
