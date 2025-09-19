
import requests
import logging
from typing import Dict, Optional
from config import settings

logger = logging.getLogger(__name__)

class EmailVerifier:
    def __init__(self, api_key: Optional[str] = None):
        # Get API key from environment variables
        self.api_key = api_key 
        self.base_url = "https://api.hunter.io/v2/email-verifier"
        
    def verify_email(self, email: str) -> Dict:
        """Verify an email address using Hunter.io API"""
        if not self.api_key or not email or '@' not in email:
            return {'result': 'invalid', 'score': 0}
        
        try:
            params = {
                'email': email,
                'api_key': self.api_key
            }
            
            response = requests.get(
                f"{self.base_url}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'result': data['data']['result'],
                    'score': data['data']['score'],
                    'status': data['data']['status']
                }
            else:
                logger.warning(f"Email verification API error: {response.status_code}")
                return {'result': 'unknown', 'score': 0}
                
        except Exception as e:
            logger.error(f"Email verification failed: {e}")
            return {'result': 'unknown', 'score': 0}
    
    def extract_domain_emails(self, domain: str) -> list:
        """Find emails for a domain"""
        if not self.api_key:
            return []
        
        try:
            params = {
                'domain': domain,
                'api_key': self.api_key
            }
            
            response = requests.get(
                "https://api.hunter.io/v2/domain-search",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['data']['emails']
            return []
            
        except Exception as e:
            logger.error(f"Domain email search failed: {e}")
            return []