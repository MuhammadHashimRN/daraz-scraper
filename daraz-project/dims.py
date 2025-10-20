import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Flask
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import umap
import numpy as np

def run(input_file="processed_products.csv"):
    """
    Perform dimensionality reduction (PCA & UMAP) and generate visualizations.
    
    Args:
        input_file (str): Path to processed CSV file
    
    Returns:
        dict: Dictionary containing paths to generated plot files
    """
    # Load data
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} products")
    
    # Fill missing numeric values
    df["ram_gb"] = df["ram_gb"].fillna(0)
    df["storage_gb"] = df["storage_gb"].fillna(0)
    df["rating"] = df["rating"].fillna(0)
    df["reviews"] = df["reviews"].fillna(0)
    df["price"] = df["price"].fillna(0)
    
    # Prepare features
    features = ["price", "ram_gb", "storage_gb", "rating", "reviews"]
    X = df[features]
    X_scaled = StandardScaler().fit_transform(X)
    
    # Dictionary to store generated plot paths
    plots = {}
    
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
        plt.arrow(0, 0, loadings["PC1"].iloc[i]*5, loadings["PC2"].iloc[i]*5, 
                 color='r', alpha=0.5, head_width=0.1)
        plt.text(loadings["PC1"].iloc[i]*5.2, loadings["PC2"].iloc[i]*5.2, 
                feature, color='r')
    plt.xlabel(f"PC1 ({pc1_top2})")
    plt.ylabel(f"PC2 ({pc2_top2})")
    plt.title("PCA of Daraz Laptops")
    plt.grid(True)
    plt.tight_layout()
    pca_path = "pca_combined.png"
    plt.savefig(pca_path)
    plt.close()
    plots["pca"] = pca_path
    print(f"✅ PCA plot saved as {pca_path}")
    
    # ---------------- UMAP ----------------
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    umap_result = reducer.fit_transform(X_scaled)
    df["UMAP1"], df["UMAP2"] = umap_result[:,0], umap_result[:,1]
    
    # Individual UMAP heatmaps
    for feat in ["ram_gb", "storage_gb", "price"]:
        plt.figure(figsize=(10,8))
        plt.scatter(df["UMAP1"], df["UMAP2"], c=df[feat], cmap="plasma", 
                   s=60, alpha=0.8)
        plt.colorbar(label=feat)
        plt.title(f"UMAP of Daraz Laptops colored by {feat}")
        plt.xlabel("UMAP1")
        plt.ylabel("UMAP2")
        plt.tight_layout()
        umap_path = f"umap_heatmap_{feat}.png"
        plt.savefig(umap_path)
        plt.close()
        plots[f"umap_{feat}"] = umap_path
        print(f"✅ UMAP heatmap saved as {umap_path}")
    
    # Composite heatmap (price + RAM + storage)
    df["composite_score"] = (
        (df["price"] - df["price"].min()) / (df["price"].max() - df["price"].min()) +
        (df["ram_gb"] - df["ram_gb"].min()) / (df["ram_gb"].max() - df["ram_gb"].min()) +
        (df["storage_gb"] - df["storage_gb"].min()) / (df["storage_gb"].max() - df["storage_gb"].min())
    )
    
    plt.figure(figsize=(10,8))
    plt.scatter(df["UMAP1"], df["UMAP2"], c=df["composite_score"], 
               cmap="plasma", s=80, alpha=0.8)
    plt.colorbar(label="Composite Score (price + RAM + storage)")
    plt.title("UMAP of Daraz Laptops (Composite Heatmap)")
    plt.xlabel("UMAP1")
    plt.ylabel("UMAP2")
    plt.tight_layout()
    composite_path = "umap_composite.png"
    plt.savefig(composite_path)
    plt.close()
    plots["umap_composite"] = composite_path
    print(f"✅ Composite UMAP plot saved as {composite_path}")
    
    print("✅ All PCA + UMAP plots generated and saved successfully!")
    
    return plots

# Allow script to run standalone
if __name__ == "__main__":
    generated_plots = run(input_file="processed_products.csv")
    print(f"Generated {len(generated_plots)} plots:")
    for name, path in generated_plots.items():
        print(f"  - {name}: {path}")