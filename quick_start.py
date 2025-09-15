#!/usr/bin/env python3
"""
Quick Start Script - Automated Setup
===================================
This script handles everything automatically!
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

def setup_environment():
    """Setup environment with minimal user input"""
    
    print("🚀 TRADING ALERT SYSTEM - QUICK START")
    print("=" * 50)
    
    # Check if .env exists
    if not Path('.env').exists():
        print("📝 Creating .env file...")
        
        env_content = f"""# Zerodha KiteConnect API Configuration
ZERODHA_API_KEY=2bys3aum1h2tl54z

# Email Configuration  
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=amnsid31@gmail.com
EMAIL_PASS=bnan jfyh wanv kdry
ALERT_TO=amnkhn31@gmail.com,csarthak.vit@gmail.com

# Instrument Tokens (Standard - will work)
NIFTY_TOKEN=256265
BANKNIFTY_TOKEN=260105
NIFTY200_TOKEN=13297412
BN200_TOKEN=260105

# System Configuration
DRY_RUN=true
LOG_LEVEL=INFO
TIMEZONE=Asia/Kolkata
MARKET_CUTOFF_HOUR=14
MARKET_CUTOFF_MINUTE=30

# Deployment
PORT=8080
HOST=0.0.0.0"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created!")
    
    print("\n🔧 Configuration ready!")
    return True

def run_system():
    """Run the trading system"""
    print("\n🚀 Starting Trading Alert System...")
    print("💡 The system will handle token management automatically!")
    print("📧 First run will require one-time Zerodha login (browser will open)")
    print("\n" + "="*50)
    
    # Import and run
    try:
        from main import TradingAlertSystem
        app = TradingAlertSystem()
        app.run()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    """Main entry point"""
    print("🎯 This script will:")
    print("1. ✅ Setup configuration automatically")  
    print("2. ✅ Handle Zerodha token management")
    print("3. ✅ Start the trading system")
    print("4. ✅ Send emails when signals detected")
    
    print("\n📋 You only need to:")
    print("🔑 Login to Zerodha ONCE when browser opens")
    print("📧 Check emails for trading alerts")
    
    response = input("\n🚀 Ready to start? (Y/n): ").strip().lower()
    if response in ['', 'y', 'yes']:
        setup_environment()
        run_system()
    else:
        print("👋 Setup cancelled. Run again when ready!")

if __name__ == "__main__":
    main()
