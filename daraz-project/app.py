from flask import Flask, jsonify, send_file, send_from_directory 
import os
import threading

# Import your refactored scripts
import scraper
import preprocess
import dims

app = Flask(__name__)

from flask_cors import CORS
CORS(app)

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

# Track running processes
running_processes = {
    "scraping": False,
    "processing": False
}

# Utility: run scripts in a thread to avoid blocking
def run_in_thread(target, *args, **kwargs):
    thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread

# -------- Endpoints --------

@app.route("/")
def home():
    """Health check endpoint."""
    return jsonify({
        "message": "Daraz Scraper API is running!",
        "endpoints": {
            "/scrape": "Start scraping Daraz for laptops",
            "/process": "Process scraped data and generate plots",
            "/all": "Run scraping + processing + plots",
            "/csv": "Download processed CSV",
            "/plot/<name>": "Download plot (pca, umap_ram, umap_storage, umap_price, umap_composite)",
            "/status": "Check processing status"
        }
    })

@app.route("/status")
def status():
    """Check status of files and processes."""
    return jsonify({
        "files": {
            "raw_csv_exists": os.path.exists(RAW_CSV),
            "processed_csv_exists": os.path.exists(PROCESSED_CSV),
            "plots_exist": {name: os.path.exists(path) for name, path in PLOTS.items()}
        },
        "processes": running_processes
    })

@app.route("/scrape")
def run_scraper():
    """Start scraping in background."""
    if running_processes["scraping"]:
        return jsonify({"error": "Scraping already in progress"}), 409
    
    def scrape_thread():
        running_processes["scraping"] = True
        try:
            num_products = scraper.scrape_laptops(
                search_term="laptop", 
                max_pages=5, 
                out_file=RAW_CSV
            )
            print(f"✅ Scraper finished, {num_products} products saved.")
        except Exception as e:
            print(f"❌ Scraper failed: {e}")
        finally:
            running_processes["scraping"] = False

    run_in_thread(scrape_thread)
    return jsonify({"status": "Scraper started in background"}), 202

@app.route("/process")
def run_process():
    """Process data and generate plots in background."""
    if not os.path.exists(RAW_CSV):
        return jsonify({"error": "No raw data found. Run /scrape first"}), 404
    
    if running_processes["processing"]:
        return jsonify({"error": "Processing already in progress"}), 409
    
    def process_thread():
        running_processes["processing"] = True
        try:
            # Run preprocessing
            num_rows = preprocess.run(
                input_file=RAW_CSV, 
                output_file=PROCESSED_CSV
            )
            print(f"✅ Preprocessing finished. {num_rows} rows processed.")
            
            # Run dimensionality reduction and plotting
            generated_plots = dims.run(input_file=PROCESSED_CSV)
            print(f"✅ Dimensionality reduction finished. Generated {len(generated_plots)} plots.")
            
        except Exception as e:
            print(f"❌ Processing failed: {e}")
        finally:
            running_processes["processing"] = False

    run_in_thread(process_thread)
    return jsonify({"status": "Processing started in background"}), 202

@app.route("/csv")
def get_csv():
    """Download the processed CSV file."""
    if os.path.exists(PROCESSED_CSV):
        return send_file(PROCESSED_CSV, as_attachment=True)
    else:
        return jsonify({"error": "Processed CSV not found. Run /process first"}), 404

@app.route("/plot/<name>")
def get_plot(name):
    """Download a specific plot by name."""
    fname = PLOTS.get(name)
    if not fname:
        return jsonify({
            "error": f"Plot '{name}' not found",
            "available_plots": list(PLOTS.keys())
        }), 404
    
    if os.path.exists(fname):
        return send_file(fname, mimetype='image/png')
    else:
        return jsonify({"error": f"Plot file '{fname}' not found. Run /process first"}), 404

@app.route("/all")
def run_all():
    """Run complete pipeline: scraping -> processing -> plots."""
    if running_processes["scraping"] or running_processes["processing"]:
        return jsonify({"error": "Another process is already running"}), 409
    
    def all_thread():
        running_processes["scraping"] = True
        running_processes["processing"] = True
        try:
            # Step 1: Scrape
            print("📥 Starting scraping...")
            num_products = scraper.scrape_laptops(
                search_term="laptop", 
                max_pages=5, 
                out_file=RAW_CSV
            )
            print(f"✅ Scraping finished: {num_products} products")
            running_processes["scraping"] = False
            
            # Step 2: Preprocess
            print("🔄 Starting preprocessing...")
            num_rows = preprocess.run(
                input_file=RAW_CSV, 
                output_file=PROCESSED_CSV
            )
            print(f"✅ Preprocessing finished: {num_rows} rows")
            
            # Step 3: Generate plots
            print("📊 Starting dimensionality reduction...")
            generated_plots = dims.run(input_file=PROCESSED_CSV)
            print(f"✅ All steps finished successfully!")
            print(f"   - Products scraped: {num_products}")
            print(f"   - Rows processed: {num_rows}")
            print(f"   - Plots generated: {len(generated_plots)}")
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
        finally:
            running_processes["scraping"] = False
            running_processes["processing"] = False

    run_in_thread(all_thread)
    return jsonify({"status": "Full pipeline started in background"}), 202

@app.route("/clean")
def clean_files():
    """Remove all generated files."""
    removed = []
    
    # Remove CSV files
    for f in [RAW_CSV, PROCESSED_CSV]:
        if os.path.exists(f):
            os.remove(f)
            removed.append(f)
    
    # Remove plot files
    for name, path in PLOTS.items():
        if os.path.exists(path):
            os.remove(path)
            removed.append(path)
    
    return jsonify({
        "status": "Cleanup complete",
        "removed_files": removed
    })



@app.route('/dashboard')
def dashboard():
    return send_from_directory('static', 'index.html')

if __name__ == "__main__":
    print("🚀 Starting Daraz Scraper API...")
    print("📍 API will be available at: http://localhost:5000")
    print("\n📚 Available endpoints:")
    print("   GET  /          - API info")
    print("   GET  /status    - Check status")
    print("   GET  /scrape    - Start scraping")
    print("   GET  /process   - Process & generate plots")
    print("   GET  /all       - Run full pipeline")
    print("   GET  /csv       - Download CSV")
    print("   GET  /plot/<name> - Download plot")
    print("   GET  /clean     - Remove all files")
    print("\n✨ Ready!\n")
    
    app.run(host="0.0.0.0", port=5000, debug=True)

