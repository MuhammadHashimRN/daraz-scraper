# from flask import Flask, jsonify, send_file, send_from_directory 
# import os
# import threading

# # Import your refactored scripts
# import scraper
# import preprocess
# import dims

# app = Flask(__name__)

# from flask_cors import CORS
# CORS(app)

# # Paths for generated files
# RAW_CSV = "raw_products.csv"
# PROCESSED_CSV = "processed_products.csv"
# PLOTS = {
#     "pca": "pca_combined.png",
#     "umap_ram": "umap_heatmap_ram_gb.png",
#     "umap_storage": "umap_heatmap_storage_gb.png",
#     "umap_price": "umap_heatmap_price.png",
#     "umap_composite": "umap_composite.png"
# }

# # Track running processes
# running_processes = {
#     "scraping": False,
#     "processing": False
# }

# # Utility: run scripts in a thread to avoid blocking
# def run_in_thread(target, *args, **kwargs):
#     thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
#     thread.start()
#     return thread

# # -------- Endpoints --------

# @app.route("/")
# def home():
#     """Health check endpoint."""
#     return jsonify({
#         "message": "Daraz Scraper API is running!",
#         "endpoints": {
#             "/scrape": "Start scraping Daraz for laptops",
#             "/process": "Process scraped data and generate plots",
#             "/all": "Run scraping + processing + plots",
#             "/csv": "Download processed CSV",
#             "/plot/<name>": "Download plot (pca, umap_ram, umap_storage, umap_price, umap_composite)",
#             "/status": "Check processing status"
#         }
#     })

# @app.route("/status")
# def status():
#     """Check status of files and processes."""
#     return jsonify({
#         "files": {
#             "raw_csv_exists": os.path.exists(RAW_CSV),
#             "processed_csv_exists": os.path.exists(PROCESSED_CSV),
#             "plots_exist": {name: os.path.exists(path) for name, path in PLOTS.items()}
#         },
#         "processes": running_processes
#     })

# @app.route("/scrape")
# def run_scraper():
#     """Start scraping in background."""
#     if running_processes["scraping"]:
#         return jsonify({"error": "Scraping already in progress"}), 409
    
#     def scrape_thread():
#         running_processes["scraping"] = True
#         try:
#             num_products = scraper.scrape_laptops(
#                 search_term="laptop", 
#                 max_pages=5, 
#                 out_file=RAW_CSV
#             )
#             print(f"✅ Scraper finished, {num_products} products saved.")
#         except Exception as e:
#             print(f"❌ Scraper failed: {e}")
#         finally:
#             running_processes["scraping"] = False

#     run_in_thread(scrape_thread)
#     return jsonify({"status": "Scraper started in background"}), 202

# @app.route("/process")
# def run_process():
#     """Process data and generate plots in background."""
#     if not os.path.exists(RAW_CSV):
#         return jsonify({"error": "No raw data found. Run /scrape first"}), 404
    
#     if running_processes["processing"]:
#         return jsonify({"error": "Processing already in progress"}), 409
    
#     def process_thread():
#         running_processes["processing"] = True
#         try:
#             # Run preprocessing
#             num_rows = preprocess.run(
#                 input_file=RAW_CSV, 
#                 output_file=PROCESSED_CSV
#             )
#             print(f"✅ Preprocessing finished. {num_rows} rows processed.")
            
#             # Run dimensionality reduction and plotting
#             generated_plots = dims.run(input_file=PROCESSED_CSV)
#             print(f"✅ Dimensionality reduction finished. Generated {len(generated_plots)} plots.")
            
#         except Exception as e:
#             print(f"❌ Processing failed: {e}")
#         finally:
#             running_processes["processing"] = False

#     run_in_thread(process_thread)
#     return jsonify({"status": "Processing started in background"}), 202

# @app.route("/csv")
# def get_csv():
#     """Download the processed CSV file."""
#     if os.path.exists(PROCESSED_CSV):
#         return send_file(PROCESSED_CSV, as_attachment=True)
#     else:
#         return jsonify({"error": "Processed CSV not found. Run /process first"}), 404

