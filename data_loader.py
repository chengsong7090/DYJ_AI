import pandas as pd
import streamlit as st
from config import NUMERIC_COLUMNS, DEFAULT_CLIENT_CODES

def clean_numeric_column(df, column_name):
    """Helper function to clean and convert numeric columns"""
    if column_name in df.columns:
        # Convert to string and clean
        df[column_name] = df[column_name].astype(str)
        df[column_name] = df[column_name].str.replace(',', '').str.replace(' ', '')
        # Handle any special cases
        df[column_name] = df[column_name].replace('nan', pd.NA)
        df[column_name] = df[column_name].replace('None', pd.NA)
        df[column_name] = df[column_name].replace('', pd.NA)
        # Convert to numeric
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    return df

@st.cache_data
def load_trade_history(file_path):
    """Load and process trade history data"""
    try:
        print(f"Attempting to load file: {file_path}")
        # Read Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"Successfully loaded file. Shape: {df.shape}")
        
        # Convert TradeDate to datetime and format to date only
        df['TradeDate'] = pd.to_datetime(df['TradeDate']).dt.date
        
        # Sort by date
        df = df.sort_values('TradeDate')
        
        # Convert ClntCode to string, strip whitespace, and ensure consistent format
        df['ClntCode'] = df['ClntCode'].astype(str).str.strip().str.zfill(6)
        
        # Debug information
        print("\nDebug Information:")
        print(f"Unique client codes in data: {sorted(df['ClntCode'].unique().tolist())}")
        print(f"Default client codes: {DEFAULT_CLIENT_CODES}")
        print(f"Is 051851 in data: {'051851' in df['ClntCode'].unique()}")
        print(f"Sample of ClntCode values: {df['ClntCode'].head().tolist()}")
        print(f"Data types: {df.dtypes}")
        
        # Clean and convert numeric columns
        for col in NUMERIC_COLUMNS:
            df = clean_numeric_column(df, col)
        
        # Additional debug for client 051851
        client_051851 = df[df['ClntCode'] == '051851']
        print(f"\nClient 051851 data:")
        print(f"Number of trades: {len(client_051851)}")
        print(f"Sample trades: {client_051851[['TradeDate', 'Instrument', 'BuySell', 'Quantity', 'Executed_Price']].head()}")
        
        return df
    except Exception as e:
        print(f"Error loading Excel file: {str(e)}")
        st.error(f"Error loading Excel file: {str(e)}")
        return None

@st.cache_data
def process_default_client_trades(df, client_code):
    """Process trades for default clients with caching"""
    try:
        # Convert client_code to string, strip whitespace, and ensure consistent format
        client_code = str(client_code).strip().zfill(6)
        
        # Filter for specific client
        client_df = df[df['ClntCode'] == client_code].copy()
        
        if client_df.empty:
            st.warning(f"No trades found for client code: {client_code}")
            return None
        
        # Group by Instrument, InstrumentName, TradeDate, and BuySell
        grouped = client_df.groupby(['Instrument', 'InstrumentName', 'TradeDate', 'BuySell'])
        
        # Calculate summary statistics
        summary = grouped.agg({
            'Quantity': 'sum',
            'Executed_Price': 'mean',
            'Consideration': 'sum'
        }).reset_index()
        
        # Calculate total summary
        total_summary = client_df.groupby(['Instrument', 'InstrumentName', 'BuySell']).agg({
            'Quantity': 'sum',
            'Executed_Price': 'mean',
            'Consideration': 'sum'
        }).reset_index()
        total_summary['TradeDate'] = 'Total'
        
        # Combine daily and total summaries
        final_summary = pd.concat([summary, total_summary])
        
        return final_summary
    except Exception as e:
        st.error(f"Error processing trades for client {client_code}: {str(e)}")
        return None

def process_client_trades(df, client_code):
    """Process trades for a specific client"""
    try:
        # Convert client_code to string, strip whitespace, and ensure consistent format
        client_code = str(client_code).strip().zfill(6)
        
        # Use cached function for default clients
        if client_code in DEFAULT_CLIENT_CODES:
            return process_default_client_trades(df, client_code)
        
        # For non-default clients, use the original processing logic
        client_df = df[df['ClntCode'] == client_code].copy()
        
        if client_df.empty:
            st.warning(f"No trades found for client code: {client_code}")
            return None
        
        # Group by Instrument, InstrumentName, TradeDate, and BuySell
        grouped = client_df.groupby(['Instrument', 'InstrumentName', 'TradeDate', 'BuySell'])
        
        # Calculate summary statistics
        summary = grouped.agg({
            'Quantity': 'sum',
            'Executed_Price': 'mean',
            'Consideration': 'sum'
        }).reset_index()
        
        # Calculate total summary
        total_summary = client_df.groupby(['Instrument', 'InstrumentName', 'BuySell']).agg({
            'Quantity': 'sum',
            'Executed_Price': 'mean',
            'Consideration': 'sum'
        }).reset_index()
        total_summary['TradeDate'] = 'Total'
        
        # Combine daily and total summaries
        final_summary = pd.concat([summary, total_summary])
        
        return final_summary
    except Exception as e:
        st.error(f"Error processing trades for client {client_code}: {str(e)}")
        return None 