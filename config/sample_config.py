# Sample Configuration File
# Copy this to your app.py CONFIG section and update with your actual credentials

SAMPLE_CONFIG = {
    # Zerodha KiteConnect API credentials
    # Get these from https://kite.trade/
    'API_KEY': 'your_api_key_here',  # Replace with your actual API key
    'ACCESS_TOKEN': 'your_access_token_here',  # Replace with your access token
    
    # Instrument tokens (get these from https://api.kite.trade/instruments)
    # Download the CSV and search for these instruments:
    'NIFTY_TOKEN': '256265',        # NIFTY 50 spot token (example)
    'BANKNIFTY_TOKEN': '260105',    # NIFTY BANK spot token (example)
    'NIFTY200_TOKEN': '13297412',   # NIFTY 200 token for RS calculation
    'BN200_TOKEN': '260105',        # Use BANKNIFTY itself or another index
    
    # Email SMTP configuration (Gmail example)
    'SMTP_HOST': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'EMAIL_USER': 'your_email@gmail.com',      # Your Gmail address
    'EMAIL_PASS': 'your_app_password',         # Gmail App Password (not regular password)
    'ALERT_TO': 'recipient@gmail.com',         # Where to send alerts
    
    # System settings
    'DRY_RUN': True,                           # Keep True for testing
    'LOG_FILE': 'alerts_log.csv',
    'TIMEZONE': 'Asia/Kolkata'
}

# Gmail App Password Setup:
# 1. Enable 2-Factor Authentication on your Gmail account
# 2. Go to Google Account settings > Security > App passwords
# 3. Generate a new app password for "Mail"
# 4. Use this app password in EMAIL_PASS field (not your regular password)

# Getting Instrument Tokens:
# 1. Visit https://api.kite.trade/instruments
# 2. Download the CSV file
# 3. Search for "NIFTY 50" and "NIFTY BANK" to find the exact tokens
# 4. Update the tokens in the CONFIG section of app.py