# @app.route("/plot/<name>")
# def get_plot(name):
#     """Download a specific plot by name."""
#     fname = PLOTS.get(name)
#     if not fname:
#         return jsonify({
#             "error": f"Plot '{name}' not found",
#             "available_plots": list(PLOTS.keys())
#         }), 404
    
#     if os.path.exists(fname):
#         return send_file(fname, mimetype='image/png')
#     else:
#         return jsonify({"error": f"Plot file '{fname}' not found. Run /process first"}), 404

# @app.route("/all")
# def run_all():
#     """Run complete pipeline: scraping -> processing -> plots."""
#     if running_processes["scraping"] or running_processes["processing"]:
#         return jsonify({"error": "Another process is already running"}), 409
    
#     def all_thread():
#         running_processes["scraping"] = True
#         running_processes["processing"] = True
#         try:
#             # Step 1: Scrape
#             print("📥 Starting scraping...")
#             num_products = scraper.scrape_laptops(
#                 search_term="laptop", 
#                 max_pages=5, 
#                 out_file=RAW_CSV
#             )
#             print(f"✅ Scraping finished: {num_products} products")
#             running_processes["scraping"] = False
            
#             # Step 2: Preprocess
#             print("🔄 Starting preprocessing...")
#             num_rows = preprocess.run(
#                 input_file=RAW_CSV, 
#                 output_file=PROCESSED_CSV
#             )
#             print(f"✅ Preprocessing finished: {num_rows} rows")
            
#             # Step 3: Generate plots
#             print("📊 Starting dimensionality reduction...")
#             generated_plots = dims.run(input_file=PROCESSED_CSV)
#             print(f"✅ All steps finished successfully!")
#             print(f"   - Products scraped: {num_products}")
#             print(f"   - Rows processed: {num_rows}")
#             print(f"   - Plots generated: {len(generated_plots)}")
            
#         except Exception as e:
#             print(f"❌ Pipeline failed: {e}")
#         finally:
#             running_processes["scraping"] = False
#             running_processes["processing"] = False

#     run_in_thread(all_thread)
#     return jsonify({"status": "Full pipeline started in background"}), 202

# @app.route("/clean")
# def clean_files():
#     """Remove all generated files."""
#     removed = []
    
#     # Remove CSV files
#     for f in [RAW_CSV, PROCESSED_CSV]:
#         if os.path.exists(f):
#             os.remove(f)
#             removed.append(f)
    
#     # Remove plot files
#     for name, path in PLOTS.items():
#         if os.path.exists(path):
#             os.remove(path)
#             removed.append(path)
    
#     return jsonify({
#         "status": "Cleanup complete",
#         "removed_files": removed
#     })



# @app.route('/dashboard')
# def dashboard():
#     return send_from_directory('static', 'index.html')

# if __name__ == "__main__":
#     print("🚀 Starting Daraz Scraper API...")
#     print("📍 API will be available at: http://localhost:5000")
#     print("\n📚 Available endpoints:")
#     print("   GET  /          - API info")
#     print("   GET  /status    - Check status")
#     print("   GET  /scrape    - Start scraping")
#     print("   GET  /process   - Process & generate plots")
#     print("   GET  /all       - Run full pipeline")
#     print("   GET  /csv       - Download CSV")
#     print("   GET  /plot/<name> - Download plot")
#     print("   GET  /clean     - Remove all files")
#     print("\n✨ Ready!\n")
    
#     app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, jsonify, send_file, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flasgger import Swagger
import os
import threading
import time
import pandas as pd
from datetime import datetime
import json
import logging  # ADD THIS LINE

# Import your scripts
import scraper
import preprocess
import dims

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}
swagger = Swagger(app, config=swagger_config)

# Paths for generated files
RAW_CSV = "raw_products.csv"
PROCESSED_CSV = "processed_products.csv"
ENHANCED_CSV = "processed_products_enhanced.csv"
PRICE_HISTORY = "price_history.csv"

