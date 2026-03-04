"""
Streamlit UI for Agentic AI Expense Tracker

Interactive web interface for natural language expense tracking.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from database.db_manager import DatabaseManager
from agent.agent import ExpenseAgent
from utils.helpers import format_currency, format_date, get_month_name
import os


# Page configuration
st.set_page_config(
    page_title="AI Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .expense-item {
        padding: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_database():
    """Load database manager (cached)."""
    return DatabaseManager("sqlite:///./database/expenses.db")


@st.cache_resource
def load_agent():
    """Load AI agent (cached)."""
    db = load_database()
    return ExpenseAgent(db_manager=db)


def initialize_session_state():
    """Initialize session state variables."""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""


def render_chat_interface(agent):
    """Render the chat interface for natural language input."""
    st.markdown("### 💬 Chat with AI Agent")
    st.write("Enter expenses or ask questions in natural language!")
    
    # Display conversation history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.conversation[-10:]:  # Show last 10 messages
            if message['role'] == 'user':
                st.markdown(f"**👤 You:** {message['content']}")
            else:
                st.markdown(f"**🤖 Agent:** {message['content']}")
    
    # User input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to conversation
        st.session_state.conversation.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # Process through agent
        with st.spinner("Processing..."):
            result = agent.process_input(user_input)
        
        # Add agent response
        st.session_state.conversation.append({
            'role': 'assistant',
            'content': result['message'],
            'timestamp': datetime.now()
        })
        
        # Rerun to show new messages
        st.rerun()


def render_expense_form(agent):
    """Render manual expense entry form."""
    st.markdown("### 📝 Manual Entry")
    
    with st.form("expense_form", clear_on_submit=True):
        amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01)
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Shopping", "Entertainment", "Bills", 
             "Healthcare", "Education", "Personal", "Other"]
        )
        date = st.date_input("Date", value=datetime.now())
        description = st.text_area("Description (optional)")
        
        submitted = st.form_submit_button("Add Expense", use_container_width=True)
        
        if submitted and amount > 0:
            try:
                db = load_database()
                expense = db.add_expense(
                    amount=amount,
                    category=category,
                    date=datetime.combine(date, datetime.min.time()),
                    description=description
                )
                st.success(f"✅ Expense #{expense.id} added successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")


def render_monthly_summary(db):
    """Render monthly summary section."""
    st.markdown("### 📊 Monthly Summary")
    
    # Get current month summary
    summary = db.get_current_month_summary()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f"{get_month_name(summary['month'])} {summary['year']}",
            value=format_currency(summary['total_amount']),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Categories",
            value=summary['expense_count'],
            delta=None
        )
    
    with col3:
        avg_expense = summary['total_amount'] / max(summary['expense_count'], 1)
        st.metric(
            label="Average per Category",
            value=format_currency(avg_expense),
            delta=None
        )
    
    # Category breakdown chart
    if summary['category_breakdown']:
        st.subheader("Category Breakdown")
        
        df = pd.DataFrame([
            {"Category": cat, "Amount": amt}
            for cat, amt in summary['category_breakdown'].items()
        ])
        
        fig = px.bar(
            df,
            x="Category",
            y="Amount",
            title="Expenses by Category",
            color="Amount",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)


def render_category_report(db):
    """Render category-wise report."""
    st.markdown("### 📈 Category Report")
    
    report = db.get_category_wise_report()
    
    if not report:
        st.info("No expenses recorded yet. Start adding expenses!")
        return
    
    # Create DataFrame
    df = pd.DataFrame(report)
    
    # Display as table
    st.dataframe(
        df[['category', 'total', 'count', 'percentage']],
        use_container_width=True,
        hide_index=True
    )
    
    # Pie chart
    fig = px.pie(
        df,
        values='total',
        names='category',
        title='Expense Distribution by Category',
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)


def render_recent_expenses(db):
    """Render recent expenses list."""
    st.markdown("### 🕐 Recent Expenses")
    
    expenses = db.get_recent_expenses(10)
    
    if not expenses:
        st.info("No expenses yet. Add your first expense!")
        return
    
    for expense in expenses:
        with st.expander(
            f"**{format_currency(expense.amount)}** - {expense.category} ({format_date(expense.date, 'short')})"
        ):
            if expense.description:
                st.write(f"📝 {expense.description}")
            st.write(f"**ID:** {expense.id}")
            st.write(f"**Recorded:** {format_date(expense.created_at, 'datetime')}")
            
            # Delete button
            if st.button("Delete", key=f"delete_{expense.id}"):
                db.delete_expense(expense.id)
                st.success("Expense deleted!")
                st.rerun()


def render_dashboard(db):
    """Render main dashboard."""
    st.markdown('<p class="main-header">💰 AI Expense Tracker Dashboard</p>', unsafe_allow_html=True)
    
    # Quick stats
    all_expenses = db.get_all_expenses()
    total_spent = sum(exp.amount for exp in all_expenses)
    this_month = db.get_current_month_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Spent", format_currency(total_spent))
    
    with col2:
        st.metric("This Month", format_currency(this_month['total_amount']))
    
    with col3:
        st.metric("Total Expenses", len(all_expenses))
    
    with col4:
        st.metric("Categories Used", this_month['expense_count'])
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly trend (simplified - last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent = db.get_expenses_by_date_range(thirty_days_ago, datetime.now())
        
        if recent:
            daily_totals = {}
            for exp in recent:
                date_key = exp.date.strftime('%Y-%m-%d')
                daily_totals[date_key] = daily_totals.get(date_key, 0) + exp.amount
            
            df = pd.DataFrame([
                {"Date": date, "Amount": amt}
                for date, amt in sorted(daily_totals.items())
            ])
            
            fig = px.line(
                df,
                x="Date",
                y="Amount",
                title="Spending Trend (Last 30 Days)",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category distribution
        report = db.get_category_wise_report()
        if report:
            df = pd.DataFrame(report)
            fig = px.pie(
                df,
                values='total',
                names='category',
                title="Category Distribution",
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)


def main():
    """Main application function."""
    initialize_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Chat with AI", "Manual Entry", "Reports", "Analytics"]
    )
    
    # Load components
    db = load_database()
    agent = load_agent()
    
    # Render selected page
    if page == "Dashboard":
        render_dashboard(db)
        st.divider()
        render_recent_expenses(db)
    
    elif page == "Chat with AI":
        render_chat_interface(agent)
    
    elif page == "Manual Entry":
        render_expense_form(agent)
        st.divider()
        render_recent_expenses(db)
    
    elif page == "Reports":
        render_monthly_summary(db)
        st.divider()
        render_category_report(db)
    
    elif page == "Analytics":
        st.markdown("### 📊 Analytics & Insights")
        
        # Time period selector
        time_period = st.selectbox(
            "Select Time Period",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
        )
        
        from datetime import timedelta
        
        if time_period == "Last 7 Days":
            days = 7
        elif time_period == "Last 30 Days":
            days = 30
        elif time_period == "Last 90 Days":
            days = 90
        else:
            days = 365 * 10  # ~All time
        
        start_date = datetime.now() - timedelta(days=days)
        expenses = db.get_expenses_by_date_range(start_date, datetime.now())
        
        if expenses:
            # Daily aggregation
            daily_data = {}
            for exp in expenses:
                date_key = exp.date.strftime('%Y-%m-%d')
                if date_key not in daily_data:
                    daily_data[date_key] = 0
                daily_data[date_key] += exp.amount
            
            df = pd.DataFrame([
                {"Date": date, "Amount": amt}
                for date, amt in sorted(daily_data.items())
            ])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.area(
                    df,
                    x="Date",
                    y="Amount",
                    title=f"Daily Spending ({time_period})",
                    fill="tozeroy"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Category breakdown for period
                category_totals = {}
                for exp in expenses:
                    category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount
                
                cat_df = pd.DataFrame([
                    {"Category": cat, "Amount": amt}
                    for cat, amt in category_totals.items()
                ])
                
                fig = px.bar(
                    cat_df,
                    x="Amount",
                    y="Category",
                    orientation='h',
                    title="Category Breakdown",
                    color="Amount",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected period.")
    
    # Footer
    st.sidebar.divider()
    st.sidebar.markdown("""
    ### ℹ️ About
    **AI Expense Tracker** uses natural language processing to make expense tracking effortless.
    
    **Features:**
    - 💬 Natural language input
    - 🤖 AI-powered entity extraction
    - 📊 Interactive charts
    - 📱 Responsive design
    
    Built with ❤️ using Streamlit
    """)


if __name__ == "__main__":
    main()
