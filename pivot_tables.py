import pandas as pd
from config import PIVOT_REQUIRED_COLUMNS

def create_instrument_pivot_table(instrument_trades):
    """Create and format pivot table by instrument"""
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
        for col in PIVOT_REQUIRED_COLUMNS:
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
    """Create and format pivot table by date"""
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
        for col in PIVOT_REQUIRED_COLUMNS:
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