echo "Deploying Daraz Scraper API..."

# Navigate to project directory
cd ~/daraz-scraper

# Stop services if running
sudo systemctl stop daraz-mcp.service
sudo systemctl stop ngrok-tunnel.service
sleep 2

# Start Flask API
echo "Starting Flask API..."
sudo systemctl start daraz-mcp.service
sudo systemctl enable daraz-mcp.service
sleep 3

# Start ngrok tunnel
echo "🌐 Starting ngrok tunnel..."
sudo systemctl start ngrok-tunnel.service
sudo systemctl enable ngrok-tunnel.service
sleep 5

# Get and display ngrok URL
echo ""
echo "🔗 Your public API URL:"
curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
echo ""

echo "✅ Deployment complete!"
echo ""
echo "📝 Useful commands:"
echo "   sudo systemctl status daraz-mcp.service"
echo "   sudo journalctl -u daraz-mcp.service -f"
echo "   sudo systemctl restart daraz-mcp.service"
echo ""