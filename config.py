# Default client codes (as strings to preserve leading zeros)
DEFAULT_CLIENT_CODES = ['118095', '051851', '915310', '912812', '207188']

# File paths
TRADE_HISTORY_FILE = r"C:\Users\cheng\OneDrive\Desktop\DYJ\Cursor\DYJ_AI\GTJA_Files\Trade History_as_at_20250105_20250303.xls"

# Numeric columns to clean
NUMERIC_COLUMNS = ['Quantity', 'Executed_Price', 'Consideration']

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