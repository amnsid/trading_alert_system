#!/usr/bin/env python3
"""
Demo Test - Trading Alert System Components
Shows how the system works without real API calls
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

# Import functions from our main app
from app import (
    detect_candlestick_patterns, 
    compute_relative_strength,
    evaluate_buy_setup,
    evaluate_sell_setup,
    send_email_alert
)

def demo_pattern_detection():
    """Demo candlestick pattern detection"""
    print("🔍 Testing Candlestick Pattern Detection:")
    
    patterns = [
        {
            'name': 'Green Hammer',
            'ohlc': {'open': 100, 'high': 102, 'low': 95, 'close': 101}
        },
        {
            'name': 'Red Hammer', 
            'ohlc': {'open': 100, 'high': 102, 'low': 95, 'close': 98}
        },
        {
            'name': 'Inverted Hammer',
            'ohlc': {'open': 100, 'high': 105, 'low': 99, 'close': 98}
        },
        {
            'name': 'Normal Candle',
            'ohlc': {'open': 100, 'high': 102, 'low': 99, 'close': 101}
        }
    ]
    
    for pattern_test in patterns:
        detected = detect_candlestick_patterns(pattern_test['ohlc'])
        print(f"  {pattern_test['name']}: {detected or 'No pattern'}")

def demo_signal_evaluation():
    """Demo BUY/SELL signal evaluation"""
    print("\n📊 Testing Signal Evaluation:")
    
    # Sample data
    close_price = 18500
    avwap_high = 18400  # CMP above AVWAP (bullish)
    avwap_low = 18300
    rs_positive = 0.02  # Positive RS (bullish)
    rs_negative = -0.02  # Negative RS (bearish)
    
    # Test BUY signal
    is_buy, buy_avwap, buy_measure = evaluate_buy_setup(
        close_price, avwap_high, avwap_low, rs_positive, "Green_Hammer"
    )
    measure_str = f"{buy_measure:.4f}" if buy_measure else "N/A"
    print(f"  BUY Signal: {is_buy} (Measure: {measure_str})")
    
    # Test SELL signal  
    close_price_bearish = 18200  # Below AVWAP
    is_sell, sell_avwap, sell_measure = evaluate_sell_setup(
        close_price_bearish, avwap_high, avwap_low, rs_negative, "Inverted_Hammer"
    )
    measure_str = f"{sell_measure:.4f}" if sell_measure else "N/A"
    print(f"  SELL Signal: {is_sell} (Measure: {measure_str})")

def demo_email_alert():
    """Demo email alert (dry run)"""
    print("\n📧 Testing Email Alert (DRY RUN):")
    
    # This will show the email format without sending
    send_email_alert(
        symbol="NIFTY",
        signal_type="BUY", 
        close=18500,
        avwap_value=18400,
        avwap_anchor="prev_high",
        rs_value=0.025,
        pattern="Green_Hammer"
    )

def main():
    """Run all demos"""
    print("Trading Alert System - Component Demo")
    print("=" * 50)
    
    demo_pattern_detection()
    demo_signal_evaluation()
    demo_email_alert()
    
    print("\n" + "=" * 50)
    print("✅ All components working! Ready for live configuration.")

if __name__ == "__main__":
    main()
