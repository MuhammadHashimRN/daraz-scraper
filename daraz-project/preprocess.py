import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Load scraped data
df = pd.read_csv("raw_products.csv")

# Clean price column to extract numeric values
df["price_num"] = df["price"].astype(str).str.replace("[^0-9.]", "", regex=True)
df["price_num"] = pd.to_numeric(df["price_num"], errors="coerce").fillna(-1)

# Feature engineering on title text
df["title"] = df["title"].astype(str)
df["title_len"] = df["title"].str.len()
df["word_count"] = df["title"].str.split().map(len)
df["has_digit"] = df["title"].str.contains(r"\d")

# Create TF-IDF text representation (top 200 words)
tf = TfidfVectorizer(max_features=200)
X_text = tf.fit_transform(df["title"].fillna(""))

# Merge all numeric and text-based features
X_text_df = pd.DataFrame(X_text.toarray(), columns=[f"tf_{i}" for i in range(X_text.shape[1])])
features = pd.concat([
    df[["price_num", "title_len", "word_count", "has_digit"]].reset_index(drop=True),
    X_text_df.reset_index(drop=True)
], axis=1)

# Save processed features and vectorizer for reuse
joblib.dump({"features": features, "raw": df, "tf": tf}, "artifacts/features.pkl")
print("Saved artifacts/features.pkl")
