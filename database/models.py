"""
Database Models for Expense Tracker

Defines SQLAlchemy ORM models for storing expense data.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Expense(Base):
    """
    Expense model representing a single expense entry.
    
    Attributes:
        id (int): Primary key
        amount (float): Expense amount
        category (str): Category of expense (e.g., Food, Transport)
        date (datetime): Date of expense
        description (str): Natural language description
        created_at (datetime): Timestamp when record was created
    """
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False, default=datetime.now)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, category='{self.category}', date='{self.date}')>"
    
    def to_dict(self):
        """Convert expense to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
