"""
Cron-based MCP scheduler for periodic execution
Add to crontab: crontab -e

# Run every day at 2 AM
0 2 * * * cd /home/ubuntu/daraz-scraper && /home/ubuntu/daraz-scraper/venv/bin/python mcp_scheduler.py

# Run every 6 hours
0 */6 * * * cd /home/ubuntu/daraz-scraper && /home/ubuntu/daraz-scraper/venv/bin/python mcp_scheduler.py
"""

import subprocess
import os
from datetime import datetime

def get_ngrok_url():
    """Get current ngrok URL from file"""
    try:
        with open('ngrok-url.txt', 'r') as f:
            return f.read().strip()
    except:
        return None

def run_automation():
    """Run MCP automation"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*60}")
    print(f"MCP Scheduler triggered at: {timestamp}")
    print(f"{'='*60}\n")
    
    api_url = get_ngrok_url()
    if not api_url:
        print("❌ Could not get ngrok URL")
        return False
    
    print(f"Using API URL: {api_url}")
    
    # Run automation
    try:
        result = subprocess.run(
            ['python3', 'mcp_automation.py', api_url],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            print("✅ Scheduled automation completed successfully")
            return True
        else:
            print(f"❌ Automation failed with code: {result.returncode}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running automation: {e}")
        return False

if __name__ == "__main__":
    run_automation()


# ============================================
# FILE 3: mcp_config.json
# Configuration file for MCP automation
# ============================================

{
  "api_url": "https://your-ngrok-url.ngrok.io",
  "scraping": {
    "search_term": "laptop",
    "max_pages": 5,
    "timeout": 600
  },
  "processing": {
    "timeout": 300
  },
  "schedule": {
    "enabled": true,
    "interval_hours": 6,
    "cron": "0 */6 * * *"
  },
  "notifications": {
    "enabled": false,
    "email": "your-email@example.com"
  },
  "storage": {
    "keep_history": true,
    "max_files": 10
  }
}