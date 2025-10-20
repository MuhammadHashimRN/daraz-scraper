from flask import Flask, jsonify, send_file
import os
import threading

# Import your scripts
import scraper
import preprocess
import dims

app = Flask(__name__)

# Paths for generated files
PROCESSED_CSV = "processed_products.csv"
PLOTS = {
    "pca": "pca_combined.png",
    "umap_ram": "umap_heatmap_ram_gb.png",
    "umap_storage": "umap_heatmap_storage_gb.png",
    "umap_price": "umap_heatmap_price.png",
    "umap_composite": "umap_composite.png"
}

# Utility: run scripts in a thread to avoid blocking
def run_in_thread(target):
    thread = threading.Thread(target=target)
    thread.start()
    return thread

# -------- Endpoints --------

@app.route("/")
def home():
    return jsonify({"message": "Daraz Scraper API is running!"})

@app.route("/scrape")
def run_scraper():
    thread = run_in_thread(scraper.run)
    return jsonify({"status": "Scraper started in background"}), 202

@app.route("/process")
def run_process():
    def process_all():
        preprocess.run()
        dims.run()
    thread = run_in_thread(process_all)
    return jsonify({"status": "Processing started in background"}), 202

@app.route("/csv")
def get_csv():
    if os.path.exists(PROCESSED_CSV):
        return send_file(PROCESSED_CSV, as_attachment=True)
    else:
        return jsonify({"error": "Processed CSV not found"}), 404

@app.route("/plot/<name>")
def get_plot(name):
    fname = PLOTS.get(name)
    if fname and os.path.exists(fname):
        return send_file(fname, as_attachment=True)
    else:
        return jsonify({"error": f"Plot {name} not found"}), 404

# Optional: trigger all steps in sequence
@app.route("/all")
def run_all():
    def all_steps():
        scraper.run()
        preprocess.run()
        dims.run()
    thread = run_in_thread(all_steps)
    return jsonify({"status": "Scraping + Processing + Dims started"}), 202

if __name__ == "__main__":
    # Make accessible externally
    app.run(host="0.0.0.0", port=5000)
