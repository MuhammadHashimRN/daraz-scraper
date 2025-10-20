from flask import Flask, jsonify, send_file
import os
import threading

# Import your scripts
import scraper
import preprocess
import dims

app = Flask(__name__)

# Paths for generated files
RAW_CSV = "raw_products.csv"
PROCESSED_CSV = "processed_products.csv"
PLOTS = {
    "pca": "pca_combined.png",
    "umap_ram": "umap_heatmap_ram_gb.png",
    "umap_storage": "umap_heatmap_storage_gb.png",
    "umap_price": "umap_heatmap_price.png",
    "umap_composite": "umap_composite.png"
}

# Utility: run scripts in a thread to avoid blocking
def run_in_thread(target, *args, **kwargs):
    thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    thread.start()
    return thread

# -------- Endpoints --------

@app.route("/")
def home():
    return jsonify({"message": "Daraz Scraper API is running!"})

@app.route("/scrape")
def run_scraper():
    def scrape_thread():
        try:
            num_products = scraper.scrape_laptops(search_term="laptop", max_pages=5, out_file=RAW_CSV)
            print(f"✅ Scraper finished, {num_products} products saved.")
        except Exception as e:
            print(f"❌ Scraper failed: {e}")

    run_in_thread(scrape_thread)
    return jsonify({"status": "Scraper started in background"}), 202


@app.route("/process")
def run_process():
    def process_thread():
        try:
            preprocess.run()
            dims.run()
            print("✅ Processing + dimensionality reduction finished.")
        except Exception as e:
            print(f"❌ Processing failed: {e}")

    run_in_thread(process_thread)
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

@app.route("/all")
def run_all():
    def all_thread():
        try:
            num_products = scraper.scrape_laptops(search_term="laptop", max_pages=5, out_file=RAW_CSV)
            preprocess.run()
            dims.run()
            print(f"✅ All steps finished. {num_products} products scraped and processed.")
        except Exception as e:
            print(f"❌ All steps failed: {e}")

    run_in_thread(all_thread)
    return jsonify({"status": "Scraping + Processing + Dims started"}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
