# Trading Alert System

A comprehensive NIFTY/BANKNIFTY trading alert system that implements Master Rulebook requirements.

## Features ✅

- 5-minute candle monitoring for NIFTY & BANKNIFTY
- AVWAP calculation anchored to previous day High & Low
- Measure calculation for both buy/sell setups
- Relative Strength computation
- All 4 candlestick patterns (Green Hammer, Red Hammer, Inverted Hammer, Inverted Green Hammer)
- 2:30 PM IST cutoff enforcement
- Email alerts with SMTP configuration
- CSV logging with all required fields
- Duplicate prevention for same candle alerts
- Dry-run mode for testing

## Quick Setup (30 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Credentials
1. Get your Zerodha API key & access token from https://kite.trade/
2. Get instrument tokens from https://api.kite.trade/instruments
3. Update the CONFIG section in `app.py`

### 3. Configure Email (Gmail recommended)
1. Enable 2FA on your Gmail account
2. Generate an App Password (not your regular password)
3. Update email settings in CONFIG

### 4. Test First (Important!)
```bash
# Run component tests
python test_system.py

# Test the main application (keep DRY_RUN = True)
python app.py
```

### 5. Go Live
1. Set `DRY_RUN = False` in CONFIG
2. Run: `python app.py`

## Configuration

See `config/sample_config.py` for detailed configuration examples.

### Required Updates in app.py CONFIG:
```python
CONFIG = {
    'API_KEY': 'your_actual_api_key',
    'ACCESS_TOKEN': 'your_actual_access_token',
    'NIFTY_TOKEN': '256265',  # Get from instruments list
    'BANKNIFTY_TOKEN': '260105',  # Get from instruments list
    'EMAIL_USER': 'your_email@gmail.com',
    'EMAIL_PASS': 'your_app_password',
    'ALERT_TO': 'recipient@gmail.com',
    'DRY_RUN': True  # Set to False when ready
}
```

## How It Works

1. **Market Hours**: Runs continuously until 2:30 PM IST daily
2. **Processing**: Only processes signals on 5-minute boundaries (:05, :10, :15, etc.)
3. **Signals**: Evaluates NIFTY and BANKNIFTY for BUY/SELL setups
4. **Alerts**: Sends email alerts and logs to CSV when conditions are met
5. **Deduplication**: Prevents duplicate alerts for the same candle

## Output Files

- `trading_alerts.log`: Detailed system logs
- `alerts_log.csv`: CSV log of all alerts with required fields

## Important Notes

- System handles IST timezone automatically
- Built-in error handling for API failures
- Memory-efficient with automatic cleanup
- Production-ready with comprehensive logging

## Troubleshooting

1. **Import Errors**: Run `pip install -r requirements.txt`
2. **API Connection**: Verify API key and access token
3. **Email Issues**: Use Gmail App Password, not regular password
4. **Token Errors**: Download latest instruments list from Zerodha
5. **Test First**: Always test with `DRY_RUN = True` before going live

## Disclaimer

This system is for educational/personal use. Always verify signals manually before making trading decisions. The author is not responsible for any financial losses.
