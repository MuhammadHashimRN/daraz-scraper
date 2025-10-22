echo "🚀 Setting up Enhanced Daraz Scraper API..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install -y python3 python3-pip python3-venv git curl jq

# Navigate to project
cd ~/daraz-scraper/daraz-project

# Create/activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p static/images
mkdir -p static/plots

# Create the requirements.txt if not exists
cat > requirements.txt <<'EOF'
requests
beautifulsoup4
matplotlib
pandas
numpy
scikit-learn
umap-learn
flask
gunicorn
python-dotenv
joblib
PyYAML
flask-socketio
flasgger
plotly
python-socketio
python-engineio

pip install -r requirements.txt

echo ""
echo "✅ Enhanced setup complete!"
echo ""
echo "📋 Features installed:"
echo "   ✓ Real-time WebSocket updates"
echo "   ✓ Advanced clustering (K-Means, DBSCAN)"
echo "   ✓ Image downloading"
echo "   ✓ Price tracking over time"
echo "   ✓ Interactive visualizations (Plotly)"
echo "   ✓ Advanced search & filters"
echo "   ✓ Performance monitoring"
echo "   ✓ API documentation (Swagger)"
echo ""
echo "🔗 Access points:"
echo "   Dashboard: http://your-url/dashboard"
echo "   API Docs: http://your-url/api/docs"
echo "   Metrics: http://your-url/metrics"
echo ""