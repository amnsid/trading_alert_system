#!/usr/bin/env python3
"""
Configuration Helper Script
Helps you set up the CONFIG section in app.py
"""

print("Trading Alert System - Configuration Setup")
print("=" * 50)

print("""
STEP 1: Get Zerodha API Credentials
==================================
1. Go to https://kite.trade/
2. Login and create an app
3. Get your API_KEY and ACCESS_TOKEN

STEP 2: Get Instrument Tokens  
============================
1. Download: https://api.kite.trade/instruments
2. Open the CSV file and search for:
   - "NIFTY 50" (spot) - copy the instrument_token
   - "NIFTY BANK" (spot) - copy the instrument_token
   - "NIFTY 200" - for reference index

STEP 3: Setup Gmail App Password
===============================
1. Enable 2-Factor Authentication on Gmail
2. Go to Google Account > Security > App passwords
3. Generate new app password for "Mail"
4. Use this password (not your regular Gmail password)

STEP 4: Update CONFIG in app.py
==============================
""")

sample_config = '''
CONFIG = {
    # Replace these with your actual credentials
    'API_KEY': 'your_actual_api_key_here',
    'ACCESS_TOKEN': 'your_actual_access_token_here',
    
    # Replace with actual instrument tokens from the CSV
    'NIFTY_TOKEN': '256265',        # Example - get actual from instruments.csv
    'BANKNIFTY_TOKEN': '260105',    # Example - get actual from instruments.csv  
    'NIFTY200_TOKEN': '13297412',   # Example - get actual from instruments.csv
    'BN200_TOKEN': '260105',        # Can use BANKNIFTY or another index
    
    # Update with your email settings
    'SMTP_HOST': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'EMAIL_USER': 'your_email@gmail.com',
    'EMAIL_PASS': 'your_gmail_app_password',  # App password, not regular password
    'ALERT_TO': 'recipient@gmail.com',
    
    # Keep True for testing, set False for live alerts
    'DRY_RUN': True,
    'LOG_FILE': 'alerts_log.csv',
    'TIMEZONE': 'Asia/Kolkata'
}
'''

print(sample_config)

print("""
STEP 5: Test the Configuration
=============================
1. Update CONFIG in app.py with your actual values
2. Keep DRY_RUN = True for testing
3. Run: python app.py
4. If successful, you'll see connection confirmation

STEP 6: Go Live
==============
1. Set DRY_RUN = False in CONFIG
2. Run: python app.py
3. System will monitor until 2:30 PM IST daily

Ready to configure? (Y/n): """)

response = input().strip().lower()
if response in ['y', 'yes', '']:
    print("\n✅ Great! Follow the steps above to configure your system.")
    print("💡 Tip: Start with DRY_RUN=True to test everything first!")
else:
    print("\n📝 Configuration guide saved. Come back when you're ready!")
