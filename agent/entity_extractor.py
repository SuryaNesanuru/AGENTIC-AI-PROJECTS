"""
Entity Extractor for Expense Tracker Agent

Extracts structured information from natural language input:
- Amount (numeric value with currency)
- Category (expense category like Food, Transport, etc.)
- Date (temporal information)
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import dateparser


class EntityExtractor:
    """
    Extracts entities (amount, category, date) from user input.
    
    Uses regex patterns and NLP techniques to parse natural language
    expense descriptions.
    """
    
    # Predefined categories for classification
    CATEGORIES = {
        'food': ['food', 'restaurant', 'meal', 'lunch', 'dinner', 'breakfast', 'snack', 
                 'grocery', 'supermarket', 'cafe', 'coffee', 'pizza', 'burger'],
        'transport': ['transport', 'taxi', 'uber', 'ola', 'bus', 'train', 'metro', 
                      'fuel', 'petrol', 'diesel', 'parking', 'toll', 'ride'],
        'shopping': ['shopping', 'clothes', 'shoes', 'mall', 'amazon', 'flipkart', 
                     'purchase', 'buy', 'shirt', 'pants', 'dress'],
        'entertainment': ['entertainment', 'movie', 'cinema', 'theater', 'concert', 
                          'game', 'netflix', 'spotify', 'subscription', 'fun'],
        'bills': ['bills', 'electricity', 'water', 'gas', 'internet', 'phone', 
                  'mobile', 'recharge', 'utility', 'rent'],
        'healthcare': ['healthcare', 'medical', 'doctor', 'hospital', 'medicine', 
                       'pharmacy', 'clinic', 'checkup', 'treatment'],
        'education': ['education', 'books', 'course', 'tuition', 'school', 'college', 
                      'university', 'learning', 'training'],
        'personal': ['personal', 'cash', 'withdrawal', 'atm', 'gift', 'donation'],
    }
    
    def __init__(self):
        """Initialize the entity extractor."""
        # Build category keyword mapping
        self.category_keywords = {}
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                self.category_keywords[keyword] = category
    
    def extract_amount(self, text: str) -> Optional[float]:
        """
        Extract monetary amount from text.
        
        Args:
            text: Input text
            
        Returns:
            Extracted amount as float, or None if not found
        """
        # Pattern 1: Currency symbol followed by number
        currency_patterns = [
            r'₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Indian Rupee symbol
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:rupees?|rs\.?|inr)',  # Rupees word
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Dollar
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|usd)',  # Dollars
            r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Euro
            r'£\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Pound
        ]
        
        for pattern in currency_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                return float(amount_str)
        
        # Pattern 2: Standalone number that might be amount
        # Look for numbers near spending verbs
        amount_pattern = r'\b(spent|paid|cost)\s+.*?\b(\d+(?:\.\d{2})?)\b'
        match = re.search(amount_pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(2))
        
        return None
    
    def extract_category(self, text: str) -> Optional[str]:
        """
        Extract expense category from text.
        
        Args:
            text: Input text
            
        Returns:
            Category name or None if not found
        """
        text_lower = text.lower()
        
        # Direct category mention (e.g., "on food", "for transport")
        on_for_pattern = r'\b(?:on|for)\s+(\w+)\b'
        matches = re.findall(on_for_pattern, text_lower)
        
        for match in matches:
            if match in self.category_keywords:
                return self.category_keywords[match].title()
        
        # Check for any category keywords in text
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if word in self.category_keywords:
                return self.category_keywords[word].title()
        
        return None
    
    def extract_date(self, text: str) -> Optional[datetime]:
        """
        Extract date from text using natural language parsing.
        
        Args:
            text: Input text
            
        Returns:
            Parsed datetime object or None if not found
        """
        # Try dateparser first (handles natural language dates)
        try:
            # Remove common words that might confuse parser
            cleaned_text = re.sub(r'\b(spent|paid|bought|on|for|today|yesterday)\b', 
                                '', text, flags=re.IGNORECASE)
            
            parsed_date = dateparser.parse(cleaned_text, settings={
                'RETURN_AS_TIMEZONE_AWARE': False,
                'PREFER_DATES_FROM': 'current_period'
            })
            
            if parsed_date:
                # Validate it's not too far in future/past
                now = datetime.now()
                if abs((parsed_date - now).days) < 365:  # Within a year
                    return parsed_date
        except Exception:
            pass
        
        # Fallback: Look for explicit date patterns
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',    # YYYY/MM/DD
            r'(today|yesterday|tomorrow)',        # Relative dates
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    if date_str.lower() == 'today':
                        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    elif date_str.lower() == 'yesterday':
                        return (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    elif date_str.lower() == 'tomorrow':
                        return (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    else:
                        # Try parsing the date string
                        for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d']:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
                except Exception:
                    pass
        
        return None
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with extracted entities
        """
        amount = self.extract_amount(text)
        category = self.extract_category(text)
        date = self.extract_date(text)
        
        # If no date found, default to today
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        return {
            'amount': amount,
            'category': category,
            'date': date,
            'is_complete': amount is not None and category is not None
        }
    
    def get_missing_entities(self, text: str) -> List[str]:
        """
        Identify which entities are missing from the input.
        
        Args:
            text: Input text
            
        Returns:
            List of missing entity names
        """
        extracted = self.extract_all(text)
        missing = []
        
        if extracted['amount'] is None:
            missing.append('amount')
        if extracted['category'] is None:
            missing.append('category')
        
        return missing


# Import timedelta for the date extraction
from datetime import timedelta


if __name__ == "__main__":
    # Test the extractor
    extractor = EntityExtractor()
    
    test_cases = [
        "I spent 250 rupees on food today",
        "Bought shoes for 1500 yesterday",
        "Paid 500 for petrol on 15/01/2024",
        "Restaurant bill of $45 last week",
    ]
    
    for text in test_cases:
        result = extractor.extract_all(text)
        print(f"Input: {text}")
        print(f"Amount: {result['amount']}, Category: {result['category']}, Date: {result['date']}")
        print(f"Complete: {result['is_complete']}\n")
