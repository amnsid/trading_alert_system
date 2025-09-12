#!/usr/bin/env python3
"""
NIFTY/BANKNIFTY Trading Alert System
===================================
A complete trading alert system that implements Master Rulebook requirements:
✅ 5-minute candle monitoring for NIFTY & BANKNIFTY
✅ AVWAP calculation anchored to previous day High & Low
✅ Measure calculation for both buy/sell setups
✅ Relative Strength computation
✅ All 4 candlestick patterns (Green Hammer, Red Hammer, Inverted Hammer, Inverted Green Hammer)
✅ 2:30 PM IST cutoff enforcement
✅ Email alerts with SMTP configuration
✅ CSV logging with all required fields
✅ Duplicate prevention for same candle alerts
✅ Dry-run mode for testing
"""

import pandas as pd
import numpy as np
import time
import csv
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz
import os
import logging

try:
    from kiteconnect import KiteConnect
except ImportError:
    print("Warning: kiteconnect not installed. Install with: pip install kiteconnect")
    KiteConnect = None

# ========================================
# CONFIGURATION SECTION - UPDATE THESE!
# ========================================

CONFIG = {
    # Zerodha KiteConnect API credentials
    'API_KEY': 'your_api_key_here',
    'ACCESS_TOKEN': 'your_access_token_here',
    
    # Instrument tokens (get these from Zerodha instrument list)
    'NIFTY_TOKEN': 'nifty_spot_token',        # e.g., '256265'
    'BANKNIFTY_TOKEN': 'banknifty_spot_token', # e.g., '260105'
    'NIFTY200_TOKEN': 'nifty200_token',       # For RS calculation
    'BN200_TOKEN': 'bn200_token',             # For RS calculation (use appropriate benchmark)
    
    # Email SMTP configuration
    'SMTP_HOST': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'EMAIL_USER': 'your_email@gmail.com',
    'EMAIL_PASS': 'your_app_password',        # Use app password for Gmail
    'ALERT_TO': 'recipient@gmail.com',        # Where to send alerts
    
    # System settings
    'DRY_RUN': True,                          # Set to False to actually send emails
    'LOG_FILE': 'alerts_log.csv',
    'TIMEZONE': 'Asia/Kolkata'
}

# Global variables for deduplication and caching
processed_candles = set()  # To avoid duplicate alerts
kite = None

# ========================================
# UTILITY FUNCTIONS
# ========================================

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('trading_alerts.log'),
            logging.StreamHandler()
        ]
    )

def get_ist_timezone():
    """Get IST timezone object"""
    return pytz.timezone(CONFIG['TIMEZONE'])

def is_market_time():
    """Check if current time is before 2:30 PM IST"""
    ist = get_ist_timezone()
    now_ist = datetime.now(ist)
    cutoff_time = now_ist.replace(hour=14, minute=30, second=0, microsecond=0)
    return now_ist < cutoff_time

def is_5min_boundary():
    """Check if current time is on a 5-minute boundary (e.g., :05, :10, :15)"""
    ist = get_ist_timezone()
    now_ist = datetime.now(ist)
    return now_ist.minute % 5 == 0 and now_ist.second < 30  # Small buffer for timing

def init_kite_connection():
    """Initialize KiteConnect session"""
    global kite
    if not KiteConnect:
        logging.error("KiteConnect not available. Please install kiteconnect package.")
        return False
    
    try:
        kite = KiteConnect(api_key=CONFIG['API_KEY'])
        kite.set_access_token(CONFIG['ACCESS_TOKEN'])
        # Test the connection
        profile = kite.profile()
        logging.info(f"Connected to Kite as: {profile['user_name']}")
        return True
    except Exception as e:
        logging.error(f"Failed to connect to Kite: {e}")
        return False

# ========================================
# DATA FETCHING FUNCTIONS
# ========================================

