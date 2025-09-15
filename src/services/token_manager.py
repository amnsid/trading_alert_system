"""
Automated Zerodha Token Management Service
"""
import os
import json
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
import time
from kiteconnect import KiteConnect
from src.config.settings import settings
from src.utils.logger import logger

class TokenManager:
    """Automated token management for Zerodha API"""
    
    def __init__(self):
        self.token_file = Path("token_cache.json")
        self.kite = None
    
    def save_token_data(self, access_token: str, expires_at: str = None):
        """Save token data to cache file"""
        if not expires_at:
            # Token expires at end of trading day (3:30 PM IST)
            from datetime import datetime
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            today = datetime.now(ist)
            expires_at = today.replace(hour=15, minute=30, second=0, microsecond=0)
            if datetime.now(ist) > expires_at:
                # If after 3:30 PM, set expiry for next day
                expires_at += timedelta(days=1)
        
        token_data = {
            'access_token': access_token,
            'expires_at': expires_at.isoformat() if hasattr(expires_at, 'isoformat') else expires_at,
            'api_key': settings.ZERODHA_API_KEY,
            'created_at': datetime.now().isoformat()
        }
        
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        logger.info("✅ Token data saved to cache")
    
    def load_token_data(self) -> dict:
        """Load token data from cache file"""
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading token data: {e}")
            return None
    
    def is_token_valid(self) -> bool:
        """Check if current token is valid"""
        token_data = self.load_token_data()
        if not token_data:
            return False
        
        try:
            # Check expiry
            from datetime import datetime
            expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
            if datetime.now() > expires_at:
                logger.info("Token expired")
                return False
            
            # Test token by making API call
            kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
            kite.set_access_token(token_data['access_token'])
            profile = kite.profile()
            
            logger.info(f"✅ Token valid for user: {profile.get('user_name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    def get_valid_token(self) -> str:
        """Get a valid access token (auto-refresh if needed)"""
        # First check if we have a valid cached token
        if self.is_token_valid():
            token_data = self.load_token_data()
            return token_data['access_token']
        
        logger.info("🔄 Need to refresh token...")
        
        # Try to get new token automatically
        new_token = self.auto_generate_token()
        if new_token:
            return new_token
        
        # If auto-generation fails, prompt user
        return self.manual_token_generation()
    
    def auto_generate_token(self) -> str:
        """Attempt to generate token automatically (if possible)"""
        logger.info("🤖 Attempting automatic token generation...")
        
        # This would require storing user credentials securely
        # For security reasons, we'll skip this and go to manual method
        logger.info("⚠️  Automatic token generation not available for security")
        return None
    
    def manual_token_generation(self) -> str:
        """Generate token with minimal user interaction"""
        logger.info("🔐 Manual token generation required")
        
        try:
            kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
            login_url = kite.login_url()
            
            print("\n" + "="*60)
            print("🔑 ZERODHA TOKEN REQUIRED")
            print("="*60)
            print("🌐 Opening login page in browser...")
            print(f"URL: {login_url}")
            
            # Open browser automatically
            webbrowser.open(login_url)
            
            print("\n📋 QUICK STEPS:")
            print("1. Login in the opened browser")
            print("2. You'll be redirected to a URL with 'request_token'")
            print("3. Copy ONLY the request_token value")
            print("   Example URL: https://example.com?request_token=ABC123&...")
            print("   Copy: ABC123")
            
            # Get token with timeout
            request_token = self.get_user_input_with_timeout(
                "\n🔑 Paste request_token here: ", 
                timeout=300  # 5 minutes timeout
            )
            
            if not request_token:
                logger.error("❌ No token provided or timeout")
                return None
            
            # Generate access token
            data = kite.generate_session(request_token, api_secret="3x6qjya3efj9bpjs68nfita8u9df5n75")
            access_token = data["access_token"]
            
            # Save token
            self.save_token_data(access_token)
            
            print("\n✅ SUCCESS! Token generated and saved.")
            print("🚀 System will now run automatically!")
            
            return access_token
            
        except Exception as e:
            logger.error(f"❌ Token generation failed: {e}")
            return None
    
    def get_user_input_with_timeout(self, prompt: str, timeout: int = 300) -> str:
        """Get user input with timeout"""
        import threading
        import sys
        
        result = [None]
        
        def get_input():
            try:
                result[0] = input(prompt).strip()
            except:
                pass
        
        thread = threading.Thread(target=get_input)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            print(f"\n⏰ Timeout after {timeout} seconds")
            return None
        
        return result[0]
    
    def auto_refresh_token_if_needed(self) -> bool:
        """Check and refresh token if needed (call this periodically)"""
        try:
            if not self.is_token_valid():
                logger.info("🔄 Token needs refresh")
                new_token = self.get_valid_token()
                if new_token:
                    logger.info("✅ Token refreshed successfully")
                    return True
                else:
                    logger.error("❌ Token refresh failed")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error in auto token refresh: {e}")
            return False

# Global token manager instance
token_manager = TokenManager()
