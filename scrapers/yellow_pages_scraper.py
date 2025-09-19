
from bs4 import BeautifulSoup
from core.base_scraper import BaseScraper
from utils.data_cleaner import clean_company_data
import logging
import re

logger = logging.getLogger(__name__)

class YellowPagesScraper(BaseScraper):
    def __init__(self, search_term, location="United States"):
        super().__init__()
        self.search_term = search_term
        self.location = location
        self.base_url = "https://www.yellowpages.com"
        
    def search_companies(self, pages_to_scrape=3):
        """Search for companies and scrape multiple pages"""
        logger.info(f"Starting search for: {self.search_term} in {self.location}")
        
        for page in range(1, pages_to_scrape + 1):
            logger.info(f"Scraping page {page}")
            
            # Build search URL - THIS WILL NEED UPDATING BASED ON ACTUAL YELLOW PAGES URL STRUCTURE
            params = {
                'search_terms': self.search_term,
                'geo_location_terms': self.location,
                'page': page
            }
            
            # This is a hypothetical URL - you need to find the actual search URL
            search_url = f"{self.base_url}/search"
            response = self.make_request(search_url, params=params)
            
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'lxml')
            company_cards = soup.find_all('div', class_='result')  # UPDATE THIS SELECTOR
            
            if not company_cards:
                logger.warning(f"No companies found on page {page}")
                break
                
            for card in company_cards:
                company_data = self._parse_company_card(card)
                if company_data:
                    cleaned_data = clean_company_data(company_data)
                    self.scraped_data.append(cleaned_data)
                    logger.info(f"Scraped: {cleaned_data['company_name']}")
            
        logger.info(f"Completed search. Found {len(self.scraped_data)} companies.")
        return self.scraped_data
    
    def _parse_company_card(self, card):
        """Extract company information from a single result card"""
        try:
            # THESE SELECTORS ARE EXAMPLES - YOU MUST INSPECT THE WEBSITE AND UPDATE THEM
            company_name = card.find('h2', class_='company-name').text.strip() if card.find('h2', class_='company-name') else "N/A"
            
            # Phone number
            phone_elem = card.find('div', class_='phones')
            phone = phone_elem.text.strip() if phone_elem else "N/A"
            
            # Website
            website_elem = card.find('a', class_='website-link')
            website = website_elem['href'] if website_elem else "N/A"
            
            # Address
            address_elem = card.find('div', class_='address')
            address = address_elem.text.strip() if address_elem else "N/A"
            
            return {
                'company_name': company_name,
                'phone': phone,
                'website': website,
                'address': address,
                'industry': self.search_term,
                'source': 'Yellow Pages',
                'date_scraped': str(self.get_current_timestamp())
            }
            
        except Exception as e:
            logger.error(f"Error parsing company card: {e}")
            return None
    
    def get_current_timestamp(self):
        from datetime import datetime
        return datetime.now()