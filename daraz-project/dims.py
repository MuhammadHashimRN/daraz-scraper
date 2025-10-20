import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import umap
import numpy as np

IN_FILE = "processed_products.csv"
df = pd.read_csv(IN_FILE)
print(f"Loaded {len(df)} products")

# Fill missing numeric values
df["ram_gb"] = df["ram_gb"].fillna(0)
df["storage_gb"] = df["storage_gb"].fillna(0)
df["rating"] = df["rating"].fillna(0)
df["reviews"] = df["reviews"].fillna(0)
df["price"] = df["price"].fillna(0)

features = ["price", "ram_gb", "storage_gb", "rating", "reviews"]
X = df[features]
X_scaled = StandardScaler().fit_transform(X)

# ---------------- PCA ----------------
pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)
df["PCA1"], df["PCA2"] = pca_result[:,0], pca_result[:,1]

# Feature loadings for PCA arrows
loadings = pd.DataFrame(pca.components_.T, columns=["PC1", "PC2"], index=features)

# Dominant features for axes
abs_loadings = loadings.abs()
pc1_top2 = "+".join(abs_loadings["PC1"].nlargest(2).index)
pc2_top2 = "+".join(abs_loadings["PC2"].nlargest(2).index)

# PCA plot
plt.figure(figsize=(10,8))
plt.scatter(df["PCA1"], df["PCA2"], s=50, alpha=0.7, color="blue")
for i, feature in enumerate(features):
    plt.arrow(0, 0, loadings["PC1"].iloc[i]*5, loadings["PC2"].iloc[i]*5, color='r', alpha=0.5, head_width=0.1)
    plt.text(loadings["PC1"].iloc[i]*5.2, loadings["PC2"].iloc[i]*5.2, feature, color='r')
plt.xlabel(f"PC1 ({pc1_top2})")
plt.ylabel(f"PC2 ({pc2_top2})")
plt.title("PCA of Daraz Laptops")
plt.grid(True)
plt.tight_layout()
plt.savefig("pca_combined.png")
plt.close()
print("✅ PCA plot saved as pca_combined.png")

# ---------------- UMAP ----------------
reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
umap_result = reducer.fit_transform(X_scaled)
df["UMAP1"], df["UMAP2"] = umap_result[:,0], umap_result[:,1]

# Individual UMAP heatmaps
for feat in ["ram_gb", "storage_gb", "price"]:
    plt.figure(figsize=(10,8))
    plt.scatter(df["UMAP1"], df["UMAP2"], c=df[feat], cmap="plasma", s=60, alpha=0.8)
    plt.colorbar(label=feat)
    plt.title(f"UMAP of Daraz Laptops colored by {feat}")
    plt.xlabel("UMAP1")
    plt.ylabel("UMAP2")
    plt.tight_layout()
    plt.savefig(f"umap_heatmap_{feat}.png")
    plt.close()
    print(f"✅ UMAP heatmap saved as umap_heatmap_{feat}.png")

# Composite heatmap (price + RAM + storage)
df["composite_score"] = (
    (df["price"] - df["price"].min()) / (df["price"].max() - df["price"].min()) +
    (df["ram_gb"] - df["ram_gb"].min()) / (df["ram_gb"].max() - df["ram_gb"].min()) +
    (df["storage_gb"] - df["storage_gb"].min()) / (df["storage_gb"].max() - df["storage_gb"].min())
)

plt.figure(figsize=(10,8))
plt.scatter(df["UMAP1"], df["UMAP2"], c=df["composite_score"], cmap="plasma", s=80, alpha=0.8)
plt.colorbar(label="Composite Score (price + RAM + storage)")
plt.title("UMAP of Daraz Laptops (Composite Heatmap)")
plt.xlabel("UMAP1")
plt.ylabel("UMAP2")
plt.tight_layout()
plt.savefig("umap_composite.png")
plt.close()
print("✅ Composite UMAP plot saved as umap_composite.png")

print("✅ All PCA + UMAP plots generated and saved successfully!")
