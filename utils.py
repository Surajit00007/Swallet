import pandas as pd
import os

TRANSACTION_FILE = "data/transactions.csv"

def load_data():
    """Load transaction data from CSV file."""
    if os.path.exists(TRANSACTION_FILE):
        return pd.read_csv(TRANSACTION_FILE)
    return pd.DataFrame()

def save_data(df):
    """Save transaction data to CSV file."""
    os.makedirs(os.path.dirname(TRANSACTION_FILE), exist_ok=True)
    df.to_csv(TRANSACTION_FILE, index=False)

def initialize_data():
    """Initialize empty transaction data file."""
    df = pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount', 'Type'])
    save_data(df)
