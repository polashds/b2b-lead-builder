
import requests
import time
import logging
from datetime import datetime
from pathlib import Path

from config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_DIR / f'scraper_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT
        })
        self.scraped_data = []
        
    def make_request(self, url, params=None):
        """Make HTTP request with error handling and delays"""
        try:
            time.sleep(settings.REQUEST_DELAY)
            response = self.session.get(
                url, 
                params=params, 
                timeout=settings.REQUEST_TIMEOUT
            )
            response.raise_for_status()  # Raise exception for bad status codes
            logger.info(f"Successfully requested: {url}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
            
    def save_to_csv(self, data, filename=None):
        """Save scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = settings.OUTPUT_DIR / f"leads_{timestamp}.csv"
        
        # This will be implemented after we create data_cleaner
        # For now, we'll create a simple save method
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        return filename