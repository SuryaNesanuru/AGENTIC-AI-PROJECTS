"""
Database Manager for Expense Tracker

Handles all database operations including CRUD, summaries, and reports.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, func, extract
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Expense


class DatabaseManager:
    """
    Manages database operations for the expense tracker.
    
    Provides methods for:
    - Database initialization
    - CRUD operations on expenses
    - Monthly summaries
    - Category-wise reports
    """
    
    def __init__(self, database_url: str = "sqlite:///./database/expenses.db"):
        """
        Initialize database connection and session.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}  # Needed for SQLite
        )
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.SessionLocal = SessionLocal
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def add_expense(
        self,
        amount: float,
        category: str,
        date: datetime,
        description: str = None
    ) -> Expense:
        """
        Add a new expense to the database.
        
        Args:
            amount: Expense amount
            category: Expense category
            date: Date of expense
            description: Optional description
            
        Returns:
            Created Expense object
        """
        session = self.get_session()
        try:
            expense = Expense(
                amount=amount,
                category=category,
                date=date,
                description=description
            )
            session.add(expense)
            session.commit()
            session.refresh(expense)
            return expense
        finally:
            session.close()
    
    def get_expense_by_id(self, expense_id: int) -> Optional[Expense]:
        """Get an expense by ID."""
        session = self.get_session()
        try:
            return session.query(Expense).filter(Expense.id == expense_id).first()
        finally:
            session.close()
    
    def get_all_expenses(self) -> List[Expense]:
        """Get all expenses ordered by date (newest first)."""
        session = self.get_session()
        try:
            return session.query(Expense).order_by(Expense.date.desc()).all()
        finally:
            session.close()
    
    def get_expenses_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Expense]:
        """Get expenses within a date range."""
        session = self.get_session()
        try:
            return session.query(Expense).filter(
                Expense.date >= start_date,
                Expense.date <= end_date
            ).order_by(Expense.date.desc()).all()
        finally:
            session.close()
    
    def get_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """
        Get monthly summary with total and category breakdown.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            Dictionary with total_amount and category_breakdown
        """
        session = self.get_session()
        try:
            # Calculate month boundaries
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Get total amount
            total_result = session.query(func.sum(Expense.amount)).filter(
                Expense.date >= start_date,
                Expense.date <= end_date
            ).scalar() or 0.0
            
            # Get category breakdown
            category_results = session.query(
                Expense.category,
                func.sum(Expense.amount).label('total')
            ).filter(
                Expense.date >= start_date,
                Expense.date <= end_date
            ).group_by(Expense.category).all()
            
            category_breakdown = {
                category: float(total) 
                for category, total in category_results
            }
            
            return {
                "year": year,
                "month": month,
                "total_amount": float(total_result),
                "category_breakdown": category_breakdown,
                "expense_count": len(category_results)
            }
        finally:
            session.close()
    
    def get_category_wise_report(self) -> List[Dict[str, Any]]:
        """
        Get overall category-wise report.
        
        Returns:
            List of dictionaries with category, total, count, and percentage
        """
        session = self.get_session()
        try:
            # Get grand total
            grand_total = session.query(func.sum(Expense.amount)).scalar() or 0.0
            
            # Get category statistics
            category_stats = session.query(
                Expense.category,
                func.sum(Expense.amount).label('total'),
                func.count(Expense.id).label('count')
            ).group_by(Expense.category).order_by(
                func.sum(Expense.amount).desc()
            ).all()
            
            report = []
            for category, total, count in category_stats:
                percentage = (float(total) / grand_total * 100) if grand_total > 0 else 0
                report.append({
                    "category": category,
                    "total": float(total),
                    "count": count,
                    "percentage": round(percentage, 2)
                })
            
            return report
        finally:
            session.close()
    
    def get_current_month_summary(self) -> Dict[str, Any]:
        """Get summary for current month."""
        now = datetime.now()
        return self.get_monthly_summary(now.year, now.month)
    
    def delete_expense(self, expense_id: int) -> bool:
        """
        Delete an expense by ID.
        
        Args:
            expense_id: ID of expense to delete
            
        Returns:
            True if deleted, False if not found
        """
        session = self.get_session()
        try:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            if expense:
                session.delete(expense)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_recent_expenses(self, limit: int = 10) -> List[Expense]:
        """Get most recent expenses."""
        session = self.get_session()
        try:
            return session.query(Expense).order_by(Expense.date.desc()).limit(limit).all()
        finally:
            session.close()
