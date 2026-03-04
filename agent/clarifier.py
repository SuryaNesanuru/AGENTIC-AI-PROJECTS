"""
Clarification Module for Expense Tracker Agent

Handles ambiguous inputs by generating clarification questions
when required information is missing.
"""

from typing import List, Dict, Any
from datetime import datetime


class Clarifier:
    """
    Generates clarification questions when user input is incomplete or ambiguous.
    
    Provides contextual questions to gather missing information for expense tracking.
    """
    
    # Templates for clarification questions
    TEMPLATES = {
        'amount': [
            "How much did you spend?",
            "What was the amount?",
            "Could you tell me the expense amount?",
            "How much was this for?"
        ],
        'category': [
            "What category is this expense for?",
            "Was this for food, transport, shopping, or something else?",
            "How would you categorize this expense?",
            "What type of expense was this?"
        ],
        'date': [
            "When did this expense occur?",
            "What date was this?",
            "Was this today, yesterday, or another date?"
        ],
        'general': [
            "I'm not sure I understood. Could you rephrase that?",
            "Could you provide more details about your expense?",
            "I need a bit more information. Can you clarify?"
        ]
    }
    
    def __init__(self):
        """Initialize the clarifier."""
        self.question_history = []
    
    def generate_clarification(
        self,
        missing_entities: List[str],
        original_text: str = None
    ) -> str:
        """
        Generate a clarification question based on missing entities.
        
        Args:
            missing_entities: List of missing entity names (e.g., ['amount', 'category'])
            original_text: Original user input for context
            
        Returns:
            Clarification question string
        """
        if not missing_entities:
            return self.TEMPLATES['general'][0]
        
        # Build question based on missing entities
        if len(missing_entities) == 1:
            entity = missing_entities[0]
            question = self.TEMPLATES.get(entity, self.TEMPLATES['general'])[0]
        else:
            # Multiple missing entities - ask for both
            if 'amount' in missing_entities and 'category' in missing_entities:
                question = "Could you tell me how much you spent and what category it belongs to? (e.g., 'I spent 500 rupees on food')"
            elif 'amount' in missing_entities and 'date' in missing_entities:
                question = "How much was the expense and when did it occur?"
            elif 'category' in missing_entities and 'date' in missing_entities:
                question = "What category is this expense for and when did it happen?"
            else:
                question = self.TEMPLATES['general'][0]
        
        self.question_history.append({
            'timestamp': datetime.now(),
            'question': question,
            'missing_entities': missing_entities
        })
        
        return question
    
    def get_help_message(self) -> str:
        """
        Get a help message explaining how to use the expense tracker.
        
        Returns:
            Help message string
        """
        return """
💡 **How to use the Expense Tracker:**

You can enter expenses in natural language. For example:
• "I spent 250 rupees on food today"
• "Bought shoes for 1500 yesterday"
• "Paid 500 for petrol on 15th January"

You can also ask for:
• Monthly summary: "Show me this month's summary"
• Category report: "Where did I spend most money?"
• General queries: "What are my total expenses?"

I'll automatically extract the amount, category, and date from your input!
        """.strip()
    
    def is_ambiguous(self, text: str) -> bool:
        """
        Check if input is too ambiguous to process.
        
        Args:
            text: User input
            
        Returns:
            True if input is ambiguous
        """
        # Very short inputs are usually ambiguous
        if len(text.strip().split()) < 3:
            return True
        
        # Check for common ambiguous patterns
        ambiguous_patterns = [
            r'^\s*$',  # Empty or whitespace only
            r'^(yes|no|ok|okay|sure)$',  # Just acknowledgments
            r'^(what|how|why|when|where)\s',  # Questions without context
        ]
        
        import re
        for pattern in ambiguous_patterns:
            if re.match(pattern, text.lower()):
                return True
        
        return False
    
    def get_contextual_followup(
        self,
        extracted_entities: Dict[str, Any],
        original_text: str
    ) -> str:
        """
        Generate a contextual follow-up message after successful extraction.
        
        Args:
            extracted_entities: Dictionary of extracted entities
            original_text: Original user input
            
        Returns:
            Follow-up message
        """
        amount = extracted_entities.get('amount')
        category = extracted_entities.get('category')
        date = extracted_entities.get('date')
        
        if amount and category:
            date_str = date.strftime("%B %d, %Y") if date else "today"
            return f"✓ Got it! Recording ₹{amount} expense for {category} on {date_str}."
        else:
            return "Thanks! Let me save that for you."


if __name__ == "__main__":
    # Test the clarifier
    clarifier = Clarifier()
    
    print("Test 1 - Missing amount:")
    print(clarifier.generate_clarification(['amount']))
    print()
    
    print("Test 2 - Missing category:")
    print(clarifier.generate_clarification(['category']))
    print()
    
    print("Test 3 - Missing both:")
    print(clarifier.generate_clarification(['amount', 'category']))
    print()
    
    print("\nHelp message:")
    print(clarifier.get_help_message())
