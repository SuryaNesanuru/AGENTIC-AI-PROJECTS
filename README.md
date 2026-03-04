# 💰 Agentic AI Expense Tracker

An intelligent expense tracking application powered by AI that understands natural language input. Track your expenses effortlessly by simply typing or speaking naturally.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### Core Capabilities
- **💬 Natural Language Processing** - Enter expenses conversationally: "I spent 250 rupees on food today"
- **🤖 AI Agent** - Intelligent intent detection and entity extraction
- **📊 Interactive Dashboard** - Beautiful charts and visualizations
- **📈 Monthly Summaries** - Automatic monthly breakdowns and reports
- **🎯 Category-wise Analysis** - See where your money goes
- **❓ Smart Clarifications** - Agent asks when information is unclear
- **🔍 Query Understanding** - Ask questions about your spending

### Technical Highlights
- **Fully Local** - No external API dependencies (works offline)
- **Modular Architecture** - Clean, well-organized code structure
- **RESTful API** - FastAPI backend with comprehensive endpoints
- **Modern UI** - Responsive Streamlit interface
- **SQLite Database** - Lightweight, zero-configuration storage
- **Extensible Design** - Easy to add new features

## 📋 Table of Contents

- [Overview](#-agentic-ai-expense-tracker)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Examples](#-examples)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

## 📸 Screenshots

### Dashboard View
```
┌─────────────────────────────────────────────────────┐
│           💰 AI Expense Tracker Dashboard           │
├─────────────────────────────────────────────────────┤
│  Total Spent    This Month    Total Expenses       │
│   ₹12,450        ₹3,200          47                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [Spending Trend Chart]      [Category Pie Chart]  │
│                                                     │
├─────────────────────────────────────────────────────┤
│  Recent Expenses:                                   │
│  • ₹250 - Food (Jan 15)                            │
│  • ₹1,500 - Shopping (Jan 14)                      │
│  • ₹500 - Transport (Jan 13)                       │
└─────────────────────────────────────────────────────┘
```

### Chat Interface
```
┌─────────────────────────────────────────────────────┐
│  💬 Chat with AI Agent                              │
├─────────────────────────────────────────────────────┤
│  🤖 Agent: How can I help you today?               │
│                                                     │
│  👤 You: I spent 250 rupees on food today          │
│                                                     │
│  🤖 Agent: ✓ Got it! Recording ₹250 expense for    │
│            Food on January 15, 2024.               │
│            Expense #1 saved successfully!           │
└─────────────────────────────────────────────────────┘
```

### Analytics & Reports
```
┌─────────────────────────────────────────────────────┐
│  📊 Category Report                                 │
├─────────────────────────────────────────────────────┤
│  Category      Total      Count    Percentage       │
│  Food         ₹4,500       18        36.2%          │
│  Transport    ₹2,800       12        22.5%          │
│  Shopping     ₹3,200        8        25.7%          │
│  Bills        ₹1,950        5        15.6%          │
└─────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Python 3.8+** - Core programming language
- **FastAPI** - High-performance REST API
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database

### AI/NLP
- **Transformers** - Hugging Face NLP library
- **DateParser** - Natural language date parsing
- **Custom NLP** - Pattern-based intent classification

### Frontend
- **Streamlit** - Interactive web UI framework
- **Plotly** - Interactive charts and graphs
- **Pandas** - Data manipulation

### Utilities
- **Pydantic** - Data validation
- **python-dotenv** - Environment configuration
- **uvicorn** - ASGI server

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (for cloning)

### Step-by-Step Setup

1. **Clone the repository**
```bash
cd c:\AGENTIC_AI_PROJECTS
cd expense-tracker
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy example env file
copy .env.example .env

# Edit .env if needed (default values work fine)
```

5. **Verify installation**
```bash
python -c "from database.db_manager import DatabaseManager; print('✓ Setup successful!')"
```

## 🚀 Usage

### Option 1: Streamlit Web Interface (Recommended)

Launch the interactive web UI:

```bash
streamlit run ui/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

**What you can do:**
- Navigate through Dashboard, Chat, Manual Entry, Reports, and Analytics
- Chat with the AI agent to add expenses naturally
- View interactive charts and reports
- Manage expenses (view, delete)

### Option 2: FastAPI Backend

Start the REST API server:

```bash
python main.py
```

Access the API documentation at `http://localhost:8000/docs`

**Example API calls:**

```python
import requests

# Chat with AI agent
response = requests.post("http://localhost:8000/chat", json={
    "text": "I spent 250 rupees on food today"
})
print(response.json())

# Get monthly summary
response = requests.get("http://localhost:8000/summary/monthly")
print(response.json())

# Get category report
response = requests.get("http://localhost:8000/report/category")
print(response.json())
```

### Option 3: Direct Python Usage

Use the agent directly in Python code:

```python
from agent.agent import ExpenseAgent
from database.db_manager import DatabaseManager

# Initialize
db = DatabaseManager()
agent = ExpenseAgent(db_manager=db)

# Process natural language
result = agent.process_input("I spent 500 rupees on petrol yesterday")
print(result['message'])

# Get summary
summary = db.get_current_month_summary()
print(f"Total spent this month: ₹{summary['total_amount']}")
```

## 📁 Project Structure

```
expense-tracker/
├── agent/                      # AI Agent module
│   ├── __init__.py
│   ├── intent_classifier.py    # Intent detection (SAVE_EXPENSE, SHOW_SUMMARY, etc.)
│   ├── entity_extractor.py     # Extract amount, category, date
│   ├── clarifier.py            # Generate clarification questions
│   └── agent.py                # Main orchestrator
│
├── database/                   # Database layer
│   ├── __init__.py
│   ├── models.py               # SQLAlchemy models (Expense)
│   ├── db_manager.py           # Database operations (CRUD, reports)
│   └── expenses.db             # SQLite database (auto-created)
│
├── ui/                         # User Interface
│   ├── __init__.py
│   └── streamlit_app.py        # Streamlit web application
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   └── helpers.py              # Helper functions (formatting, parsing)
│
├── main.py                     # FastAPI backend application
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 📚 API Documentation

### Endpoints

#### POST `/chat`
Process natural language input through AI agent.

**Request:**
```json
{
  "text": "I spent 250 rupees on food today"
}
```

**Response:**
```json
{
  "action": "expense_saved",
  "message": "✓ Got it! Recording ₹250 expense for Food on January 15, 2024.",
  "data": {
    "expense": {
      "id": 1,
      "amount": 250.0,
      "category": "Food",
      "date": "2024-01-15T00:00:00"
    }
  },
  "requires_clarification": false
}
```

#### GET `/expenses`
Get all expenses (optional limit parameter).

**Query Parameters:**
- `limit` (int, optional): Number of expenses to return (default: 100)

#### GET `/expenses/{expense_id}`
Get a specific expense by ID.

#### POST `/expenses`
Manually create an expense.

**Request:**
```json
{
  "amount": 250.0,
  "category": "Food",
  "date": "2024-01-15T00:00:00",
  "description": "Lunch at office cafeteria"
}
```

#### DELETE `/expenses/{expense_id}`
Delete an expense.

#### GET `/summary/monthly`
Get monthly summary.

**Query Parameters:**
- `year` (int, optional): Year (defaults to current year)
- `month` (int, optional): Month (defaults to current month)

#### GET `/report/category`
Get category-wise expense report.

#### GET `/agent/help`
Get help message from AI agent.

Full interactive API documentation available at: `http://localhost:8000/docs`

## 💡 Examples

### Natural Language Inputs

The AI agent understands various ways to express expenses:

**Saving Expenses:**
- "I spent 250 rupees on food today"
- "Bought shoes for 1500 yesterday"
- "Paid 500 for petrol on 15th January"
- "Restaurant bill of $45 last week"
- "Expense: 800 rupees on groceries"

**Asking for Summaries:**
- "Show me this month's summary"
- "How much did I spend this month?"
- "Total expenses for January"

**Category Reports:**
- "Where did I spend most money?"
- "Show me category breakdown"
- "Which category has highest expenses?"

**General Queries:**
- "What are my total expenses?"
- "Show me recent expenses"
- "How many transactions did I make?"

### Clarification Dialogues

**Incomplete Input:**
```
You: I bought something
Agent: Could you tell me how much you spent and what category it belongs to?
       (e.g., 'I spent 500 rupees on food')

You: 500 rupees
Agent: What category is this expense for?

You: Food
Agent: ✓ Got it! Recording ₹500 expense for Food on today.
       Expense #5 saved successfully!
```

## 🔮 Future Enhancements

### Planned Features
- [ ] **Multi-currency support** - Automatic currency conversion
- [ ] **Receipt scanning** - OCR integration for receipt images
- [ ] **Voice input** - Speech-to-text integration
- [ ] **Budget alerts** - Notifications when exceeding budgets
- [ ] **Export functionality** - CSV, PDF, Excel reports
- [ ] **Recurring expenses** - Automatic tracking of subscriptions
- [ ] **Data visualization** - More chart types and custom date ranges
- [ ] **User authentication** - Multi-user support
- [ ] **Cloud sync** - Optional cloud backup
- [ ] **Mobile app** - React Native or Flutter version
- [ ] **Email reports** - Scheduled monthly summaries
- [ ] **Integration** - Bank statement import, UPI transaction parsing

### AI Improvements
- [ ] Fine-tuned transformer model for better accuracy
- [ ] Contextual learning from past expenses
- [ ] Automatic categorization suggestions
- [ ] Spending pattern analysis and insights
- [ ] Predictive budgeting recommendations

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/expense-tracker.git

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Testing and linting

# Run tests (when added)
pytest

# Code formatting
black .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Hugging Face** - For excellent NLP libraries
- **Streamlit** - Amazing framework for data apps
- **FastAPI** - Lightning-fast web framework
- **Plotly** - Beautiful interactive visualizations

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

---

**Built with ❤️ using AI and Python**

*Last Updated: March 4, 2026*
