@echo off
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_SERVER_ADDRESS=localhost
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
call .\venv\Scripts\activate.bat
streamlit run client_trade_analyzer.py 