# Performance metrics
metrics = {
    "requests": 0,
    "scraping_duration": 0,
    "processing_duration": 0,
    "last_scrape": None,
    "errors": 0
}

# Track running processes
running_processes = {
    "scraping": False,
    "processing": False
}

def broadcast_status():
    """Broadcast status to all connected WebSocket clients"""
    status = get_status_data()
    socketio.emit('status_update', status)

def get_status_data():
    """Get current system status"""
    plots_exist = {}
    if os.path.exists('static/plots'):
        for filename in os.listdir('static/plots'):
            if filename.endswith(('.png', '.html')):
                plots_exist[filename] = True
    
    return {
        "files": {
            "raw_csv_exists": os.path.exists(RAW_CSV),
            "processed_csv_exists": os.path.exists(PROCESSED_CSV),
            "enhanced_csv_exists": os.path.exists(ENHANCED_CSV),
            "price_history_exists": os.path.exists(PRICE_HISTORY),
            "plots_exist": plots_exist
        },
        "processes": running_processes,
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    }

def run_in_thread(target, *args, **kwargs):
    thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread

# -------- WebSocket Events --------

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status_update', get_status_data())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client"""
    emit('status_update', get_status_data())

# -------- API Endpoints --------

@app.route("/")
def home():
    """
    API Home
    ---
    responses:
      200:
        description: API information
    """
    metrics["requests"] += 1
    return jsonify({
        "message": "Daraz Scraper API is running!",
        "version": "2.0.0",
        "features": [
            "Real-time WebSocket updates",
            "Advanced clustering & analytics",
            "Image downloading",
            "Price tracking",
            "Interactive visualizations",
            "Advanced search & filters",
            "Performance monitoring"
        ],
        "endpoints": {
            "/": "API information",
            "/status": "System status",
            "/metrics": "Performance metrics",
            "/scrape": "Start scraping",
            "/process": "Process data",
            "/all": "Run full pipeline",
            "/csv": "Download CSV",
            "/search": "Search products",
            "/price-changes": "Get price changes",
            "/plot/<name>": "Get plot",
            "/images/<filename>": "Get product image",
            "/dashboard": "Web dashboard",
            "/api/docs": "API documentation"
        }
    })

@app.route("/dashboard")
def dashboard():
    """Serve the frontend dashboard"""
    return send_from_directory('static', 'index.html')

@app.route("/status")
def status():
    """
    Get System Status
    ---
    responses:
      200:
        description: Current system status
    """
    metrics["requests"] += 1
    return jsonify(get_status_data())

@app.route("/metrics")
def get_metrics():
    """
    Get Performance Metrics
    ---
    responses:
      200:
        description: Performance metrics
    """
    metrics["requests"] += 1
    
    # Add request rate
    uptime = time.time() - app.config.get('start_time', time.time())
    metrics["requests_per_minute"] = (metrics["requests"] / uptime) * 60 if uptime > 0 else 0
    
    return jsonify(metrics)

@app.route("/scrape")
def run_scraper():
    """
    Start Scraping
    ---
    responses:
      202:
        description: Scraping started
      409:
        description: Already running
    """
    metrics["requests"] += 1
    
    if running_processes["scraping"]:
        return jsonify({"error": "Scraping already in progress"}), 409
    
    def scrape_thread():
        running_processes["scraping"] = True
        broadcast_status()
        
        try:
            start_time = time.time()
            socketio.emit('log', {'message': '📥 Starting scraping...', 'type': 'info'})
            
            num_products = scraper.scrape_laptops(
                search_term="laptop", 
                max_pages=5, 
                out_file=RAW_CSV,
                download_images=True
            )
            
            duration = time.time() - start_time
            metrics["scraping_duration"] = duration
            metrics["last_scrape"] = datetime.now().isoformat()
            
            socketio.emit('log', {
                'message': f'✅ Scraping completed: {num_products} products in {duration:.1f}s',
                'type': 'success'
            })
            
            print(f"✅ Scraper finished, {num_products} products saved.")
        except Exception as e:
            metrics["errors"] += 1
            socketio.emit('log', {'message': f'❌ Scraping failed: {str(e)}', 'type': 'error'})
            print(f"❌ Scraper failed: {e}")
        finally:
            running_processes["scraping"] = False
            broadcast_status()

    run_in_thread(scrape_thread)
    return jsonify({"status": "Scraper started in background"}), 202

