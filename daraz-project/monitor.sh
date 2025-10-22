API_URL="http://localhost:5000"

echo "📊 Daraz Scraper API Monitor"
echo "============================"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    clear
    echo "📊 Daraz Scraper API Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================================"
    
    # Get status
    STATUS=$(curl -s $API_URL/status)
    
    # Get metrics
    METRICS=$(curl -s $API_URL/metrics)
    
    echo ""
    echo "📁 Files:"
    echo "$STATUS" | jq -r '.files | to_entries[] | "  \(.key): \(.value)"'
    
    echo ""
    echo "⚙️  Processes:"
    echo "$STATUS" | jq -r '.processes | to_entries[] | "  \(.key): \(.value)"'
    
    echo ""
    echo "📈 Metrics:"
    echo "$METRICS" | jq -r 'to_entries[] | "  \(.key): \(.value)"'
    
    echo ""
    echo "🔄 Refreshing in 5 seconds..."
    sleep 5
done