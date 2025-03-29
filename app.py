import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os
from utils import load_data, save_data, initialize_data
from calendar_integration import create_date_picker_with_suggestions

# Page configuration and styling
st.set_page_config(page_title="Expense Tracker", layout="centered")
st.markdown("""
    <style>
    /* General Styling */
    .block-container {
        padding-top: 2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4776E6 !important;
        color: white !important;
    }
    
    /* Credit Button Styling */
    .credit-button button {
        background: linear-gradient(to right, #00b09b, #96c93d) !important;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .credit-button button:hover {
        background: linear-gradient(to right, #96c93d, #00b09b) !important;
    }
    
    /* Debit Button Styling */
    .debit-button button {
        background: linear-gradient(to right, #FF416C, #FF4B2B) !important;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .debit-button button:hover {
        background: linear-gradient(to right, #FF4B2B, #FF416C) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 Expense Tracker")

# Initialize session state for balance
if 'current_balance' not in st.session_state:
    st.session_state.current_balance = 0.0
    
# Define category icons and colors for use throughout the app
CATEGORY_INFO = {
    "🍔 Food": {"color": "#FF9F1C", "description": "Restaurants, groceries, food delivery"},
    "🚌 Transportation": {"color": "#2EC4B6", "description": "Public transit, fuel, ride services"},
    "🏠 Housing": {"color": "#E71D36", "description": "Rent, mortgage, maintenance"},
    "💡 Utilities": {"color": "#011627", "description": "Electricity, water, internet, gas"},
    "🎮 Entertainment": {"color": "#8338EC", "description": "Movies, games, streaming services"},
    "🏥 Healthcare": {"color": "#FF006E", "description": "Doctor visits, medicine, insurance"},
    "🛍️ Shopping": {"color": "#FB5607", "description": "Clothing, electronics, personal items"},
    "💰 Salary": {"color": "#3A86FF", "description": "Regular income from employment"},
    "💼 Business": {"color": "#8AC926", "description": "Business income and expenses"},
    "🎓 Education": {"color": "#FFBE0B", "description": "Tuition, books, courses"},
    "✈️ Travel": {"color": "#9B5DE5", "description": "Vacations, hotels, flights"},
    "🎁 Gifts": {"color": "#F15BB5", "description": "Presents, donations, charity"},
    "💸 Investments": {"color": "#00BBF9", "description": "Stocks, mutual funds, crypto"},
    "💳 Loan Payment": {"color": "#4361EE", "description": "EMIs, credit card payments"},
    "📱 Subscriptions": {"color": "#4CC9F0", "description": "Monthly services, memberships"},
    "📦 Other": {"color": "#B5BAC7", "description": "Miscellaneous expenses"}
}

# Load or initialize data
df = load_data()
if df.empty:
    initialize_data()
    df = load_data()

# Calculate current balance
st.session_state.current_balance = df['Amount'].sum()

# Main transaction form
st.header("Add Transaction")
col1, col2 = st.columns(2)

with col1:
    transaction_type = st.selectbox("Type", ["💸 Expense", "💵 Income"])
    amount = st.number_input("Amount (₹)", min_value=0.01, format="%.2f")

with col2:
    # Get the list of categories from our dictionary
    categories = list(CATEGORY_INFO.keys())
    
    # Store the selected index for use in CSS
    if 'selected_category_index' not in st.session_state:
        st.session_state.selected_category_index = 0
    
    # Show category name and info on hover
    selected_category = st.selectbox(
        "Category", 
        categories,
        index=st.session_state.selected_category_index,
        format_func=lambda x: f"{x} - {CATEGORY_INFO[x]['description'][:20]}..."
    )
    
    # Update the selected index in session state
    st.session_state.selected_category_index = categories.index(selected_category)
    
    # Display a color indicator for the selected category
    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 8px;
            background-color: {CATEGORY_INFO[selected_category]['color']};
            border-radius: 4px;
            margin-bottom: 10px;">
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Use our enhanced date picker with calendar integration
    date = create_date_picker_with_suggestions()

description = st.text_input("Description")

transaction_button = "Expense" if "💸" in transaction_type else "Income"
button_style = "debit-button" if "💸" in transaction_type else "credit-button"

with st.container():
    st.markdown(f"""<div class="{button_style}">""", unsafe_allow_html=True)
    if st.button(f"Add {transaction_button}"):
        amount_final = -amount if "💸" in transaction_type else amount
        new_transaction = pd.DataFrame({
            'Date': [date],
            'Category': [selected_category],
            'Description': [description],
            'Amount': [amount_final],
            'Type': [transaction_type]
        })
        df = pd.concat([df, new_transaction], ignore_index=True)
        save_data(df)
        st.success(f"{transaction_type} of ₹{amount:,.2f} added successfully!")
        st.rerun()
    st.markdown("""</div>""", unsafe_allow_html=True)

# Main content section with account summary
st.markdown("### 💼 Account Summary")
col1, col2 = st.columns(2)

# Display current balance and warning
with col1:
    st.metric("Current Balance", f"₹{st.session_state.current_balance:,.2f}")
    if st.session_state.current_balance < 1000:  # Updated threshold for INR
        st.warning("⚠️ Low balance warning! Below ₹1,000")

# Time period filter
with col2:
    time_period = st.selectbox("Select Time Period", 
                             ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])

# Filter data based on time period
current_date = datetime.now().date()
if time_period != "All Time":
    days = int(time_period.split()[1])
    start_date = current_date - timedelta(days=days)
    df_filtered = df[pd.to_datetime(df['Date']).dt.date >= start_date]
else:
    df_filtered = df.copy()

# Financial statistics cards
col3, col4, col5 = st.columns(3)

with col3:
    total_income = df_filtered[df_filtered['Amount'] > 0]['Amount'].sum()
    st.metric("💵 Income", f"₹{total_income:,.2f}")

with col4:
    total_expenses = abs(df_filtered[df_filtered['Amount'] < 0]['Amount'].sum())
    st.metric("💸 Expenses", f"₹{total_expenses:,.2f}")

with col5:
    if total_income > 0:
        savings_rate = ((total_income - total_expenses) / total_income) * 100
        st.metric("💰 Savings Rate", f"{savings_rate:.1f}%")

# Create tabs for Analytics and Transactions
tab1, tab2 = st.tabs(["📊 Analytics & Charts", "📝 Transactions"])

with tab1:
    st.header("💹 Analytics Dashboard")
    
    # Expense by Category section
    st.subheader("Expense Distribution by Category")
    expenses_by_category = df_filtered[df_filtered['Amount'] < 0].groupby('Category')['Amount'].sum().abs()
    
    if not expenses_by_category.empty:
        # Get category colors for the pie chart
        category_colors = []
        for category in expenses_by_category.index:
            if category in CATEGORY_INFO:
                category_colors.append(CATEGORY_INFO[category]['color'])
            else:
                category_colors.append("#B5BAC7")  # Default color for unknown categories
                
        fig_category = px.pie(
            values=expenses_by_category.values, 
            names=expenses_by_category.index,
            title="Where is your money going?",
            hover_data=[expenses_by_category.values],
            custom_data=[expenses_by_category.values.round(2)],
            color_discrete_sequence=category_colors
        )
        
        fig_category.update_traces(
            hovertemplate="<b>%{label}</b><br>Amount: ₹%{customdata[0]:,.2f}<extra></extra>",
            textinfo='label+percent',
            textposition='inside'
        )
        
        fig_category.update_layout(
            margin=dict(t=30, b=0, l=0, r=0),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1.0,
                xanchor="right",
                x=1.0
            )
        )
        
        st.plotly_chart(fig_category, use_container_width=True)
        
        # Display a legend with category descriptions
        st.markdown("#### Category Legend")
        legend_cols = st.columns(3)
        
        for i, (category, value) in enumerate(expenses_by_category.items()):
            col_idx = i % 3
            if category in CATEGORY_INFO:
                with legend_cols[col_idx]:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <div style="width: 15px; height: 15px; background-color: {CATEGORY_INFO[category]['color']}; 
                                    border-radius: 50%; margin-right: 8px;"></div>
                            <div>
                                <b>{category}</b><br>
                                <small style="color: #666;">{CATEGORY_INFO[category]['description']}</small><br>
                                <b style="color: #333;">₹{value:,.2f}</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
    else:
        st.info("No expense data available for the selected period.")
    
    # Spending over time chart
    st.subheader("Financial Trends")
    daily_expenses = df_filtered.groupby('Date')['Amount'].sum().reset_index()
    
    if not daily_expenses.empty:
        fig_timeline = px.line(
            daily_expenses, 
            x='Date', 
            y='Amount',
            title="Balance Progression Over Time",
            labels={'Amount': 'Amount (₹)', 'Date': 'Date'},
            markers=True
        )
        fig_timeline.update_traces(
            hovertemplate="Date: %{x}<br>Amount: ₹%{y:,.2f}<extra></extra>"
        )
        fig_timeline.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Income vs Expense bar chart
        income_expense_by_date = df_filtered.copy()
        income_expense_by_date['Income'] = income_expense_by_date['Amount'].apply(lambda x: max(x, 0))
        income_expense_by_date['Expense'] = income_expense_by_date['Amount'].apply(lambda x: abs(min(x, 0)))
        income_expense_by_date = income_expense_by_date.groupby('Date')[['Income', 'Expense']].sum().reset_index()
        
        fig_bar = px.bar(
            income_expense_by_date,
            x='Date',
            y=['Income', 'Expense'],
            title='Income vs Expense Comparison',
            labels={'value': 'Amount (₹)', 'Date': 'Date'},
            barmode='group',
            color_discrete_map={'Income': '#00b09b', 'Expense': '#FF416C'}
        )
        fig_bar.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        fig_bar.update_traces(hovertemplate="%{y:,.2f}₹<extra></extra>")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No transaction data available for the selected period.")

with tab2:
    st.header("📝 Transaction History")
    
    # Transaction filtering options
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        transaction_filter = st.selectbox(
            "Filter by Transaction Type", 
            ["All Transactions", "💵 Income Only", "💸 Expense Only"]
        )
    
    with filter_col2:
        if len(set(df_filtered['Category'].tolist())) > 0:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All Categories"] + sorted(set(df_filtered['Category'].tolist()))
            )
        else:
            category_filter = "All Categories"
    
    # Apply filters
    if transaction_filter == "💵 Income Only":
        transactions_filtered = df_filtered[df_filtered['Amount'] > 0]
    elif transaction_filter == "💸 Expense Only":
        transactions_filtered = df_filtered[df_filtered['Amount'] < 0]
    else:
        transactions_filtered = df_filtered.copy()
    
    if category_filter != "All Categories":
        transactions_filtered = transactions_filtered[transactions_filtered['Category'] == category_filter]
    
    # Display transaction table
    if not transactions_filtered.empty:
        transactions_display = transactions_filtered[['Date', 'Category', 'Description', 'Amount', 'Type']].copy()
        
        # Format amount with INR currency symbol
        transactions_display['Amount'] = transactions_display['Amount'].apply(
            lambda x: f"₹{x:,.2f}" if x < 0 else f"+₹{x:,.2f}"
        )
        
        # Add color to the amount column based on whether it's an expense or income
        styled_df = transactions_display.sort_values('Date', ascending=False).style.apply(
            lambda x: ['color: #FF416C' if '-' in v else 'color: #00b09b' 
                      if '+' in v else '' for v in x], 
            subset=['Amount']
        )
        
        # Display the styled dataframe
        st.dataframe(
            styled_df,
            hide_index=True,
            use_container_width=True
        )
        
        # Display transactions count with more context
        if len(transactions_display) == 1:
            st.info(f"Showing 1 transaction for the selected period.")
        else:
            st.info(f"Showing {len(transactions_display)} transactions for the selected period.")
    else:
        st.info("No transactions found matching the selected filters.")
        
    # Summary of filtered transactions
    if not transactions_filtered.empty:
        st.subheader("Summary")
        sum_value = transactions_filtered['Amount'].sum()
        st.metric(
            "Total for filtered transactions", 
            f"₹{sum_value:,.2f}",
            delta=None
        )