import pandas as pd
import streamlit as st
from datetime import datetime
import os
import sys
import numpy as np

# Set environment variables to prevent email prompt
os.environ['STREAMLIT_SERVER_EMAIL'] = ''
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Add debug information
print("Starting program...")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"File path: {os.path.abspath(__file__)}")

# Set page configuration
st.set_page_config(
    page_title="Client Trade Analyzer",
    page_icon="📊",
    layout="wide"
)

# Default client codes (as strings to preserve leading zeros)
DEFAULT_CLIENT_CODES = ['118095', '051851', '915310', '912812', '207188']

def clean_numeric_column(df, column_name):
    """Helper function to clean and convert numeric columns"""
    if column_name in df.columns:
        # Convert to string and clean
        df[column_name] = df[column_name].astype(str)
        df[column_name] = df[column_name].str.replace(',', '').str.replace(' ', '')
        # Handle any special cases
        df[column_name] = df[column_name].replace('nan', np.nan)
        df[column_name] = df[column_name].replace('None', np.nan)
        df[column_name] = df[column_name].replace('', np.nan)
        # Convert to numeric
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    return df

# Function to load and process trade history
def load_trade_history(file_path):
    try:
        print(f"Attempting to load file: {file_path}")
        # Read Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"Successfully loaded file. Shape: {df.shape}")
        
        # Convert TradeDate to datetime and format to date only
        df['TradeDate'] = pd.to_datetime(df['TradeDate']).dt.date
        
        # Sort by date
        df = df.sort_values('TradeDate')
        
        # Convert ClntCode to string and strip any whitespace
        df['ClntCode'] = df['ClntCode'].astype(str).str.strip()
        print(f"Unique client codes in data: {df['ClntCode'].unique().tolist()}")
        
        # Clean and convert numeric columns
        numeric_columns = ['Quantity', 'Executed_Price', 'Consideration']
        for col in numeric_columns:
            df = clean_numeric_column(df, col)
        
        return df
    except Exception as e:
        print(f"Error loading Excel file: {str(e)}")
        st.error(f"Error loading Excel file: {str(e)}")
        return None

# Function to process trades for a specific client
def process_client_trades(df, client_code):
    try:
        # Convert client_code to string and strip whitespace
        client_code = str(client_code).strip()
        print(f"Processing trades for client code: {client_code}")
        print(f"Available client codes: {df['ClntCode'].unique().tolist()}")
        
        # Filter for specific client
        client_df = df[df['ClntCode'] == client_code].copy()
        
        if client_df.empty:
            print(f"No trades found for client code: {client_code}")
            st.warning(f"No trades found for client code: {client_code}")
            return None
        
        print(f"Found {len(client_df)} trades for client {client_code}")
        
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
        print(f"Error processing trades for client {client_code}: {str(e)}")
        st.error(f"Error processing trades for client {client_code}: {str(e)}")
        return None

def create_instrument_pivot_table(instrument_trades):
    """Helper function to create and format pivot table by instrument"""
    try:
        # Create a copy to avoid modifying the original
        df = instrument_trades.copy()
        
        # Convert TradeDate to string to avoid Arrow serialization issues
        df['TradeDate'] = df['TradeDate'].astype(str)
        
        # Ensure numeric columns are properly formatted
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        df['Executed_Price'] = pd.to_numeric(df['Executed_Price'], errors='coerce').fillna(0)
        
        # Create pivot table with proper aggregation
        pivot_data = pd.DataFrame(df.pivot_table(
            index=['TradeDate'],
            columns='BuySell',
            values=['Quantity', 'Executed_Price'],
            aggfunc={
                'Quantity': 'sum',
                'Executed_Price': 'mean'
            },
            fill_value=0
        ))
        
        # Ensure all required columns exist
        required_columns = [
            ('Quantity', 'BUY'),
            ('Quantity', 'SELL'),
            ('Executed_Price', 'BUY'),
            ('Executed_Price', 'SELL')
        ]
        
        # Add missing columns with zeros
        for col in required_columns:
            if col not in pivot_data.columns:
                pivot_data[col] = 0
        
        # Reorder columns to show Quantity first
        new_columns = []
        for col in ['BUY', 'SELL']:
            new_columns.extend([('Quantity', col), ('Executed_Price', col)])
        
        # Reorder and rename columns
        pivot_data = pivot_data[new_columns]
        
        # Format the pivot table
        formatted_pivot = pivot_data.copy()
        
        # Handle Quantity columns
        for col in ['BUY', 'SELL']:
            if ('Quantity', col) in formatted_pivot.columns:
                formatted_pivot[('Quantity', col)] = formatted_pivot[('Quantity', col)].fillna(0).astype('Int64')
        
        # Handle Executed_Price columns
        for col in ['BUY', 'SELL']:
            if ('Executed_Price', col) in formatted_pivot.columns:
                formatted_pivot[('Executed_Price', col)] = formatted_pivot[('Executed_Price', col)].fillna(0).round(6)
        
        return formatted_pivot
    except Exception as e:
        print(f"Error creating instrument pivot table: {str(e)}")
        return None

