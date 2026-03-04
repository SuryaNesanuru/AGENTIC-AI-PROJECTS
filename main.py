"""
FastAPI Backend for Agentic AI Expense Tracker

Provides REST API endpoints for expense management and AI agent interaction.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

# Import local modules
from database.db_manager import DatabaseManager
from database.models import Expense
from agent.agent import ExpenseAgent


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Agentic AI Expense Tracker API",
    description="AI-powered expense tracking with natural language processing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database manager
db_manager = DatabaseManager(os.getenv("DATABASE_URL", "sqlite:///./database/expenses.db"))

# Initialize AI agent
agent = ExpenseAgent(db_manager=db_manager)


# Pydantic models for request/response validation
class UserInput(BaseModel):
    """User input model for chat interface."""
    text: str


class ExpenseCreate(BaseModel):
    """Manual expense creation model."""
    amount: float
    category: str
    date: Optional[datetime] = None
    description: Optional[str] = None


class ExpenseResponse(BaseModel):
    """Expense response model."""
    id: int
    amount: float
    category: str
    date: str
    description: Optional[str]
    created_at: str


class AgentResponse(BaseModel):
    """Agent response model."""
    action: str
    message: str
    data: Optional[Dict[str, Any]]
    requires_clarification: bool


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "message": "Welcome to Agentic AI Expense Tracker API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/chat",
            "/expenses",
            "/expenses/{expense_id}",
            "/summary/monthly",
            "/report/category"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}


# Chat endpoint - main AI agent interface
@app.post("/chat", response_model=AgentResponse)
async def chat(user_input: UserInput):
    """
    Process natural language input through the AI agent.
    
    The agent will:
    1. Classify intent (save expense, show summary, etc.)
    2. Extract entities (amount, category, date)
    3. Take appropriate action
    4. Return response with clarification if needed
    """
    try:
        result = agent.process_input(user_input.text)
        return AgentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Expense CRUD endpoints
@app.get("/expenses", response_model=List[ExpenseResponse])
async def get_all_expenses(limit: Optional[int] = 100):
    """Get all expenses (limited by default)."""
    try:
        expenses = db_manager.get_recent_expenses(limit)
        return [ExpenseResponse(**exp.to_dict()) for exp in expenses]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: int):
    """Get a specific expense by ID."""
    expense = db_manager.get_expense_by_id(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseResponse(**expense.to_dict())


@app.post("/expenses", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate):
    """Manually create an expense (bypassing AI agent)."""
    try:
        date = expense.date or datetime.now()
        new_expense = db_manager.add_expense(
            amount=expense.amount,
            category=expense.category,
            date=date,
            description=expense.description
        )
        return ExpenseResponse(**new_expense.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: int):
    """Delete an expense."""
    success = db_manager.delete_expense(expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}


# Summary and Report endpoints
@app.get("/summary/monthly")
async def get_monthly_summary(year: Optional[int] = None, month: Optional[int] = None):
    """
    Get monthly summary.
    
    If year and month are not provided, returns current month summary.
    """
    try:
        if year is None or month is None:
            summary = db_manager.get_current_month_summary()
        else:
            summary = db_manager.get_monthly_summary(year, month)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report/category")
async def get_category_report():
    """Get category-wise expense report."""
    try:
        report = db_manager.get_category_wise_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/summary/date-range")
async def get_date_range_summary(start_date: datetime, end_date: datetime):
    """Get summary for a specific date range."""
    try:
        expenses = db_manager.get_expenses_by_date_range(start_date, end_date)
        total = sum(exp.amount for exp in expenses)
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_amount": total,
            "expense_count": len(expenses),
            "expenses": [exp.to_dict() for exp in expenses]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Agent help endpoint
@app.get("/agent/help")
async def get_agent_help():
    """Get help message from the AI agent."""
    return {"help": agent.get_help()}


if __name__ == "__main__":
    import uvicorn
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
