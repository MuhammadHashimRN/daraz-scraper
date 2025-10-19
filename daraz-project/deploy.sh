#!/bin/bash
# One-step EC2 deployment script

set -e
sudo apt update
sudo apt install -y python3-venv python3-pip git

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

mkdir -p artifacts
python3 scraper.py
python3 preprocess.py
python3 dims.py

# Run Flask API via Gunicorn in background
nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app > gunicorn.log 2>&1 &

echo "Deployment complete. Check gunicorn.log for details."
