"""
Intent Classifier for Expense Tracker Agent

Uses transformer-based models to classify user intent into categories:
- SAVE_EXPENSE: User wants to save an expense
- SHOW_SUMMARY: User wants to see monthly summary
- SHOW_CATEGORY_REPORT: User wants category-wise breakdown
- ANSWER_QUERY: User has a question about expenses
- NEED_CLARIFICATION: Input is ambiguous
"""

from enum import Enum
from typing import Tuple
import re


class IntentType(Enum):
    """Enumeration of possible intent types."""
    SAVE_EXPENSE = "save_expense"
    SHOW_SUMMARY = "show_summary"
    SHOW_CATEGORY_REPORT = "show_category_report"
    ANSWER_QUERY = "answer_query"
    NEED_CLARIFICATION = "need_clarification"


class IntentClassifier:
    """
    Classifies user input into different intent categories.
    
    Uses a combination of keyword matching and pattern recognition
    for fast, accurate classification without heavy ML models.
    """
    
    # Keyword patterns for each intent type
    PATTERNS = {
        IntentType.SAVE_EXPENSE: [
            r'\b(spent|paid|bought|purchased|expense|cost)\b',
            r'\b(rupees?|rs\.?|\$|€|£|dollars?|euros?)\b.*\b(on|for)\b',
            r'\b(i\s+spent|i\s+bought|i\s+paid)\b',
            r'\b(expense|add\s+expense|record)\b',
        ],
        IntentType.SHOW_SUMMARY: [
            r'\b(summary|total|month|monthly)\b',
            r'\b(how\s+much|how\s+many).*(spent|expenses)\b',
            r'\b(show|display|get).*(summary|overview)\b',
            r'\b(this|last|current)\s+month\b',
        ],
        IntentType.SHOW_CATEGORY_REPORT: [
            r'\b(category|categories|breakdown|split)\b',
            r'\b(where|which).*(money|spent)\b',
            r'\b(most|highest).*(spent|expense)\b',
            r'\b(category.*report|report.*category)\b',
        ],
        IntentType.ANSWER_QUERY: [
            r'\b(what|how|why|when|where)\b',
            r'\b(question|tell\s+me|explain)\b',
            r'\b(can\s+you|could\s+you)\b',
            r'\?$'  # Question mark at end
        ],
    }
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize the intent classifier.
        
        Args:
            confidence_threshold: Minimum confidence score for classification
        """
        self.confidence_threshold = confidence_threshold
    
    def classify(self, text: str) -> Tuple[IntentType, float]:
        """
        Classify user input into an intent type.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (IntentType, confidence_score)
        """
        text_lower = text.lower().strip()
        
        # Score each intent type based on pattern matches
        scores = {}
        for intent_type, patterns in self.PATTERNS.items():
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    match_count += 1
            # Normalize score by number of patterns
            scores[intent_type] = match_count / len(patterns)
        
        # Get the intent with highest score
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]
        
        # Check if confidence meets threshold
        if confidence < self.confidence_threshold:
            return IntentType.NEED_CLARIFICATION, 1.0 - confidence
        
        return best_intent, confidence
    
    def classify_simple(self, text: str) -> IntentType:
        """
        Simple classification without confidence score.
        
        Args:
            text: User input text
            
        Returns:
            IntentType
        """
        intent, confidence = self.classify(text)
        return intent


# Example usage and testing
if __name__ == "__main__":
    classifier = IntentClassifier()
    
    test_cases = [
        "I spent 250 rupees on food today",
        "Show me this month's summary",
        "Where did I spend most money?",
        "Can you tell me my expenses?",
        "Random text that might be unclear",
    ]
    
    for text in test_cases:
        intent, confidence = classifier.classify(text)
        print(f"Input: {text}")
        print(f"Intent: {intent.value}, Confidence: {confidence:.2f}\n")