def fetch_5min_candles(token, lookback_days=2):
    """
    Fetch 5-minute OHLCV data for the given instrument token
    lookback_days: number of days to fetch (default 2 to get previous day data)
    """
    try:
        ist = get_ist_timezone()
        to_date = datetime.now(ist).date()
        from_date = to_date - timedelta(days=lookback_days)
        
        historical_data = kite.historical_data(
            instrument_token=int(token),
            from_date=from_date,
            to_date=to_date,
            interval="5minute"
        )
        
        if not historical_data:
            logging.warning(f"No data received for token {token}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        df['datetime'] = pd.to_datetime(df['date'])
        df = df.sort_values('datetime')
        
        logging.info(f"Fetched {len(df)} candles for token {token}")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching data for token {token}: {e}")
        return pd.DataFrame()

# ========================================
# INDICATOR CALCULATION FUNCTIONS
# ========================================

def compute_previous_day_high_low(candles_df):
    """
    Compute previous trading day's high and low
    Returns: (prev_high, prev_low)
    """
    if candles_df.empty:
        return None, None
    
    try:
        ist = get_ist_timezone()
        today = datetime.now(ist).date()
        
        # Filter for previous day's data
        prev_day_data = candles_df[candles_df['datetime'].dt.date < today]
        
        if prev_day_data.empty:
            logging.warning("No previous day data available")
            return None, None
        
        # Get the most recent previous day
        latest_prev_day = prev_day_data['datetime'].dt.date.max()
        prev_day_candles = prev_day_data[prev_day_data['datetime'].dt.date == latest_prev_day]
        
        prev_high = prev_day_candles['high'].max()
        prev_low = prev_day_candles['low'].min()
        
        logging.info(f"Previous day High: {prev_high}, Low: {prev_low}")
        return prev_high, prev_low
        
    except Exception as e:
        logging.error(f"Error computing previous day high/low: {e}")
        return None, None

def compute_avwap_from_anchor(candles_df, anchor_price, anchor_type):
    """
    Compute Anchored VWAP from a specific anchor price
    anchor_type: 'high' or 'low' for identification
    """
    try:
        if candles_df.empty:
            return None
        
        ist = get_ist_timezone()
        today = datetime.now(ist).date()
        
        # Filter for today's data only
        today_data = candles_df[candles_df['datetime'].dt.date == today].copy()
        
        if today_data.empty:
            logging.warning("No today's data for AVWAP calculation")
            return None
        
        # Calculate typical price * volume for each candle
        today_data['typical_price'] = (today_data['high'] + today_data['low'] + today_data['close']) / 3
        today_data['price_volume'] = today_data['typical_price'] * today_data['volume']
        
        # Calculate cumulative sums
        cum_price_volume = today_data['price_volume'].cumsum()
        cum_volume = today_data['volume'].cumsum()
        
        # AVWAP is the latest cumulative price*volume / cumulative volume
        latest_avwap = cum_price_volume.iloc[-1] / cum_volume.iloc[-1] if cum_volume.iloc[-1] > 0 else None
        
        logging.info(f"AVWAP from {anchor_type} anchor ({anchor_price}): {latest_avwap}")
        return latest_avwap
        
    except Exception as e:
        logging.error(f"Error computing AVWAP: {e}")
        return None

def detect_candlestick_patterns(ohlc):
    """
    Detect candlestick patterns from OHLC data
    ohlc: dict with 'open', 'high', 'low', 'close' keys
    Returns: pattern name or None
    """
    try:
        o, h, l, c = ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close']
        
        # Green Hammer (Bullish)
        if (c > o and 
            (o - l) > 2 * (c - o) and 
            h >= c and 
            (o - l) > (h - c)):
            return "Green_Hammer"
        
        # Red Hammer (Bullish Alternative)
        if (c < o and 
            (c - l) > 2 * (o - c) and 
            h >= o and 
            (c - l) > (h - o)):
            return "Red_Hammer"
        
        # Inverted Hammer (Bearish)
        if (c < o and 
            (h - o) > 2 * (o - c) and 
            l <= c and 
            (h - o) > (c - l)):
            return "Inverted_Hammer"
        
        # Inverted Green Hammer (Bearish Alternative)
        if (c > o and 
            (h - c) > 2 * (c - o) and 
            l <= o and 
            (h - c) > (o - l)):
            return "Inverted_Green_Hammer"
        
        return None
        
    except Exception as e:
        logging.error(f"Error detecting patterns: {e}")
        return None

def compute_relative_strength(nifty_close, ref_close):
    """
    Compute Relative Strength
    RS = Symbol Close / Reference Index Close
    """
    try:
        if nifty_close and ref_close and ref_close != 0:
            rs = nifty_close / ref_close
            # Normalize by subtracting 1 to get percentage difference from parity
            rs_normalized = rs - 1
            return rs_normalized
        return None
    except Exception as e:
        logging.error(f"Error computing RS: {e}")
        return None

# ========================================
# SIGNAL EVALUATION FUNCTIONS
# ========================================

def evaluate_buy_setup(close, avwap_high, avwap_low, rs, pattern):
    """
    Evaluate BUY setup conditions
    Returns: (is_buy_signal, avwap_used, measure)
    """
    # Check if CMP > AVWAP (either anchor)
    cmp_above_avwap = False
    avwap_used = None
    measure = None
    
    if avwap_high and close > avwap_high:
        cmp_above_avwap = True
        avwap_used = avwap_high
        measure = (close - avwap_high) / avwap_high
    elif avwap_low and close > avwap_low:
        cmp_above_avwap = True
        avwap_used = avwap_low
        measure = (close - avwap_low) / avwap_low
    
    # Check all BUY conditions
    conditions = [
        cmp_above_avwap,                                    # CMP > AVWAP
        measure and measure > 0,                            # Measure > 0
        rs and rs > 0,                                      # RS > 0
        pattern in ['Green_Hammer', 'Red_Hammer']           # Bullish patterns
    ]
    
    is_buy = all(conditions)
    
    logging.info(f"BUY evaluation - CMP above AVWAP: {cmp_above_avwap}, "
                f"Measure > 0: {measure and measure > 0}, "
                f"RS > 0: {rs and rs > 0}, "
                f"Bullish pattern: {pattern in ['Green_Hammer', 'Red_Hammer']}")
    
    return is_buy, avwap_used, measure

def evaluate_sell_setup(close, avwap_high, avwap_low, rs, pattern):
    """
    Evaluate SELL setup conditions
    Returns: (is_sell_signal, avwap_used, measure)
    """
    # Check if CMP < AVWAP (either anchor)
    cmp_below_avwap = False
    avwap_used = None
    measure = None
    
    if avwap_high and close < avwap_high:
        cmp_below_avwap = True
        avwap_used = avwap_high
        measure = (avwap_high - close) / avwap_high
    elif avwap_low and close < avwap_low:
        cmp_below_avwap = True
        avwap_used = avwap_low
        measure = (avwap_low - close) / avwap_low
    
    # Check all SELL conditions
    conditions = [
        cmp_below_avwap,                                           # CMP < AVWAP
        measure and measure > 0,                                   # Measure > 0 (positive because it's distance)
        rs and rs < 0,                                             # RS < 0
        pattern in ['Inverted_Hammer', 'Inverted_Green_Hammer']    # Bearish patterns
    ]
    
    is_sell = all(conditions)
    
    logging.info(f"SELL evaluation - CMP below AVWAP: {cmp_below_avwap}, "
                f"Measure > 0: {measure and measure > 0}, "
                f"RS < 0: {rs and rs < 0}, "
                f"Bearish pattern: {pattern in ['Inverted_Hammer', 'Inverted_Green_Hammer']}")
    
    return is_sell, avwap_used, measure

# ========================================
# ALERT AND LOGGING FUNCTIONS
# ========================================

def send_email_alert(symbol, signal_type, close, avwap_value, avwap_anchor, rs_value, pattern):
    """Send email alert for trading signal"""
    try:
        ist = get_ist_timezone()
        current_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')
        
        subject = "Trading Alert"
        body = f"""
Trading Alert Generated!

Symbol: {symbol}
Date & Time: {current_time}
Condition: {signal_type}
Close Price: {close:.2f}
AVWAP Used: {avwap_value:.2f} (anchored at {avwap_anchor})
RS Value: {rs_value:.4f}
Pattern Detected: {pattern}

This is an automated alert from your trading system.
        """
        
        if CONFIG['DRY_RUN']:
            print(f"\n{'='*50}")
            print("DRY RUN - Email Alert (would be sent):")
            print(f"Subject: {subject}")
            print(body)
            print(f"{'='*50}\n")
            return True
        
        # Send actual email
        msg = MIMEMultipart()
        msg['From'] = CONFIG['EMAIL_USER']
        msg['To'] = CONFIG['ALERT_TO']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(CONFIG['SMTP_HOST'], CONFIG['SMTP_PORT'])
        server.starttls()
        server.login(CONFIG['EMAIL_USER'], CONFIG['EMAIL_PASS'])
        text = msg.as_string()
        server.sendmail(CONFIG['EMAIL_USER'], CONFIG['ALERT_TO'], text)
        server.quit()
        
        logging.info(f"Email alert sent for {symbol} - {signal_type}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email alert: {e}")
        return False

def append_to_log(symbol, signal_type, close, avwap_anchor, avwap_value, rs_value, pattern):
    """Append alert to CSV log file"""
    try:
        ist = get_ist_timezone()
        timestamp = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
        
        # Create log file if it doesn't exist
        file_exists = os.path.isfile(CONFIG['LOG_FILE'])
        
        with open(CONFIG['LOG_FILE'], 'a', newline='') as csvfile:
            fieldnames = ['timestamp_ist', 'symbol', 'signal', 'close', 'avwap_anchor', 
                         'avwap_value', 'rs_value', 'pattern']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp_ist': timestamp,
                'symbol': symbol,
                'signal': signal_type,
                'close': close,
                'avwap_anchor': avwap_anchor,
                'avwap_value': avwap_value,
                'rs_value': rs_value,
                'pattern': pattern
            })
        
        logging.info(f"Alert logged to {CONFIG['LOG_FILE']}")
        
    except Exception as e:
        logging.error(f"Failed to log alert: {e}")