@app.route("/process")
def run_process():
    """
    Process Data
    ---
    responses:
      202:
        description: Processing started
      404:
        description: No raw data found
      409:
        description: Already running
    """
    metrics["requests"] += 1
    
    if not os.path.exists(RAW_CSV):
        return jsonify({"error": "No raw data found. Run /scrape first"}), 404
    
    if running_processes["processing"]:
        return jsonify({"error": "Processing already in progress"}), 409
    
    def process_thread():
        running_processes["processing"] = True
        broadcast_status()
        
        try:
            start_time = time.time()
            socketio.emit('log', {'message': '🔄 Starting preprocessing...', 'type': 'info'})
            
            num_rows = preprocess.run(input_file=RAW_CSV, output_file=PROCESSED_CSV)
            
            socketio.emit('log', {'message': '📊 Starting dimensionality reduction...', 'type': 'info'})
            
            result = dims.run(input_file=PROCESSED_CSV)
            
            duration = time.time() - start_time
            metrics["processing_duration"] = duration
            
            socketio.emit('log', {
                'message': f'✅ Processing completed in {duration:.1f}s. Generated {len(result["plots"])} visualizations',
                'type': 'success'
            })
            
            print(f"✅ Processing finished. {num_rows} rows processed.")
        except Exception as e:
            metrics["errors"] += 1
            socketio.emit('log', {'message': f'❌ Processing failed: {str(e)}', 'type': 'error'})
            print(f"❌ Processing failed: {e}")
        finally:
            running_processes["processing"] = False
            broadcast_status()

    run_in_thread(process_thread)
    return jsonify({"status": "Processing started in background"}), 202

@app.route("/all")
def run_all():
    """
    Run Full Pipeline
    ---
    responses:
      202:
        description: Pipeline started
      409:
        description: Already running
    """
    metrics["requests"] += 1
    
    if running_processes["scraping"] or running_processes["processing"]:
        return jsonify({"error": "Another process is already running"}), 409
    
    def all_thread():
        running_processes["scraping"] = True
        running_processes["processing"] = True
        broadcast_status()
        
        try:
            # Scraping
            socketio.emit('log', {'message': '📥 Starting full pipeline: Scraping...', 'type': 'info'})
            num_products = scraper.scrape_laptops(
                search_term="laptop", 
                max_pages=5, 
                out_file=RAW_CSV,
                download_images=True
            )
            running_processes["scraping"] = False
            broadcast_status()
            
            # Processing
            socketio.emit('log', {'message': '🔄 Preprocessing data...', 'type': 'info'})
            num_rows = preprocess.run(input_file=RAW_CSV, output_file=PROCESSED_CSV)
            
            # Dims
            socketio.emit('log', {'message': '📊 Generating visualizations...', 'type': 'info'})
            result = dims.run(input_file=PROCESSED_CSV)
            
            socketio.emit('log', {
                'message': f'🎉 Pipeline completed! {num_products} products, {len(result["plots"])} plots',
                'type': 'success'
            })
            
            print(f"✅ All steps finished. {num_products} products scraped and processed.")
        except Exception as e:
            metrics["errors"] += 1
            socketio.emit('log', {'message': f'❌ Pipeline failed: {str(e)}', 'type': 'error'})
            print(f"❌ All steps failed: {e}")
        finally:
            running_processes["scraping"] = False
            running_processes["processing"] = False
            broadcast_status()

    run_in_thread(all_thread)
    return jsonify({"status": "Full pipeline started in background"}), 202

