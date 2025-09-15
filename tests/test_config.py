#!/usr/bin/env python3
"""
Test configuration and services
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    
    try:
        from src.config.settings import settings
        
        print(f"✅ Settings loaded successfully")
        print(f"📍 Base directory: {settings.BASE_DIR}")
        print(f"📁 Logs directory: {settings.LOGS_DIR}")
        print(f"📁 Data directory: {settings.DATA_DIR}")
        print(f"🔧 Dry run mode: {settings.DRY_RUN}")
        print(f"🌍 Timezone: {settings.TIMEZONE}")
        
        # Check missing settings
        missing = settings.validate_required_settings()
        if missing:
            print(f"⚠️  Missing settings: {', '.join(missing)}")
            print("💡 Create .env file with your credentials")
        else:
            print("✅ All required settings present")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_services():
    """Test service imports"""
    print("\n📡 Testing Services...")
    
    try:
        from src.services.zerodha_service import zerodha_service
        from src.services.email_service import email_service
        from src.core.trading_engine import trading_engine
        
        print("✅ Zerodha service imported")
        print("✅ Email service imported") 
        print("✅ Trading engine imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Services test failed: {e}")
        return False

def test_indicators():
    """Test technical indicators"""
    print("\n📊 Testing Technical Indicators...")
    
    try:
        from src.core.indicators import TechnicalIndicators
        from src.core.patterns import CandlestickPatterns
        
        # Test pattern detection
        patterns = CandlestickPatterns()
        test_ohlc = {
            'open': 100,
            'high': 102,
            'low': 95,
            'close': 101
        }
        
        pattern = patterns.detect_pattern(test_ohlc)
        print(f"✅ Pattern detection working: {pattern}")
        
        # Test relative strength
        indicators = TechnicalIndicators()
        rs = indicators.compute_relative_strength(18500, 18400)
        print(f"✅ Relative strength calculation: {rs:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Indicators test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 TRADING ALERT SYSTEM - CONFIGURATION TEST")
    print("=" * 60)
    
    tests = [
        test_configuration,
        test_services,
        test_indicators
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    if passed == len(tests):
        print("✅ ALL TESTS PASSED! System is ready for configuration.")
        print("\n📋 Next Steps:")
        print("1. Copy .env.example to .env")
        print("2. Update .env with your Zerodha API credentials")
        print("3. Update .env with your email settings")
        print("4. Run: python main.py")
    else:
        print(f"❌ {len(tests) - passed} test(s) failed. Please check the errors above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    main()
