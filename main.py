import streamlit as st
from data_loader import load_trade_history, process_client_trades
from ui import display_client_view, display_date_view, create_sidebar
from config import TRADE_HISTORY_FILE, DEFAULT_CLIENT_CODES, VIEW_TYPES

def main():
    st.title("Client Trade Analyzer")
    
    # Load data
    df = load_trade_history(TRADE_HISTORY_FILE)
    
    if df is not None:
        try:
            # Start with default client codes
            all_codes = DEFAULT_CLIENT_CODES.copy()
            
            # Create sidebar and get selected client
            selected_client_code, all_codes = create_sidebar(df, all_codes)
            
            if selected_client_code is not None:
                # Add view selection
                view_type = st.radio(
                    "View Type",
                    VIEW_TYPES,
                    horizontal=True
                )
                
                if view_type == "By Client":
                    # Process trades for selected client
                    client_trades = process_client_trades(df, selected_client_code)
                    
                    if client_trades is not None:
                        display_client_view(df, selected_client_code, client_trades)
                else:  # By Date view
                    display_date_view(df, all_codes)
                
        except Exception as e:
            print(f"Error in main function: {str(e)}")
            st.error(f"Error displaying data: {str(e)}")

if __name__ == "__main__":
    main() 