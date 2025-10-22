import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
import umap
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os

def perform_clustering(X_scaled, df, n_clusters=5):
    """
    Perform K-Means and DBSCAN clustering on scaled features.
    
    Args:
        X_scaled: Standardized feature matrix
        df: Original dataframe
        n_clusters: Number of clusters for K-Means
    
    Returns:
        Enhanced dataframe with cluster labels and cluster statistics
    """
    # K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans_labels = kmeans.fit_predict(X_scaled)
    kmeans_score = silhouette_score(X_scaled, kmeans_labels)
    
    # DBSCAN clustering
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    dbscan_labels = dbscan.fit_predict(X_scaled)
    
    # Add to dataframe
    df['cluster_kmeans'] = kmeans_labels
    df['cluster_dbscan'] = dbscan_labels
    
    print(f"✅ K-Means clustering: {n_clusters} clusters, silhouette score: {kmeans_score:.3f}")
    print(f"✅ DBSCAN clustering: {len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)} clusters")
    
    return df, kmeans_labels, dbscan_labels, kmeans_score

def create_interactive_pca(df, features):
    """Create interactive PCA plot with Plotly"""
    fig = px.scatter(
        df,
        x='PCA1',
        y='PCA2',
        color='cluster_kmeans',
        size='price',
        hover_data=['title', 'brand', 'ram_gb', 'storage_gb', 'price', 'rating'],
        title='Interactive PCA Analysis with Clustering',
        labels={'cluster_kmeans': 'Cluster'},
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=700,
        showlegend=True,
        hovermode='closest'
    )
    
    fig.write_html('static/plots/pca_interactive.html')
    print("✅ Interactive PCA saved")
    return fig

