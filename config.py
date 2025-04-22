import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Default client codes for caching
DEFAULT_CLIENT_CODES = [
    '051851',
    '051852',
    '051853'
]

# File paths
TRADE_HISTORY_FILE = r"C:\Users\cheng\OneDrive\Desktop\DYJ\Cursor\DYJ_AI\GTJA_Files\Trade History_as_at_20250105_20250303.xls"

# Numeric columns that need cleaning
NUMERIC_COLUMNS = [
    'Quantity',
    'Executed_Price',
    'Consideration'
]

# Pivot table column configurations
PIVOT_REQUIRED_COLUMNS = [
    ('Quantity', 'BUY'),
    ('Quantity', 'SELL'),
    ('Executed_Price', 'BUY'),
    ('Executed_Price', 'SELL')
]

# View types
VIEW_TYPES = ["By Client", "By Date"]
CLIENT_VIEW_TYPES = ["By Instrument", "By Date"] 