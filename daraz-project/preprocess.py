import pandas as pd
import re

def extract_ram(text):
    """Extract RAM size in GB from product title."""
    text = str(text).lower()
    m = re.search(r"(\d+)\s?gb\s?ram", text)
    if m: 
        return int(m.group(1))
    m = re.search(r"ram\s?(\d+)\s?gb", text)
    return int(m.group(1)) if m else None

def extract_storage(text):
    """Extract storage size in GB from product title."""
    text = str(text).lower()
    # Check for TB first
    m = re.search(r"(\d+)\s?tb", text)
    if m: 
        return int(m.group(1)) * 1024
    m = re.search(r"(\d+)\s?gb", text)
    return int(m.group(1)) if m else None

def extract_cpu(text):
    """Extract CPU type from product title."""
    t = str(text).lower()
    if "i9" in t: 
        return "i9"
    if "i7" in t: 
        return "i7"
    if "i5" in t: 
        return "i5"
    if "i3" in t: 
        return "i3"
    if "ryzen 9" in t: 
        return "ryzen9"
    if "ryzen 7" in t: 
        return "ryzen7"
    if "ryzen 5" in t: 
        return "ryzen5"
    if "ryzen 3" in t: 
        return "ryzen3"
    return "other"

def run(input_file="raw_products.csv", output_file="processed_products.csv"):
    """
    Process raw product data and extract features.
    
    Args:
        input_file (str): Path to raw CSV file
        output_file (str): Path to save processed CSV
    
    Returns:
        int: Number of rows in processed dataset
    """
    # Load data
    df = pd.read_csv(input_file, encoding="utf-8")
    print(f"Loaded {len(df)} products")
    
    # Apply extraction functions
    df["ram_gb"] = df["title"].apply(extract_ram)
    df["storage_gb"] = df["title"].apply(extract_storage)
    df["cpu"] = df["title"].apply(extract_cpu)
    
    # Drop rows without price (should be very few)
    df = df.dropna(subset=["price"])
    
    # Fill missing numeric values
    df["ram_gb"] = df["ram_gb"].fillna(0)
    df["storage_gb"] = df["storage_gb"].fillna(0)
    df["rating"] = df["rating"].fillna(0)
    df["reviews"] = df["reviews"].fillna(0)
    
    # Save processed data
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"✅ Saved processed dataset to {output_file} ({len(df)} rows)")
    print(df.head(5))
    
    return len(df)

# Allow script to run standalone
if __name__ == "__main__":
    num_rows = run(input_file="raw_products.csv", output_file="processed_products.csv")
    print(f"Total rows processed: {num_rows}")