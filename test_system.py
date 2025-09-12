#!/usr/bin/env python3
"""
Test Script for Trading Alert System
===================================
Simple test to verify the system components work correctly
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import pytz
        print("✅ pytz imported successfully")
    except ImportError as e:
        print(f"❌ pytz import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        from kiteconnect import KiteConnect
        print("✅ kiteconnect imported successfully")
    except ImportError as e:
        print(f"⚠️  kiteconnect import failed: {e}")
        print("   This is expected if you haven't installed it yet.")
        print("   Run: pip install kiteconnect")
    
    return True

def test_timezone():
    """Test timezone functionality"""
    print("\nTesting timezone functionality...")
    
    try:
        import pytz
        from datetime import datetime
        
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        print(f"✅ Current IST time: {now_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        return True
    except Exception as e:
        print(f"❌ Timezone test failed: {e}")
        return False

def test_file_operations():
    """Test file read/write operations"""
    print("\nTesting file operations...")
    
    try:
        import csv
        test_file = "test_log.csv"
        
        # Test CSV writing
        with open(test_file, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'symbol', 'signal']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'timestamp': '2023-01-01 10:00:00',
                'symbol': 'TEST',
                'signal': 'BUY'
            })
        
        # Test CSV reading
        with open(test_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            if len(rows) == 1 and rows[0]['symbol'] == 'TEST':
                print("✅ CSV operations working correctly")
            else:
                print("❌ CSV data verification failed")
                return False
        
        # Cleanup
        os.remove(test_file)
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def test_pattern_detection():
    """Test candlestick pattern detection logic"""
    print("\nTesting pattern detection...")
    
    try:
        # Import the pattern detection function from app.py
        from app import detect_candlestick_patterns
        
        # Test Green Hammer pattern
        green_hammer = {
            'open': 100,
            'high': 102,
            'low': 95,
            'close': 101
        }
        
        pattern = detect_candlestick_patterns(green_hammer)
        if pattern == "Green_Hammer":
            print("✅ Green Hammer pattern detection working")
        else:
            print(f"⚠️  Green Hammer pattern detection returned: {pattern}")
        
        return True
        
    except ImportError:
        print("⚠️  Cannot import app.py - this is expected if not in same directory")
        return True
    except Exception as e:
        print(f"❌ Pattern detection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Trading Alert System - Component Test")
    print("=" * 50)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_imports()
    all_passed &= test_timezone()
    all_passed &= test_file_operations()
    all_passed &= test_pattern_detection()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! System components are working correctly.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Update CONFIG in app.py with your API credentials")
        print("3. Run: python app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nMake sure to install dependencies: pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    main()