def create_date_pivot_table(client_trades):
    """Helper function to create and format pivot table by date"""
    try:
        # Create a copy to avoid modifying the original
        df = client_trades.copy()
        
        # Convert TradeDate to string to avoid Arrow serialization issues
        df['TradeDate'] = df['TradeDate'].astype(str)
        
        # Ensure numeric columns are properly formatted
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        df['Executed_Price'] = pd.to_numeric(df['Executed_Price'], errors='coerce').fillna(0)
        
        # Create pivot table with proper aggregation
        pivot_data = pd.DataFrame(df.pivot_table(
            index=['TradeDate', 'Instrument', 'InstrumentName'],
            columns='BuySell',
            values=['Quantity', 'Executed_Price'],
            aggfunc={
                'Quantity': 'sum',
                'Executed_Price': 'mean'
            },
            fill_value=0
        ))
        
        # Ensure all required columns exist
        required_columns = [
            ('Quantity', 'BUY'),
            ('Quantity', 'SELL'),
            ('Executed_Price', 'BUY'),
            ('Executed_Price', 'SELL')
        ]
        
        # Add missing columns with zeros
        for col in required_columns:
            if col not in pivot_data.columns:
                pivot_data[col] = 0
        
        # Reorder columns to show Quantity first
        new_columns = []
        for col in ['BUY', 'SELL']:
            new_columns.extend([('Quantity', col), ('Executed_Price', col)])
        
        # Reorder and rename columns
        pivot_data = pivot_data[new_columns]
        
        # Format the pivot table
        formatted_pivot = pivot_data.copy()
        
        # Handle Quantity columns
        for col in ['BUY', 'SELL']:
            if ('Quantity', col) in formatted_pivot.columns:
                formatted_pivot[('Quantity', col)] = formatted_pivot[('Quantity', col)].fillna(0).astype('Int64')
        
        # Handle Executed_Price columns
        for col in ['BUY', 'SELL']:
            if ('Executed_Price', col) in formatted_pivot.columns:
                formatted_pivot[('Executed_Price', col)] = formatted_pivot[('Executed_Price', col)].fillna(0).round(6)
        
        return formatted_pivot
    except Exception as e:
        print(f"Error creating date pivot table: {str(e)}")
        return None