def create_3d_umap(df, umap_3d_result):
    """Create 3D UMAP visualization"""
    fig = go.Figure(data=[go.Scatter3d(
        x=umap_3d_result[:, 0],
        y=umap_3d_result[:, 1],
        z=umap_3d_result[:, 2],
        mode='markers',
        marker=dict(
            size=5,
            color=df['price'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Price")
        ),
        text=df['title'],
        hovertemplate='<b>%{text}</b><br>' +
                      'Price: $%{marker.color:.2f}<br>' +
                      '<extra></extra>'
    )])
    
    fig.update_layout(
        title='3D UMAP Visualization',
        scene=dict(
            xaxis_title='UMAP 1',
            yaxis_title='UMAP 2',
            zaxis_title='UMAP 3'
        ),
        template='plotly_dark',
        height=700
    )
    
    fig.write_html('static/plots/umap_3d.html')
    print("✅ 3D UMAP saved")
    return fig

def create_cluster_analysis_plots(df):
    """Create detailed cluster analysis visualizations"""
    # Cluster statistics
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Average Price by Cluster', 'Average RAM by Cluster',
                       'Average Storage by Cluster', 'Average Rating by Cluster'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    cluster_stats = df.groupby('cluster_kmeans').agg({
        'price': 'mean',
        'ram_gb': 'mean',
        'storage_gb': 'mean',
        'rating': 'mean'
    }).reset_index()
    
    # Price
    fig.add_trace(
        go.Bar(x=cluster_stats['cluster_kmeans'], y=cluster_stats['price'],
               name='Price', marker_color='lightblue'),
        row=1, col=1
    )
    
    # RAM
    fig.add_trace(
        go.Bar(x=cluster_stats['cluster_kmeans'], y=cluster_stats['ram_gb'],
               name='RAM', marker_color='lightgreen'),
        row=1, col=2
    )
    
    # Storage
    fig.add_trace(
        go.Bar(x=cluster_stats['cluster_kmeans'], y=cluster_stats['storage_gb'],
               name='Storage', marker_color='lightcoral'),
        row=2, col=1
    )
    
    # Rating
    fig.add_trace(
        go.Bar(x=cluster_stats['cluster_kmeans'], y=cluster_stats['rating'],
               name='Rating', marker_color='lightyellow'),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text="Cluster Analysis Dashboard",
        template='plotly_dark',
        height=800,
        showlegend=False
    )
    
    fig.write_html('static/plots/cluster_analysis.html')
    print("✅ Cluster analysis dashboard saved")
    return fig

def create_price_distribution_plot(df):
    """Create price distribution by cluster"""
    fig = px.box(
        df,
        x='cluster_kmeans',
        y='price',
        color='cluster_kmeans',
        title='Price Distribution by Cluster',
        labels={'cluster_kmeans': 'Cluster', 'price': 'Price ($)'}
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=600,
        showlegend=False
    )
    
    fig.write_html('static/plots/price_distribution.html')
    print("✅ Price distribution plot saved")
    return fig

def run(input_file="processed_products.csv"):
    """
    Perform dimensionality reduction, clustering, and generate visualizations.
    
    Args:
        input_file (str): Path to processed CSV file
    
    Returns:
        dict: Dictionary containing paths to generated plot files and statistics
    """
    # Create plots directory
    os.makedirs('static/plots', exist_ok=True)
    
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
    
    # Dictionary to store results
    plots = {}
    stats = {}
    
    # ==================== CLUSTERING ====================
    df, kmeans_labels, dbscan_labels, silhouette = perform_clustering(X_scaled, df, n_clusters=5)
    stats['n_clusters'] = 5
    stats['silhouette_score'] = float(silhouette)
    
    # ==================== PCA ====================
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)
    df["PCA1"], df["PCA2"] = pca_result[:,0], pca_result[:,1]
    
    stats['pca_variance_explained'] = [float(x) for x in pca.explained_variance_ratio_]
    
    # Feature loadings for PCA arrows
    loadings = pd.DataFrame(pca.components_.T, columns=["PC1", "PC2"], index=features)
    
    # Dominant features for axes
    abs_loadings = loadings.abs()
    pc1_top2 = "+".join(abs_loadings["PC1"].nlargest(2).index)
    pc2_top2 = "+".join(abs_loadings["PC2"].nlargest(2).index)
    
    # Static PCA plot with clustering
    plt.figure(figsize=(12,10))
    scatter = plt.scatter(df["PCA1"], df["PCA2"], c=df["cluster_kmeans"], 
                         cmap='viridis', s=50, alpha=0.7, edgecolors='black', linewidth=0.5)
    plt.colorbar(scatter, label='Cluster')
    
    # Add feature vectors
    scale_factor = 5
    for i, feature in enumerate(features):
        plt.arrow(0, 0, 
                 loadings["PC1"].iloc[i] * scale_factor, 
                 loadings["PC2"].iloc[i] * scale_factor, 
                 color='red', alpha=0.6, head_width=0.15, linewidth=2.5)
        plt.text(loadings["PC1"].iloc[i] * scale_factor * 1.15, 
                loadings["PC2"].iloc[i] * scale_factor * 1.15, 
                feature, color='darkred', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    plt.xlabel(f"PC1 ({pc1_top2}) - {pca.explained_variance_ratio_[0]:.2%} variance", fontsize=12)
    plt.ylabel(f"PC2 ({pc2_top2}) - {pca.explained_variance_ratio_[1]:.2%} variance", fontsize=12)
    plt.title("PCA Analysis with K-Means Clustering", fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    pca_path = "static/plots/pca_combined.png"
    plt.savefig(pca_path, dpi=150, bbox_inches='tight')
    plt.close()
    plots["pca"] = pca_path
    print(f"✅ Static PCA plot saved")
    
    # Interactive PCA
    create_interactive_pca(df, features)
    plots["pca_interactive"] = "static/plots/pca_interactive.html"
    
    # ==================== UMAP 2D ====================
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    umap_result = reducer.fit_transform(X_scaled)
    df["UMAP1"], df["UMAP2"] = umap_result[:,0], umap_result[:,1]
    
    # Individual UMAP heatmaps
    for feat in ["ram_gb", "storage_gb", "price"]:
        plt.figure(figsize=(12,10))
        scatter = plt.scatter(df["UMAP1"], df["UMAP2"], c=df[feat], 
                            cmap="plasma", s=60, alpha=0.8, edgecolors='black', linewidth=0.5)
        cbar = plt.colorbar(scatter, label=feat)
        cbar.ax.tick_params(labelsize=10)
        plt.title(f"UMAP colored by {feat}", fontsize=16, fontweight='bold')
        plt.xlabel("UMAP1", fontsize=12)
        plt.ylabel("UMAP2", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        umap_path = f"static/plots/umap_heatmap_{feat}.png"
        plt.savefig(umap_path, dpi=150, bbox_inches='tight')
        plt.close()
        plots[f"umap_{feat}"] = umap_path
        print(f"✅ UMAP {feat} heatmap saved")
    
    # Composite heatmap
    df["composite_score"] = (
        (df["price"] - df["price"].min()) / (df["price"].max() - df["price"].min() + 0.001) +
        (df["ram_gb"] - df["ram_gb"].min()) / (df["ram_gb"].max() - df["ram_gb"].min() + 0.001) +
        (df["storage_gb"] - df["storage_gb"].min()) / (df["storage_gb"].max() - df["storage_gb"].min() + 0.001)
    )
    
    plt.figure(figsize=(12,10))
    scatter = plt.scatter(df["UMAP1"], df["UMAP2"], c=df["composite_score"], 
                         cmap="plasma", s=80, alpha=0.8, edgecolors='black', linewidth=0.5)
    cbar = plt.colorbar(scatter, label="Composite Score")
    cbar.ax.tick_params(labelsize=10)
    plt.title("UMAP Composite Heatmap", fontsize=16, fontweight='bold')
    plt.xlabel("UMAP1", fontsize=12)
    plt.ylabel("UMAP2", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    composite_path = "static/plots/umap_composite.png"
    plt.savefig(composite_path, dpi=150, bbox_inches='tight')
    plt.close()
    plots["umap_composite"] = composite_path
    print(f"✅ UMAP composite plot saved")
    
    # ==================== UMAP 3D ====================
    print("Generating 3D UMAP...")
    reducer_3d = umap.UMAP(n_components=3, n_neighbors=15, min_dist=0.1, random_state=42)
    umap_3d_result = reducer_3d.fit_transform(X_scaled)
    create_3d_umap(df, umap_3d_result)
    plots["umap_3d"] = "static/plots/umap_3d.html"
    
    # ==================== CLUSTER ANALYSIS ====================
    create_cluster_analysis_plots(df)
    plots["cluster_analysis"] = "static/plots/cluster_analysis.html"
    
    create_price_distribution_plot(df)
    plots["price_distribution"] = "static/plots/price_distribution.html"
    
    # Save enhanced dataframe
    df.to_csv('processed_products_enhanced.csv', index=False)
    print(f"✅ Enhanced CSV saved with clustering data")
    
    # Save statistics
    stats['total_products'] = len(df)
    stats['cluster_sizes'] = {int(k): int(v) for k, v in df['cluster_kmeans'].value_counts().to_dict().items()}
    stats['features_used'] = features
    
    with open('static/plots/stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ All PCA + UMAP plots generated successfully!")
    print("="*60)
    print(f"📊 Total Visualizations: {len(plots)}")
    print(f"📈 Silhouette Score: {silhouette:.3f}")
    print(f"🎯 Number of Clusters: {stats['n_clusters']}")
    print(f"📦 Products Analyzed: {stats['total_products']}")
    print("="*60)
    
    return {"plots": plots, "stats": stats}


if __name__ == "__main__":
    result = run(input_file="processed_products.csv")
    print(f"\n📊 Statistics Summary:")
    print(json.dumps(result['stats'], indent=2))