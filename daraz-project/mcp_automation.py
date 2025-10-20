"""
MCP (Model Context Protocol) Automation for Daraz Scraper
Automates the entire pipeline: scraping -> processing -> visualization
"""

import requests
import time
import json
import sys
from datetime import datetime

class DarazMCPAutomation:
    """Automates Daraz scraper pipeline via MCP"""
    
    def __init__(self, api_url):
        self.api_url = api_url.rstrip('/')
        self.log_file = f"mcp_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
    def log(self, message):
        """Log message to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')
    
    def check_health(self):
        """Check if API is accessible"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            if response.status_code == 200:
                self.log("✅ API health check passed")
                return True
            else:
                self.log(f"❌ API returned status code: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ API health check failed: {e}")
            return False
    
    def trigger_scraping(self):
        """Trigger scraping process"""
        self.log("📥 Triggering scraping process...")
        try:
            response = requests.get(f"{self.api_url}/scrape", timeout=10)
            if response.status_code == 202:
                self.log("✅ Scraping started successfully")
                return True
            else:
                self.log(f"❌ Scraping failed with status: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Scraping trigger failed: {e}")
            return False
    
    def wait_for_completion(self, process_type="scraping", max_wait=300):
        """Wait for process to complete by checking status"""
        self.log(f"⏳ Waiting for {process_type} to complete...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.api_url}/status", timeout=10)
                if response.status_code == 200:
                    status = response.json()
                    
                    if process_type == "scraping":
                        if not status['processes']['scraping']:
                            self.log(f"✅ {process_type.capitalize()} completed")
                            return True
                    elif process_type == "processing":
                        if not status['processes']['processing']:
                            self.log(f"✅ {process_type.capitalize()} completed")
                            return True
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.log(f"⚠️ Status check error: {e}")
                time.sleep(5)
        
        self.log(f"❌ {process_type.capitalize()} timeout")
        return False
    
    def trigger_processing(self):
        """Trigger data processing and visualization"""
        self.log("🔄 Triggering processing and visualization...")
        try:
            response = requests.get(f"{self.api_url}/process", timeout=10)
            if response.status_code == 202:
                self.log("✅ Processing started successfully")
                return True
            else:
                self.log(f"❌ Processing failed with status: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Processing trigger failed: {e}")
            return False
    
    def download_results(self):
        """Download CSV and plots"""
        self.log("📊 Downloading results...")
        
        # Download CSV
        try:
            response = requests.get(f"{self.api_url}/csv", timeout=30)
            if response.status_code == 200:
                filename = f"processed_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                self.log(f"✅ Downloaded CSV: {filename}")
            else:
                self.log(f"⚠️ CSV download failed: {response.status_code}")
        except Exception as e:
            self.log(f"❌ CSV download error: {e}")
        
        # Download plots
        plots = ['pca', 'umap_ram', 'umap_storage', 'umap_price', 'umap_composite']
        for plot_name in plots:
            try:
                response = requests.get(f"{self.api_url}/plot/{plot_name}", timeout=30)
                if response.status_code == 200:
                    filename = f"{plot_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    self.log(f"✅ Downloaded plot: {filename}")
                else:
                    self.log(f"⚠️ Plot {plot_name} download failed: {response.status_code}")
            except Exception as e:
                self.log(f"❌ Plot {plot_name} download error: {e}")
    
    def run_full_pipeline(self):
        """Execute complete automation pipeline"""
        self.log("=" * 60)
        self.log("🚀 Starting MCP Automation Pipeline")
        self.log("=" * 60)
        
        # Step 1: Health check
        if not self.check_health():
            self.log("❌ Pipeline aborted: API not accessible")
            return False
        
        # Step 2: Trigger scraping
        if not self.trigger_scraping():
            self.log("❌ Pipeline aborted: Scraping failed to start")
            return False
        
        # Step 3: Wait for scraping
        if not self.wait_for_completion("scraping", max_wait=600):
            self.log("❌ Pipeline aborted: Scraping timeout")
            return False
        
        # Step 4: Trigger processing
        if not self.trigger_processing():
            self.log("❌ Pipeline aborted: Processing failed to start")
            return False
        
        # Step 5: Wait for processing
        if not self.wait_for_completion("processing", max_wait=300):
            self.log("❌ Pipeline aborted: Processing timeout")
            return False
        
        # Step 6: Download results
        self.download_results()
        
        self.log("=" * 60)
        self.log("✅ MCP Automation Pipeline Completed Successfully!")
        self.log(f"📝 Log file: {self.log_file}")
        self.log("=" * 60)
        
        return True


def main():
    """Main entry point for MCP automation"""
    if len(sys.argv) < 2:
        print("Usage: python mcp_automation.py <API_URL>")
        print("Example: python mcp_automation.py https://abcd1234.ngrok.io")
        sys.exit(1)
    
    api_url = sys.argv[1]
    automation = DarazMCPAutomation(api_url)
    
    success = automation.run_full_pipeline()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()