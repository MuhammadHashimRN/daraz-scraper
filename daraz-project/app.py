from flask import Flask, jsonify, request
import joblib
import pandas as pd

app = Flask(__name__)

# Load precomputed artifacts
art = joblib.load("artifacts/features.pkl")
dims = joblib.load("artifacts/dims.pkl")
raw = art["raw"]

@app.route("/status")
def status():
    """Health check endpoint"""
    return jsonify({"status": "ok", "rows": len(raw)})

@app.route("/products")
def products():
    """Return top N products with optional PCA/UMAP embeddings"""
    n = int(request.args.get("n", 10))
    reduce = request.args.get("reduce", "")
    out = raw.head(n).to_dict(orient="records")

    if reduce == "pca":
        arr = dims["X_pca"][:n, :2].tolist()
        for i, o in enumerate(out):
            o["embed"] = arr[i]

    if reduce == "umap":
        arr = dims["X_umap"][:n, :2].tolist()
        for i, o in enumerate(out):
            o["embed"] = arr[i]

    return jsonify(out)

if __name__ == "__main__":
    # Run locally for testing; on EC2, use gunicorn instead
    app.run(host="0.0.0.0", port=5000)
