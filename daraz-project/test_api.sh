API_URL="http://localhost:5000"

echo "🧪 Testing Enhanced Daraz Scraper API"
echo "======================================"

# Test 1: Health check
echo -e "\n1️⃣ Testing health endpoint..."
curl -s $API_URL/ | jq '.message'

# Test 2: Status
echo -e "\n2️⃣ Testing status endpoint..."
curl -s $API_URL/status | jq '.files'

# Test 3: Metrics
echo -e "\n3️⃣ Testing metrics endpoint..."
curl -s $API_URL/metrics | jq

# Test 4: Trigger scraping
echo -e "\n4️⃣ Triggering scraping..."
curl -s $API_URL/scrape | jq '.status'

# Wait for scraping
echo "⏳ Waiting 30 seconds for scraping to complete..."
sleep 30

# Test 5: Check status again
echo -e "\n5️⃣ Checking status after scraping..."
curl -s $API_URL/status | jq '.files.raw_csv_exists'

# Test 6: Trigger processing
echo -e "\n6️⃣ Triggering processing..."
curl -s $API_URL/process | jq '.status'

# Wait for processing
echo "⏳ Waiting 30 seconds for processing..."
sleep 30

# Test 7: Search products
echo -e "\n7️⃣ Testing search endpoint..."
curl -s -X POST $API_URL/search \
  -H "Content-Type: application/json" \
  -d '{"min_price": 500, "max_price": 2000}' | jq '.total'

# Test 8: Get clusters
echo -e "\n8️⃣ Testing clusters endpoint..."
curl -s $API_URL/clusters | jq '.total_clusters'

# Test 9: Get price changes
echo -e "\n9️⃣ Testing price changes..."
curl -s $API_URL/price-changes | jq '.total_changes'

# Test 10: Get statistics
echo -e "\n🔟 Testing stats endpoint..."
curl -s $API_URL/stats | jq

echo -e "\n✅ API testing complete!"