@app.route("/csv")
def get_csv():
    """
    Download Processed CSV
    ---
    responses:
      200:
        description: CSV file
      404:
        description: File not found
    """
    metrics["requests"] += 1
    
    csv_file = ENHANCED_CSV if os.path.exists(ENHANCED_CSV) else PROCESSED_CSV
    
    if os.path.exists(csv_file):
        return send_file(csv_file, as_attachment=True)
    else:
        return jsonify({"error": "CSV not found. Run /process first"}), 404

@app.route("/search", methods=['POST'])
def search_products():
    """
    Search Products with Filters
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            query:
              type: string
              description: Search query
            min_price:
              type: number
              description: Minimum price
            max_price:
              type: number
              description: Maximum price
            min_rating:
              type: number
              description: Minimum rating
            brand:
              type: string
              description: Brand filter
            min_ram:
              type: number
              description: Minimum RAM
            min_storage:
              type: number
              description: Minimum storage
            cluster:
              type: integer
              description: Cluster ID
    responses:
      200:
        description: Filtered products
      404:
        description: No data available
    """
    metrics["requests"] += 1
    
    csv_file = ENHANCED_CSV if os.path.exists(ENHANCED_CSV) else PROCESSED_CSV
    
    if not os.path.exists(csv_file):
        return jsonify({"error": "No data available"}), 404
    
    df = pd.read_csv(csv_file)
    
    # Get filter parameters
    data = request.get_json() or {}
    query = data.get('query', '')
    min_price = data.get('min_price', 0)
    max_price = data.get('max_price', float('inf'))
    min_rating = data.get('min_rating', 0)
    brand = data.get('brand')
    min_ram = data.get('min_ram', 0)
    min_storage = data.get('min_storage', 0)
    cluster = data.get('cluster')
    
    # Apply filters
    filtered = df[
        (df['price'] >= min_price) &
        (df['price'] <= max_price) &
        (df['rating'] >= min_rating) &
        (df['ram_gb'] >= min_ram) &
        (df['storage_gb'] >= min_storage)
    ]
    
    if query:
        filtered = filtered[
            filtered['title'].str.contains(query, case=False, na=False)
        ]
    
    if brand:
        filtered = filtered[
            filtered['brand'].str.contains(brand, case=False, na=False)
        ]
    
    if cluster is not None and 'cluster_kmeans' in filtered.columns:
        filtered = filtered[filtered['cluster_kmeans'] == cluster]
    
    # Sort by rating and price
    filtered = filtered.sort_values(['rating', 'price'], ascending=[False, True])
    
    return jsonify({
        "total": len(filtered),
        "products": filtered.head(50).to_dict('records')
    })

@app.route("/price-changes")
def get_price_changes():
    """
    Get Price Changes
    ---
    responses:
      200:
        description: Price change data
      404:
        description: No history available
    """
    metrics["requests"] += 1
    
    if not os.path.exists(PRICE_HISTORY):
        return jsonify({"error": "No price history available"}), 404
    
    changes = scraper.get_price_changes(PRICE_HISTORY)
    
    return jsonify({
        "total_changes": len(changes),
        "significant_changes": [c for c in changes if abs(c['change_percent']) > 5],
        "all_changes": changes[:20]
    })

@app.route("/plot/<name>")
def get_plot(name):
    """
    Get Plot File
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Plot name
    responses:
      200:
        description: Plot file
      404:
        description: Plot not found
    """
    metrics["requests"] += 1
    
    # Check for static plots (PNG)
    png_path = f"static/plots/{name}.png"
    if os.path.exists(png_path):
        return send_file(png_path, mimetype='image/png')
    
    # Check for interactive plots (HTML)
    html_path = f"static/plots/{name}.html"
    if os.path.exists(html_path):
        return send_file(html_path, mimetype='text/html')
    
    # Legacy support
    legacy_plots = {
        "pca": "pca_combined.png",
        "umap_ram": "umap_heatmap_ram_gb.png",
        "umap_storage": "umap_heatmap_storage_gb.png",
        "umap_price": "umap_heatmap_price.png",
        "umap_composite": "umap_composite.png"
    }
    
    if name in legacy_plots:
        legacy_path = f"static/plots/{legacy_plots[name]}"
        if os.path.exists(legacy_path):
            return send_file(legacy_path, mimetype='image/png')
    
    return jsonify({
        "error": f"Plot '{name}' not found",
        "available_plots": [f.replace('.png', '').replace('.html', '') 
                           for f in os.listdir('static/plots') 
                           if f.endswith(('.png', '.html'))]
    }), 404

