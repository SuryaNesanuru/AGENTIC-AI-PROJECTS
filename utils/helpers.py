"""
Utility Functions for Expense Tracker

Helper functions for common operations like currency parsing, date formatting, and text cleaning.
"""

import re
from datetime import datetime
from typing import Optional


def parse_currency(text: str) -> Optional[float]:
    """
    Parse currency amount from text.
    
    Args:
        text: Text containing currency amount
        
    Returns:
        Parsed amount as float or None if not found
    """
    # Remove currency symbols and extract number
    patterns = [
        r'₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*rupees?',
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'£\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:\.\d{2})?)',  # Generic number
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            return float(amount_str)
    
    return None


def format_date(date: datetime, format_type: str = 'short') -> str:
    """
    Format a datetime object to string.
    
    Args:
        date: Datetime object to format
        format_type: 'short', 'long', or 'iso'
        
    Returns:
        Formatted date string
    """
    if date is None:
        return ""
    
    formats = {
        'short': '%b %d, %Y',      # Jan 15, 2024
        'long': '%B %d, %Y',       # January 15, 2024
        'iso': '%Y-%m-%d',         # 2024-01-15
        'time': '%H:%M',           # 14:30
        'datetime': '%b %d, %Y %H:%M'  # Jan 15, 2024 14:30
    }
    
    fmt = formats.get(format_type, formats['short'])
    return date.strftime(fmt)


def clean_text(text: str) -> str:
    """
    Clean and normalize text input.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?\'\"-]', '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    return text.strip()


def format_currency(amount: float, currency: str = 'INR') -> str:
    """
    Format amount with currency symbol.
    
    Args:
        amount: Amount to format
        currency: Currency code (INR, USD, EUR, GBP)
        
    Returns:
        Formatted currency string
    """
    symbols = {
        'INR': '₹',
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    }
    
    symbol = symbols.get(currency, '₹')
    return f"{symbol}{amount:,.2f}"


def get_month_name(month: int) -> str:
    """
    Get month name from month number.
    
    Args:
        month: Month number (1-12)
        
    Returns:
        Month name
    """
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    if 1 <= month <= 12:
        return months[month - 1]
    return "Invalid month"


def calculate_percentage(part: float, whole: float) -> float:
    """
    Calculate percentage.
    
    Args:
        part: Part value
        whole: Whole value
        
    Returns:
        Percentage value
    """
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)


if __name__ == "__main__":
    # Test utilities
    print("Testing parse_currency:")
    print(parse_currency("I spent 250 rupees"))  # 250.0
    print(parse_currency("$45.99"))  # 45.99
    
    print("\nTesting format_date:")
    now = datetime.now()
    print(format_date(now, 'short'))  # Jan 15, 2024
    print(format_date(now, 'long'))   # January 15, 2024
    
    print("\nTesting clean_text:")
    print(clean_text("  Hello   World!  "))  # "hello world!"
    
    print("\nTesting format_currency:")
    print(format_currency(1250.50, 'INR'))  # ₹1,250.50
    print(format_currency(45.99, 'USD'))    # $45.99
