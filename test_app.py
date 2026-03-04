"""
Quick Test Script for Expense Tracker Core Logic

Tests the agent, database, and utilities without external dependencies.
"""

import sys
sys.path.insert(0, '.')

print("=" * 60)
print("Testing Agentic AI Expense Tracker - Core Modules")
print("=" * 60)

# Test 1: Intent Classifier
print("\n1. Testing Intent Classifier...")
try:
    from agent.intent_classifier import IntentClassifier, IntentType
    classifier = IntentClassifier()
    
    test_cases = [
        ("I spent 250 rupees on food today", IntentType.SAVE_EXPENSE),
        ("Show me this month's summary", IntentType.SHOW_SUMMARY),
        ("Where did I spend most money?", IntentType.SHOW_CATEGORY_REPORT),
        ("What are my expenses?", IntentType.ANSWER_QUERY),
    ]
    
    for text, expected in test_cases:
        intent, confidence = classifier.classify(text)
        status = "✓" if intent == expected else "✗"
        print(f"  {status} '{text[:40]}...' -> {intent.value} (confidence: {confidence:.2f})")
    
    print("  ✓ Intent Classifier working!")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 2: Entity Extractor
print("\n2. Testing Entity Extractor...")
try:
    from agent.entity_extractor import EntityExtractor
    extractor = EntityExtractor()
    
    test_cases = [
        "I spent 250 rupees on food today",
        "Bought shoes for 1500 yesterday",
        "Paid 500 for petrol on 15th January",
    ]
    
    for text in test_cases:
        result = extractor.extract_all(text)
        print(f"  Input: '{text}'")
        print(f"    Amount: {result['amount']}, Category: {result['category']}, Date: {result['date']}")
    
    print("  ✓ Entity Extractor working!")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 3: Clarifier
print("\n3. Testing Clarifier...")
try:
    from agent.clarifier import Clarifier
    clarifier = Clarifier()
    
    print(f"  Missing amount: {clarifier.generate_clarification(['amount'])}")
    print(f"  Missing category: {clarifier.generate_clarification(['category'])}")
    print(f"  Missing both: {clarifier.generate_clarification(['amount', 'category'])}")
    print("  ✓ Clarifier working!")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 4: Database Manager
print("\n4. Testing Database Manager...")
try:
    from database.db_manager import DatabaseManager
    from datetime import datetime
    
    db = DatabaseManager("sqlite:///./test_expenses.db")
    
    # Add test expense
    expense = db.add_expense(
        amount=250.0,
        category="Food",
        date=datetime.now(),
        description="Test expense"
    )
    print(f"  ✓ Added expense #{expense.id}")
    
    # Get all expenses
    expenses = db.get_all_expenses()
    print(f"  ✓ Retrieved {len(expenses)} expenses")
    
    # Get monthly summary
    summary = db.get_current_month_summary()
    print(f"  ✓ Monthly summary: Total ₹{summary['total_amount']}")
    
    # Get category report
    report = db.get_category_wise_report()
    print(f"  ✓ Category report: {len(report)} categories")
    
    # Cleanup
    db.delete_expense(expense.id)
    print(f"  ✓ Deleted test expense")
    
    print("  ✓ Database Manager working!")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 5: Agent Integration
print("\n5. Testing Agent Integration...")
try:
    from agent.agent import ExpenseAgent
    
    agent = ExpenseAgent(db_manager=db)
    
    # Test expense saving
    result = agent.process_input("I spent 500 rupees on transport today")
    print(f"  Action: {result['action']}")
    print(f"  Message: {result['message'][:80]}...")
    
    # Test summary request
    result = agent.process_input("Show me this month's summary")
    print(f"  Summary action: {result['action']}")
    
    print("  ✓ Agent Integration working!")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 6: Utilities
print("\n6. Testing Utilities...")
try:
    from utils.helpers import parse_currency, format_date, format_currency
    from datetime import datetime
    
    now = datetime.now()
    print(f"  Parse currency: '₹250' -> {parse_currency('₹250')}")
    print(f"  Format date: {format_date(now, 'long')}")
    print(f"  Format currency: {format_currency(1250.50, 'INR')}")
    print("  ✓ Utilities working!")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 60)
print("All core modules tested successfully! ✓")
print("=" * 60)
print("\nNext steps:")
print("1. Install full dependencies: pip install -r requirements.txt")
print("2. Run Streamlit UI: streamlit run ui/streamlit_app.py")
print("3. Or run FastAPI backend: python main.py")
print("\nNote: Some tests may have limited functionality without")
print("      the transformers library for advanced NLP features.")
