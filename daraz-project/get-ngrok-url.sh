cat > ~/daraz-scraper/get-ngrok-url.sh <<'URL_SCRIPT'
#!/bin/bash

echo "🔍 Fetching ngrok URL..."

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Installing jq..."
    sudo apt-get install -y jq
fi

# Get the public URL
URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [ "$URL" != "null" ] && [ ! -z "$URL" ]; then
    echo ""
    echo "✅ Your public API URL:"
    echo "   $URL"
    echo ""
    echo "🧪 Test it:"
    echo "   curl $URL"
    echo ""
    echo "📋 Save this URL for your frontend!"
    echo "$URL" > ngrok-url.txt
    echo "   (Saved to ngrok-url.txt)"
else
    echo "❌ Could not fetch ngrok URL. Is ngrok running?"
    echo "   Check: sudo systemctl status ngrok-tunnel.service"
fi
URL_SCRIPT

chmod +x ~/daraz-scraper/get-ngrok-url.sh

echo "📝 Created get-ngrok-url.sh helper script"
echo ""
echo "✅ All setup files created!"
DEPLOY_SCRIPT