#!/usr/bin/env python3
"""
Auto-Start Trading System
========================
Minimizes manual intervention to absolute minimum
"""
import os
import sys
from pathlib import Path

# Set environment for Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.append(str(Path(__file__).parent))

def check_token_status():
    """Check if we have a valid token"""
    try:
        from src.services.token_manager import token_manager
        return token_manager.is_token_valid()
    except:
        return False

def main():
    """Main entry point with smart automation"""
    
    print("🚀 TRADING ALERT SYSTEM - AUTO START")
    print("=" * 50)
    
    # Check token status
    has_valid_token = check_token_status()
    
    if has_valid_token:
        print("✅ Valid token found - Starting automatically!")
        print("📊 System will monitor markets until 2:30 PM IST")
        print("📧 Email alerts will be sent when signals detected")
        print("\n🤖 RUNNING IN FULL AUTO MODE...")
        print("Press Ctrl+C to stop")
        
        # Start system immediately
        try:
            from main import TradingAlertSystem
            app = TradingAlertSystem()
            app.run()
        except KeyboardInterrupt:
            print("\n🛑 System stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    else:
        print("🔑 First-time setup required")
        print("📝 Need to get Zerodha token (ONE TIME ONLY)")
        print("\n💡 After this, system runs 100% automatically!")
        
        response = input("\n🚀 Continue with setup? (Y/n): ").strip().lower()
        if response in ['', 'y', 'yes']:
            try:
                from main import TradingAlertSystem
                app = TradingAlertSystem()
                app.run()
                
                print("\n🎉 SETUP COMPLETE!")
                print("🤖 From now on, just run: python auto_start.py")
                print("📧 System will work automatically!")
                
            except KeyboardInterrupt:
                print("\n🛑 Setup cancelled")
            except Exception as e:
                print(f"\n❌ Setup failed: {e}")
        else:
            print("👋 Setup cancelled. Run again when ready!")

if __name__ == "__main__":
    main()
