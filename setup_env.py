#!/usr/bin/env python3
"""
Quick setup script to create .env file with your credentials
"""

def create_env_file():
    """Create .env file with user credentials"""
    
    print("🔧 Setting up .env file with your credentials...")
    
    env_content = """# Zerodha KiteConnect API Configuration
ZERODHA_API_KEY=2bys3aum1h2tl54z
ZERODHA_ACCESS_TOKEN=PASTE_YOUR_ACCESS_TOKEN_HERE

# Instrument Tokens (Standard tokens - will work for most cases)
NIFTY_TOKEN=256265
BANKNIFTY_TOKEN=260105
NIFTY200_TOKEN=13297412
BN200_TOKEN=260105

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=amnsid31@gmail.com
EMAIL_PASS=bnan jfyh wanv kdry
ALERT_TO=amnkhn31@gmail.com,csarthak.vit@gmail.com

# System Configuration
DRY_RUN=true
LOG_LEVEL=INFO
TIMEZONE=Asia/Kolkata
MARKET_CUTOFF_HOUR=14
MARKET_CUTOFF_MINUTE=30

# Deployment Configuration
PORT=8080
HOST=0.0.0.0"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print("\n📋 NEXT STEPS:")
    print("1. Get your Zerodha access token:")
    print("   - Run: python get_access_token.py")
    print("   - Follow the instructions to get token")
    print("   - Update ZERODHA_ACCESS_TOKEN in .env file")
    print("\n2. Test the system:")
    print("   - Run: python main.py")
    
    return True

if __name__ == "__main__":
    create_env_file()