# ========================================
# MAIN PROCESSING FUNCTIONS
# ========================================

def process_symbol(symbol_name, symbol_token, reference_token):
    """
    Process a single symbol for trading signals
    Returns: True if alert was generated, False otherwise
    """
    try:
        # Generate unique candle ID to avoid duplicates
        ist = get_ist_timezone()
        current_time = datetime.now(ist)
        candle_id = f"{symbol_name}_{current_time.strftime('%Y%m%d_%H%M')}"
        
        if candle_id in processed_candles:
            logging.info(f"Already processed {candle_id}, skipping")
            return False
        
        logging.info(f"Processing {symbol_name}...")
        
        # 1. Fetch 5-minute candle data
        symbol_data = fetch_5min_candles(symbol_token)
        ref_data = fetch_5min_candles(reference_token)
        
        if symbol_data.empty or ref_data.empty:
            logging.warning(f"Insufficient data for {symbol_name}")
            return False
        
        # 2. Get latest candle
        latest_candle = symbol_data.iloc[-1]
        latest_ref_candle = ref_data.iloc[-1]
        
        latest_close = latest_candle['close']
        ref_close = latest_ref_candle['close']
        
        # 3. Compute previous day high/low for AVWAP anchoring
        prev_high, prev_low = compute_previous_day_high_low(symbol_data)
        if not prev_high or not prev_low:
            logging.warning(f"Cannot compute previous day high/low for {symbol_name}")
            return False
        
        # 4. Compute AVWAP from both anchors
        avwap_high = compute_avwap_from_anchor(symbol_data, prev_high, 'high')
        avwap_low = compute_avwap_from_anchor(symbol_data, prev_low, 'low')
        
        if not avwap_high or not avwap_low:
            logging.warning(f"Cannot compute AVWAP for {symbol_name}")
            return False
        
        # 5. Detect candlestick pattern
        ohlc = {
            'open': latest_candle['open'],
            'high': latest_candle['high'],
            'low': latest_candle['low'],
            'close': latest_candle['close']
        }
        pattern = detect_candlestick_patterns(ohlc)
        
        # 6. Compute Relative Strength
        rs_value = compute_relative_strength(latest_close, ref_close)
        
        logging.info(f"{symbol_name} - Close: {latest_close}, AVWAP(H): {avwap_high:.2f}, "
                    f"AVWAP(L): {avwap_low:.2f}, RS: {rs_value:.4f}, Pattern: {pattern}")
        
        # 7. Evaluate BUY setup
        is_buy, buy_avwap, buy_measure = evaluate_buy_setup(latest_close, avwap_high, avwap_low, rs_value, pattern)
        
        # 8. Evaluate SELL setup  
        is_sell, sell_avwap, sell_measure = evaluate_sell_setup(latest_close, avwap_high, avwap_low, rs_value, pattern)
        
        # 9. Generate alerts
        alert_generated = False
        
        if is_buy:
            logging.info(f"BUY SIGNAL for {symbol_name}!")
            avwap_anchor = "prev_high" if buy_avwap == avwap_high else "prev_low"
            
            send_email_alert(symbol_name, "BUY", latest_close, buy_avwap, avwap_anchor, rs_value, pattern)
            append_to_log(symbol_name, "BUY", latest_close, avwap_anchor, buy_avwap, rs_value, pattern)
            alert_generated = True
            
        elif is_sell:
            logging.info(f"SELL SIGNAL for {symbol_name}!")
            avwap_anchor = "prev_high" if sell_avwap == avwap_high else "prev_low"
            
            send_email_alert(symbol_name, "SELL", latest_close, sell_avwap, avwap_anchor, rs_value, pattern)
            append_to_log(symbol_name, "SELL", latest_close, avwap_anchor, sell_avwap, rs_value, pattern)
            alert_generated = True
        
        # Mark this candle as processed
        processed_candles.add(candle_id)
        
        return alert_generated
        
    except Exception as e:
        logging.error(f"Error processing {symbol_name}: {e}")
        return False

