"""
Main Agent Orchestrator for Expense Tracker

Coordinates intent classification, entity extraction, and database operations
to provide intelligent expense tracking capabilities.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from .intent_classifier import IntentClassifier, IntentType
from .entity_extractor import EntityExtractor
from .clarifier import Clarifier


class ExpenseAgent:
    """
    Main AI agent that orchestrates expense tracking operations.
    
    The agent:
    1. Classifies user intent
    2. Extracts relevant entities
    3. Takes appropriate action (save, show summary, answer query)
    4. Handles clarification when needed
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize the expense agent.
        
        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.intent_classifier = IntentClassifier(confidence_threshold=0.7)
        self.entity_extractor = EntityExtractor()
        self.clarifier = Clarifier()
        self.db_manager = db_manager
        
        # Conversation state
        self.conversation_history = []
        self.pending_expense_data = None
    
    def set_database(self, db_manager):
        """Set the database manager."""
        self.db_manager = db_manager
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and return appropriate response.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Dictionary with response data including:
            - action: What action was taken
            - message: Response message for user
            - data: Any structured data (expense, summary, etc.)
            - requires_clarification: Boolean indicating if more info needed
        """
        # Check for ambiguous input first
        if self.clarifier.is_ambiguous(user_input):
            return {
                'action': 'clarification',
                'message': self.clarifier.generate_clarification([], user_input),
                'data': None,
                'requires_clarification': True
            }
        
        # Classify intent
        intent, confidence = self.intent_classifier.classify(user_input)
        
        # Route to appropriate handler based on intent
        if intent == IntentType.SAVE_EXPENSE:
            return self._handle_save_expense(user_input)
        elif intent == IntentType.SHOW_SUMMARY:
            return self._handle_show_summary(user_input)
        elif intent == IntentType.SHOW_CATEGORY_REPORT:
            return self._handle_show_category_report(user_input)
        elif intent == IntentType.ANSWER_QUERY:
            return self._handle_answer_query(user_input)
        else:  # NEED_CLARIFICATION
            return {
                'action': 'clarification',
                'message': self.clarifier.generate_clarification([], user_input),
                'data': None,
                'requires_clarification': True
            }
    
    def _handle_save_expense(self, user_input: str) -> Dict[str, Any]:
        """Handle expense saving intent."""
        # Extract entities
        extracted = self.entity_extractor.extract_all(user_input)
        
        # Check if we have all required information
        missing = self.entity_extractor.get_missing_entities(user_input)
        
        if missing:
            # Need clarification
            return {
                'action': 'clarification',
                'message': self.clarifier.generate_clarification(missing, user_input),
                'data': {'extracted': extracted, 'missing': missing},
                'requires_clarification': True
            }
        
        # We have all info - save the expense
        if self.db_manager is None:
            return {
                'action': 'error',
                'message': "Database not initialized. Cannot save expense.",
                'data': None,
                'requires_clarification': False
            }
        
        try:
            # Save to database
            expense = self.db_manager.add_expense(
                amount=extracted['amount'],
                category=extracted['category'],
                date=extracted['date'],
                description=user_input
            )
            
            followup = self.clarifier.get_contextual_followup(extracted, user_input)
            
            return {
                'action': 'expense_saved',
                'message': f"{followup} Expense #{expense.id} saved successfully!",
                'data': {'expense': expense.to_dict()},
                'requires_clarification': False
            }
            
        except Exception as e:
            return {
                'action': 'error',
                'message': f"Error saving expense: {str(e)}",
                'data': None,
                'requires_clarification': False
            }
    
    def _handle_show_summary(self, user_input: str) -> Dict[str, Any]:
        """Handle request to show monthly summary."""
        if self.db_manager is None:
            return {
                'action': 'error',
                'message': "Database not initialized.",
                'data': None,
                'requires_clarification': False
            }
        
        try:
            # Get current month summary
            summary = self.db_manager.get_current_month_summary()
            
            message = (
                f"📊 **Monthly Summary**\n\n"
                f"**Month:** {datetime.now().strftime('%B %Y')}\n"
                f"**Total Expenses:** ₹{summary['total_amount']:.2f}\n"
                f"**Number of Categories:** {summary['expense_count']}\n\n"
                f"**Breakdown by Category:**\n"
            )
            
            for category, amount in summary['category_breakdown'].items():
                message += f"• {category}: ₹{amount:.2f}\n"
            
            return {
                'action': 'show_summary',
                'message': message,
                'data': {'summary': summary},
                'requires_clarification': False
            }
            
        except Exception as e:
            return {
                'action': 'error',
                'message': f"Error getting summary: {str(e)}",
                'data': None,
                'requires_clarification': False
            }
    
    def _handle_show_category_report(self, user_input: str) -> Dict[str, Any]:
        """Handle request to show category-wise report."""
        if self.db_manager is None:
            return {
                'action': 'error',
                'message': "Database not initialized.",
                'data': None,
                'requires_clarification': False
            }
        
        try:
            report = self.db_manager.get_category_wise_report()
            
            if not report:
                return {
                    'action': 'show_report',
                    'message': "No expenses recorded yet. Start by telling me about your expenses!",
                    'data': {'report': []},
                    'requires_clarification': False
                }
            
            message = "📊 **Category-Wise Report**\n\n"
            for item in report:
                message += (
                    f"**{item['category']}**\n"
                    f"  Total: ₹{item['total']:.2f} ({item['percentage']}%)\n"
                    f"  Transactions: {item['count']}\n\n"
                )
            
            return {
                'action': 'show_report',
                'message': message,
                'data': {'report': report},
                'requires_clarification': False
            }
            
        except Exception as e:
            return {
                'action': 'error',
                'message': f"Error getting category report: {str(e)}",
                'data': None,
                'requires_clarification': False
            }
    
    def _handle_answer_query(self, user_input: str) -> Dict[str, Any]:
        """Handle general queries about expenses."""
        if self.db_manager is None:
            return {
                'action': 'error',
                'message': "Database not initialized.",
                'data': None,
                'requires_clarification': False
            }
        
        try:
            # Try to answer common query types
            text_lower = user_input.lower()
            
            # Total expenses query
            if 'total' in text_lower and ('expense' in text_lower or 'spent' in text_lower):
                all_expenses = self.db_manager.get_all_expenses()
                total = sum(exp.amount for exp in all_expenses)
                count = len(all_expenses)
                
                return {
                    'action': 'answer_query',
                    'message': f"Your total expenses: ₹{total:.2f} across {count} transactions.",
                    'data': {'total': total, 'count': count},
                    'requires_clarification': False
                }
            
            # Recent expenses query
            elif 'recent' in text_lower or 'last' in text_lower:
                recent = self.db_manager.get_recent_expenses(5)
                if not recent:
                    message = "No recent expenses found."
                else:
                    message = "**Recent Expenses:**\n"
                    for exp in recent:
                        message += f"• ₹{exp.amount} on {exp.category} ({exp.date.strftime('%b %d')})\n"
                
                return {
                    'action': 'answer_query',
                    'message': message,
                    'data': {'expenses': [e.to_dict() for e in recent]},
                    'requires_clarification': False
                }
            
            # Default - can't answer
            else:
                return {
                    'action': 'clarification',
                    'message': "I can help you with questions like:\n• 'What are my total expenses?'\n• 'Show me recent expenses'\n• 'How much did I spend this month?'\n\nWould you like to see your monthly summary instead?",
                    'data': None,
                    'requires_clarification': True
                }
                
        except Exception as e:
            return {
                'action': 'error',
                'message': f"Error processing query: {str(e)}",
                'data': None,
                'requires_clarification': False
            }
    
    def get_help(self) -> str:
        """Get help message."""
        return self.clarifier.get_help_message()
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
        self.pending_expense_data = None


if __name__ == "__main__":
    # Test the agent (without database)
    agent = ExpenseAgent()
    
    test_inputs = [
        "I spent 250 rupees on food today",
        "Show me this month's summary",
        "Where did I spend most money?",
        "Random unclear text",
    ]
    
    for text in test_inputs:
        print(f"\nInput: {text}")
        result = agent.process_input(text)
        print(f"Action: {result['action']}")
        print(f"Message: {result['message']}")
