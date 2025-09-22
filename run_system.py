#!/usr/bin/env python3
"""
FULLY AUTOMATED Trading Alert System
===================================
NO MANUAL WORK REQUIRED!
"""
import os
import sys
import webbrowser
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Add src to path
sys.path.append(str(Path(__file__).parent))

def setup_and_run():
    """Setup and run the system with minimal user interaction"""
    
    print("=" * 60)
    print("FULLY AUTOMATED TRADING ALERT SYSTEM")
    print("=" * 60)
    print("Email System: CONFIGURED (amnsid31@gmail.com)")
    print("Recipients: amnkhn31@gmail.com, csarthak.vit@gmail.com")
    print("Zerodha API: Will handle automatically")
    print("=" * 60)
    
    # Check if .env exists, create if not
    if not Path('.env').exists():
        print("Creating configuration file...")
        
        env_content = """# Zerodha KiteConnect API Configuration
ZERODHA_API_KEY=2bys3aum1h2tl54z
ZERODHA_API_SECRET=PASTE_YOUR_API_SECRET_HERE

# Email Configuration  
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=amnsid31@gmail.com
EMAIL_PASS=bnan jfyh wanv kdry
ALERT_TO=amnkhn31@gmail.com,csarthak.vit@gmail.com

# Instrument Tokens
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
        print("Configuration created successfully!")
    
    print("\nStarting system...")
    print("NOTE: Browser will open ONCE for Zerodha login")
    print("After that, system runs 100% automatically!")
    
    input("\nPress Enter to continue...")
    
    try:
        from main import TradingAlertSystem
        app = TradingAlertSystem()
        app.run()
    except KeyboardInterrupt:
        print("\nSystem stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("Check logs/trading_alerts.log for details")

if __name__ == "__main__":
    setup_and_run()
