import streamlit as st
import pandas as pd
from data_loader import process_client_trades
from pivot_tables import create_instrument_pivot_table, create_date_pivot_table
from config import VIEW_TYPES, CLIENT_VIEW_TYPES

def display_client_view(df, selected_client_code, client_trades):
    """Display client view with instrument or date grouping"""
    client_view_type = st.radio(
        "Client View Type",
        CLIENT_VIEW_TYPES,
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

def display_date_view(df, all_codes):
    """Display date view showing all clients' trades"""
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

def create_sidebar(df, all_codes):
    """Create sidebar with client selection"""
    st.sidebar.title("Client Selection")
    
    # Add new client code input
    new_client_code = st.sidebar.text_input(
        "Add new client code",
        help="Enter a new client code to add to the list"
    )
    
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
        
        return selected_client.split(' - ')[0], all_codes
    else:
        st.sidebar.error("No matching clients found")
        return None, all_codes 