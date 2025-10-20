URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [ "$URL" != "null" ] && [ ! -z "$URL" ]; then
    echo "✅ Your API URL: $URL"
    echo "$URL" > ngrok-url.txt
else
    echo "❌ Ngrok not running. Check: sudo systemctl status ngrok-tunnel.service"
fi