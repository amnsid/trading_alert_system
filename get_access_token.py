#!/usr/bin/env python3
"""
Zerodha Access Token Generator
=============================
This script helps you get the access token for Zerodha KiteConnect API
"""
import webbrowser
from kiteconnect import KiteConnect

# Your API credentials
API_KEY = "2bys3aum1h2tl54z"
API_SECRET = "3x6qjya3efj9bpjs68nfita8u9df5n75"

def get_access_token():
    """Generate access token for Zerodha API"""
    
    print("=" * 60)
    print("🔑 ZERODHA ACCESS TOKEN GENERATOR")
    print("=" * 60)
    
    # Initialize KiteConnect
    kite = KiteConnect(api_key=API_KEY)
    
    # Generate login URL
    login_url = kite.login_url()
    print(f"🌐 Opening login URL in browser...")
    print(f"URL: {login_url}")
    
    # Open in browser
    webbrowser.open(login_url)
    
    print("\n📋 STEPS:")
    print("1. Login to your Zerodha account in the opened browser")
    print("2. After login, you'll be redirected to a URL")
    print("3. Copy the 'request_token' from the URL")
    print("   Example: https://example.com?request_token=ABC123&action=login&status=success")
    print("   Copy: ABC123")
    
    # Get request token from user
    request_token = input("\n🔑 Enter the request_token from URL: ").strip()
    
    if not request_token:
        print("❌ No request token provided!")
        return None
    
    try:
        # Generate access token
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]
        
        print("\n✅ SUCCESS!")
        print("=" * 60)
        print(f"🔑 Your Access Token: {access_token}")
        print("=" * 60)
        
        # Save to file for easy copying
        with open("access_token.txt", "w") as f:
            f.write(f"ACCESS_TOKEN={access_token}\n")
            f.write(f"API_KEY={API_KEY}\n")
            f.write(f"API_SECRET={API_SECRET}\n")
        
        print(f"💾 Access token saved to: access_token.txt")
        print("\n📋 Next Steps:")
        print("1. Copy this access token")
        print("2. Update ZERODHA_ACCESS_TOKEN in .env file")
        print("3. Run: python main.py")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return None

if __name__ == "__main__":
    get_access_token()
