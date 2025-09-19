
import pandas as pd
from pathlib import Path
from datetime import datetime
from scrapers.yellow_pages_scraper import YellowPagesScraper
from core.email_verifier import EmailVerifier
from config import settings
import logging

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting B2B Lead List Builder")
    
    # Read search terms
    search_terms_file = settings.INPUT_DIR / 'search_terms.txt'
    if not search_terms_file.exists():
        logger.error("Search terms file not found!")
        return
    
    with open(search_terms_file, 'r') as f:
        search_terms = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    all_leads = []
    
    # Scrape for each search term
    for search_term in search_terms:
        logger.info(f"Processing search term: {search_term}")
        
        try:
            scraper = YellowPagesScraper(search_term)
            leads = scraper.search_companies(pages_to_scrape=2)  # Scrape 2 pages per term
            all_leads.extend(leads)
            
        except Exception as e:
            logger.error(f"Failed to process {search_term}: {e}")
            continue
    
    # Save raw data first
    if all_leads:
        df = pd.DataFrame(all_leads)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = settings.OUTPUT_DIR / f'leads_{timestamp}.csv'
        
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(all_leads)} leads to {output_file}")
        
        # Show sample output
        print("\n=== SAMPLE OUTPUT (First 3 rows) ===")
        print(df.head(3).to_string(index=False))
        
    else:
        logger.warning("No leads were scraped!")

if __name__ == "__main__":
    main()