def main():
    st.title("Client Trade Analyzer")
    
    # File path
    file_path = r"C:\Users\cheng\OneDrive\Desktop\DYJ\Cursor\DYJ_AI\GTJA_Files\Trade History_as_at_20250105_20250303.xls"
    
    # Load data
    df = load_trade_history(file_path)
    
    if df is not None:
        try:
            # Create sidebar for client code list input
            st.sidebar.title("Client Selection")
            
            # Add new client code input
            new_client_code = st.sidebar.text_input(
                "Add new client code",
                help="Enter a new client code to add to the list"
            )
            
            # Start with default client codes
            all_codes = DEFAULT_CLIENT_CODES.copy()
            
            # Add new code if provided
            if new_client_code:
                if new_client_code not in all_codes:
                    all_codes.append(new_client_code)
            
            # Filter client info based on selected codes
            client_info = df[df['ClntCode'].isin(all_codes)][['ClntCode', 'ClntName']].drop_duplicates()
            
            if not client_info.empty:
                client_info['display'] = client_info['ClntCode'] + ' - ' + client_info['ClntName']
                
                # Create dropdown for filtered clients
                selected_client = st.sidebar.selectbox(
                    "Select a client",
                    options=client_info['display'].tolist()
                )
                
                # Get selected client code
                selected_client_code = selected_client.split(' - ')[0]
                
                # Add view selection
                view_type = st.radio(
                    "View Type",
                    ["By Client", "By Date"],
                    horizontal=True
                )
                
                if view_type == "By Client":
                    # Process trades for selected client
                    client_trades = process_client_trades(df, selected_client_code)
                    
                    if client_trades is not None:
                        # Add sub-view selection for client view
                        client_view_type = st.radio(
                            "Client View Type",
                            ["By Instrument", "By Date"],
                            horizontal=True
                        )
                        
                        if client_view_type == "By Instrument":
                            # Group by Instrument
                            for instrument in client_trades['Instrument'].unique():
                                instrument_trades = client_trades[client_trades['Instrument'] == instrument]
                                instrument_name = instrument_trades['InstrumentName'].iloc[0]
                                
                                with st.expander(f"{instrument} - {instrument_name}"):
                                    pivot_table = create_instrument_pivot_table(instrument_trades)
                                    if pivot_table is not None:
                                        st.dataframe(
                                            pivot_table,
                                            use_container_width=True
                                        )
                                    else:
                                        st.error(f"Error displaying data for {instrument}")
                        else:  # By Date for selected client
                            pivot_table = create_date_pivot_table(client_trades)
                            if pivot_table is not None:
                                st.dataframe(
                                    pivot_table,
                                    use_container_width=True
                                )
                            else:
                                st.error("Error displaying data by date")
                else:  # By Date view (all clients)
                    # Get unique dates from the data
                    unique_dates = sorted(df['TradeDate'].unique(), reverse=True)
                    selected_date = st.selectbox(
                        "Select a date",
                        options=unique_dates,
                        format_func=lambda x: x.strftime('%Y-%m-%d')
                    )
                    
                    # Filter trades for the selected date and selected clients
                    date_trades = df[
                        (df['TradeDate'] == selected_date) & 
                        (df['ClntCode'].isin(all_codes))
                    ].copy()
                    
                    if not date_trades.empty:
                        try:
                            # Calculate weighted average price
                            date_trades['Weighted_Price'] = date_trades['Executed_Price'] * date_trades['Quantity']
                            
                            # Group by Client, Instrument, and BuySell
                            grouped = date_trades.groupby(['ClntCode', 'ClntName', 'Instrument', 'InstrumentName', 'BuySell'])
                            
                            # Calculate summary statistics
                            summary = grouped.agg({
                                'Quantity': 'sum',
                                'Weighted_Price': 'sum'
                            }).reset_index()
                            
                            # Calculate weighted average price with zero division handling
                            summary['Weighted_Avg_Price'] = summary.apply(
                                lambda x: x['Weighted_Price'] / x['Quantity'] if x['Quantity'] != 0 else 0,
                                axis=1
                            )
                            
                            # Create pivot table
                            pivot_data = pd.pivot_table(
                                summary,
                                values=['Quantity', 'Weighted_Avg_Price'],
                                index=['ClntCode', 'ClntName', 'Instrument', 'InstrumentName'],
                                columns='BuySell',
                                fill_value=0
                            )
                            
                            # Ensure all required columns exist
                            required_columns = [
                                ('Quantity', 'BUY'),
                                ('Quantity', 'SELL'),
                                ('Weighted_Avg_Price', 'BUY'),
                                ('Weighted_Avg_Price', 'SELL')
                            ]
                            
                            # Add missing columns with zeros
                            for col in required_columns:
                                if col not in pivot_data.columns:
                                    pivot_data[col] = 0
                            
                            # Reorder columns to show Quantity before Price
                            new_columns = []
                            for col in ['BUY', 'SELL']:
                                new_columns.extend([('Quantity', col), ('Weighted_Avg_Price', col)])
                            
                            pivot_data = pivot_data[new_columns]
                            
                            # Format the pivot table
                            formatted_pivot = pivot_data.copy()
                            
                            # Format numeric columns
                            for col in ['BUY', 'SELL']:
                                if ('Quantity', col) in formatted_pivot.columns:
                                    formatted_pivot[('Quantity', col)] = formatted_pivot[('Quantity', col)].astype('Int64')
                                if ('Weighted_Avg_Price', col) in formatted_pivot.columns:
                                    formatted_pivot[('Weighted_Avg_Price', col)] = formatted_pivot[('Weighted_Avg_Price', col)].round(6)
                            
                            # Display the pivot table
                            st.dataframe(
                                formatted_pivot,
                                use_container_width=True
                            )
                        except Exception as e:
                            print(f"Error processing date view: {str(e)}")
                            st.error(f"Error processing date view: {str(e)}")
                    else:
                        st.warning(f"No trades found for the selected date: {selected_date.strftime('%Y-%m-%d')}")
            else:
                st.sidebar.error("No matching clients found")
                
        except Exception as e:
            print(f"Error in main function: {str(e)}")
            st.error(f"Error displaying data: {str(e)}")

if __name__ == "__main__":
    main() 