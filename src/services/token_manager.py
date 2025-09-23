"""Automated Zerodha Token Management Service"""
import os
import json
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from kiteconnect import KiteConnect

from src.config.settings import settings
from src.utils.logger import logger

class TokenManager:
    """Automated token management for Zerodha API"""
    
    def __init__(self):
        self.token_file = Path("token_cache.json")
        self.kite = None
    
    def save_token_data(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        refresh_expires_at: Optional[datetime] = None,
    ) -> None:
        """Persist the token payload to disk"""

        def _to_iso(value: Optional[datetime]) -> Optional[str]:
            if not value:
                return None
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=timezone.utc)
                return value.isoformat()
            return str(value)

        if not expires_at:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=23)

        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": _to_iso(expires_at),
            "refresh_expires_at": _to_iso(refresh_expires_at),
            "api_key": settings.ZERODHA_API_KEY,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        logger.info("Token data saved to cache")
    
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
            expires_at = self._parse_datetime(token_data.get("expires_at"))
            if not expires_at:
                logger.info("Token expiry not recorded; forcing regeneration")
                return False

            now_utc = datetime.now(timezone.utc)
            if now_utc > expires_at:
                logger.info("Token expired")
                return False

            if expires_at - now_utc <= timedelta(minutes=15):
                logger.info("Token nearing expiry; scheduling refresh")
                return False

            # Test token by making API call
            kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
            kite.set_access_token(token_data['access_token'])
            profile = kite.profile()
            
            logger.info("Token valid for user: %s", profile.get('user_name', 'Unknown'))
            return True
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    def get_valid_token(self) -> str:
        """Get a valid access token (auto-refresh if needed)"""
        # First check if we have a valid cached token
        if self.is_token_valid():
            token_data = self.load_token_data()
            access_token = token_data['access_token']
            os.environ["ZERODHA_ACCESS_TOKEN"] = access_token
            return access_token
        
        logger.info("Attempting to refresh token")
        
        # Try to get new token automatically
        new_token = self.auto_generate_token()
        if new_token:
            return new_token
        
        # If auto-generation fails, prompt user
        return self.manual_token_generation()
    
    def auto_generate_token(self) -> str:
        """Attempt to generate token automatically (if possible)"""
        logger.info("Attempting automatic token refresh using cached credentials")

        token_data = self.load_token_data()
        if not token_data:
            logger.info("No cached token data available for refresh")
            return None

        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            logger.warning("Cached token is missing refresh_token; manual login required")
            return None

        if not settings.ZERODHA_API_SECRET:
            logger.error("ZERODHA_API_SECRET not configured; cannot refresh token automatically")
            return None

        try:
            kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
            data = kite.refresh_access_token(
                refresh_token=refresh_token,
                api_secret=settings.ZERODHA_API_SECRET,
            )

            access_token = data["access_token"]
            new_refresh_token = data.get("refresh_token", refresh_token)
            login_time = self._parse_datetime(data.get("login_time"))
            expires_at = self._derive_expiry(login_time)

            self.save_token_data(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_at=expires_at,
            )

            os.environ["ZERODHA_ACCESS_TOKEN"] = access_token
            logger.info("Access token refreshed successfully")
            return access_token
        except Exception as exc:
            logger.error(f"Automatic token refresh failed: {exc}")
            return None
    
    def manual_token_generation(self) -> str:
        """Generate token with minimal user interaction"""
        logger.info("Manual token generation required")
        
        try:
            kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
            login_url = kite.login_url()
            
            print("\n" + "="*60)
            print("ZERODHA TOKEN REQUIRED")
            print("="*60)
            print("Opening login page in browser...")
            print(f"URL: {login_url}")
            
            # Open browser automatically
            webbrowser.open(login_url)
            
            print("\nQuick steps:")
            print("1. Login in the opened browser")
            print("2. You'll be redirected to a URL with 'request_token'")
            print("3. Copy ONLY the request_token value")
            print("   Example URL: https://example.com?request_token=ABC123&...")
            print("   Copy: ABC123")
            
            # Get token with timeout
            request_token = self.get_user_input_with_timeout(
                "\nPaste request_token here: ",
                timeout=300  # 5 minutes timeout
            )
            
            if not request_token:
                logger.error("No token provided or timeout")
                return None
            
            # Generate access token
            data = kite.generate_session(
                request_token,
                api_secret=settings.ZERODHA_API_SECRET,
            )
            access_token = data["access_token"]
            refresh_token = data.get("refresh_token")
            login_time = self._parse_datetime(data.get("login_time"))
            expires_at = self._derive_expiry(login_time)

            # Save token
            self.save_token_data(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )

            os.environ["ZERODHA_ACCESS_TOKEN"] = access_token

            print("\nToken generated and saved.")
            print("The system will now run automatically.")

            return access_token
            
        except Exception as e:
            logger.error("Token generation failed: %s", e)
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
            print(f"\nTimeout after {timeout} seconds")
            return None
        
        return result[0]

    def _parse_datetime(self, value) -> Optional[datetime]:
        """Convert various datetime formats to aware UTC datetime"""
        if not value:
            return None

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)

        try:
            value = str(value)
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            logger.warning(f"Unable to parse datetime value: {value}")
            return None

    def _derive_expiry(self, login_time: Optional[datetime]) -> datetime:
        """Best-effort calculation of access-token expiry"""
        if login_time:
            return login_time + timedelta(hours=23, minutes=45)
        return datetime.now(timezone.utc) + timedelta(hours=23)
    
    def auto_refresh_token_if_needed(self) -> bool:
        """Check and refresh token if needed (call this periodically)"""
        try:
            if not self.is_token_valid():
                logger.info("Token needs refresh")
                new_token = self.get_valid_token()
                if new_token:
                    logger.info("Token refreshed successfully")
                    return True
                else:
                    logger.error("Token refresh failed")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error in auto token refresh: {e}")
            return False

# Global token manager instance
token_manager = TokenManager()