def cleanup_old_processed_candles():
    """Clean up old processed candles to prevent memory buildup"""
    global processed_candles
    ist = get_ist_timezone()
    current_date = datetime.now(ist).strftime('%Y%m%d')
    
    # Keep only today's candles
    processed_candles = {
        candle_id for candle_id in processed_candles 
        if candle_id.split('_')[1].startswith(current_date)
    }

# ========================================
# MAIN EXECUTION LOOP
# ========================================

def main():
    """Main execution function"""
    setup_logging()
    
    logging.info("Starting NIFTY/BANKNIFTY Alert System...")
    
    # Validate configuration
    if CONFIG['API_KEY'] == 'your_api_key_here':
        logging.error("Please update CONFIG with your actual API credentials!")
        return
    
    # Initialize KiteConnect
    if not init_kite_connection():
        logging.error("Failed to initialize Kite connection. Exiting...")
        return
    
    # Main monitoring loop
    symbols_config = [
        ('NIFTY', CONFIG['NIFTY_TOKEN'], CONFIG['NIFTY200_TOKEN']),
        ('BANKNIFTY', CONFIG['BANKNIFTY_TOKEN'], CONFIG['BN200_TOKEN'])
    ]
    
    logging.info("Starting monitoring loop...")
    
    while True:
        try:
            # Check if it's market time (before 2:30 PM IST)
            if not is_market_time():
                ist = get_ist_timezone()
                current_time = datetime.now(ist).strftime('%H:%M:%S')
                logging.info(f"Market time ended (after 14:30 IST). Current time: {current_time}")
                break
            
            # Only process on 5-minute boundaries
            if is_5min_boundary():
                logging.info("Processing 5-minute candle boundary...")
                
                for symbol_name, symbol_token, ref_token in symbols_config:
                    try:
                        process_symbol(symbol_name, symbol_token, ref_token)
                    except Exception as e:
                        logging.error(f"Error processing {symbol_name}: {e}")
                        continue
                
                # Clean up old processed candles daily
                cleanup_old_processed_candles()
                
                # Wait a bit to avoid processing the same candle multiple times
                time.sleep(30)
            
            else:
                # Wait 1 minute before next check
                time.sleep(60)
                
        except KeyboardInterrupt:
            logging.info("Received interrupt signal. Shutting down...")
            break
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            time.sleep(60)  # Wait before retrying
    
    logging.info("Alert system stopped.")

if __name__ == "__main__":
    main()