@app.route("/images/<filename>")
def get_image(filename):
    """
    Get Product Image
    ---
    parameters:
      - name: filename
        in: path
        type: string
        required: true
    responses:
      200:
        description: Image file
      404:
        description: Image not found
    """
    metrics["requests"] += 1
    
    image_path = os.path.join('static/images', filename)
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    return jsonify({"error": "Image not found"}), 404

@app.route("/stats")
def get_stats():
    """
    Get Statistics
    ---
    responses:
      200:
        description: Statistical data
    """
    metrics["requests"] += 1
    
    stats_file = 'static/plots/stats.json'
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        return jsonify(stats)
    
    return jsonify({"error": "No statistics available"}), 404

@app.route("/clusters")
def get_clusters():
    """
    Get Cluster Information
    ---
    responses:
      200:
        description: Cluster data
    """
    metrics["requests"] += 1
    
    if not os.path.exists(ENHANCED_CSV):
        return jsonify({"error": "Enhanced data not available"}), 404
    
    df = pd.read_csv(ENHANCED_CSV)
    
    if 'cluster_kmeans' not in df.columns:
        return jsonify({"error": "Clustering not performed yet"}), 404
    
    cluster_info = []
    for cluster_id in sorted(df['cluster_kmeans'].unique()):
        cluster_data = df[df['cluster_kmeans'] == cluster_id]
        cluster_info.append({
            "cluster_id": int(cluster_id),
            "size": len(cluster_data),
            "avg_price": float(cluster_data['price'].mean()),
            "avg_ram": float(cluster_data['ram_gb'].mean()),
            "avg_storage": float(cluster_data['storage_gb'].mean()),
            "avg_rating": float(cluster_data['rating'].mean()),
            "price_range": {
                "min": float(cluster_data['price'].min()),
                "max": float(cluster_data['price'].max())
            }
        })
    
    return jsonify({
        "total_clusters": len(cluster_info),
        "clusters": cluster_info
    })

@app.route("/clean")
def clean_files():
    """
    Clean Generated Files
    ---
    responses:
      200:
        description: Cleanup complete
    """
    metrics["requests"] += 1
    
    removed = []
    
    # Remove CSV files
    for f in [RAW_CSV, PROCESSED_CSV, ENHANCED_CSV, PRICE_HISTORY]:
        if os.path.exists(f):
            os.remove(f)
            removed.append(f)
    
    # Remove plot files
    if os.path.exists('static/plots'):
        for f in os.listdir('static/plots'):
            filepath = os.path.join('static/plots', f)
            os.remove(filepath)
            removed.append(filepath)
    
    # Remove images
    if os.path.exists('static/images'):
        for f in os.listdir('static/images'):
            filepath = os.path.join('static/images', f)
            os.remove(filepath)
            removed.append(filepath)
    
    broadcast_status()
    
    return jsonify({
        "status": "Cleanup complete",
        "removed_files": removed,
        "count": len(removed)
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    metrics["errors"] += 1
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('static/plots', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Store start time for metrics
    app.config['start_time'] = time.time()
    
    print("🚀 Starting Enhanced Daraz Scraper API...")
    print("📍 API available at: http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000/api/docs")
    print("🎨 Dashboard: http://localhost:5000/dashboard")
    print("\n✨ Features enabled:")
    print("   ✓ Real-time WebSocket updates")
    print("   ✓ Advanced clustering & analytics")
    print("   ✓ Image downloading")
    print("   ✓ Price tracking")
    print("   ✓ Interactive visualizations")
    print("   ✓ Advanced search & filters")
    print("   ✓ Performance monitoring")
    print("   ✓ API documentation (Swagger)")
    print("\n✨ Ready!\n")
    
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)