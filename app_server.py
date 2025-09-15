#!/usr/bin/env python3
"""
Dual-mode application: Web setup + Trading system
"""
import os
import sys
import threading
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

def run_web_server():
    """Run Flask web server for token setup"""
    from src.web.app import app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)

def run_trading_system():
    """Run trading alert system"""
    # Wait a bit for web server to start
    time.sleep(5)
    
    while True:
        try:
            # Check if token is available
            from src.services.token_manager import token_manager
            if token_manager.is_token_valid():
                print("✅ Valid token found - Starting trading system...")
                
                # Start trading system
                from main import TradingAlertSystem
                app = TradingAlertSystem()
                app.run()
                break
            else:
                print("⏳ Waiting for token setup via web interface...")
                time.sleep(60)  # Check every minute
                
        except Exception as e:
            print(f"❌ Error in trading system: {e}")
            time.sleep(60)

def main():
    """Main entry point - runs both web server and trading system"""
    print("🚀 TRADING ALERT SYSTEM - CLOUD DEPLOYMENT")
    print("=" * 50)
    print("🌐 Web Interface: Starting...")
    print("📊 Trading System: Will start after token setup")
    
    # Start web server in background thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Start trading system in main thread
    run_trading_system()

if __name__ == "__main__":
    main()
