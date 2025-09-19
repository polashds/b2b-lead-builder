
import re
import pandas as pd
from typing import Dict, Any

def clean_phone_number(phone: str) -> str:
    """Clean and standardize phone numbers"""
    if not phone:
        return ""
    
    # Remove all non-digit characters except leading +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Handle US numbers (add +1 if missing country code)
    if cleaned.startswith('1') and len(cleaned) == 11:
        cleaned = '+' + cleaned
    elif len(cleaned) == 10:
        cleaned = '+1' + cleaned
        
    return cleaned

def clean_website_url(url: str) -> str:
    """Clean and standardize website URLs"""
    if not url:
        return ""
    
    url = url.strip().lower()
    if url and not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    return url

def clean_company_data(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean all company data fields"""
    cleaned_data = company_data.copy()
    
    cleaned_data['phone'] = clean_phone_number(company_data.get('phone', ''))
    cleaned_data['website'] = clean_website_url(company_data.get('website', ''))
    cleaned_data['company_name'] = company_data.get('company_name', '').strip()
    cleaned_data['industry'] = company_data.get('industry', '').strip().title()
    
    # Clean address
    address = company_data.get('address', '')
    if isinstance(address, str):
        cleaned_data['address'] = ' '.join(address.split())
    else:
        cleaned_data['address'] = ''
    
    return cleaned_data