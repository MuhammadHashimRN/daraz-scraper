import joblib
import numpy as np
from sklearn.decomposition import PCA
import umap
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Load processed features
art = joblib.load("artifacts/features.pkl")
X = art["features"].fillna(0).values

# Apply PCA (10 components)
pca = PCA(n_components=10, random_state=42)
X_pca = pca.fit_transform(X)

# Apply UMAP for 2D visualization
u = umap.UMAP(n_components=2, random_state=42)
X_umap = u.fit_transform(X)

# Cluster reduced data to evaluate quality
k = KMeans(n_clusters=5, random_state=42).fit_predict(X_umap)
sil_umap = silhouette_score(X_umap, k) if len(set(k)) > 1 else -1

# Save dimensionality-reduction results
joblib.dump({
    "pca": pca,
    "umap": u,
    "X_pca": X_pca,
    "X_umap": X_umap,
    "sil_umap": sil_umap
}, "artifacts/dims.pkl")

print("PCA explained variance (first 3):", pca.explained_variance_ratio_.cumsum()[:3])
print("UMAP silhouette score:", sil_umap)
