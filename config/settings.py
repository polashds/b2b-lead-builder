
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
DATA_DIR = BASE_DIR / 'data'
INPUT_DIR = DATA_DIR / 'input'
OUTPUT_DIR = DATA_DIR / 'output'
LOG_DIR = DATA_DIR / 'logs'

# Create directories if they don't exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
INPUT_DIR.mkdir(exist_ok=True)

# Scraper settings
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # seconds between requests to be polite
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Output settings
OUTPUT_FILENAME = 'leads_{timestamp}.csv'