echo "Setting up Daraz Scraper API on EC2..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-venv git curl jq

# Create project directory
mkdir -p ~/daraz-scraper
cd ~/daraz-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install flask requests beautifulsoup4 pandas scikit-learn umap-learn matplotlib

# Install ngrok
echo "📦 Installing ngrok..."
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt-get update
sudo apt-get install -y ngrok

echo ""
echo "⚠️  IMPORTANT: Configure ngrok with your auth token:"
echo "   1. Sign up at https://ngrok.com"
echo "   2. Get token from https://dashboard.ngrok.com/get-started/your-authtoken"
echo "   3. Run: ngrok config add-authtoken YOUR_TOKEN_HERE"
echo ""
echo "✅ Setup complete! Next: add your token and run deploy.sh"