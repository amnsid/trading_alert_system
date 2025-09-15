"""
Zerodha KiteConnect API service
"""
from typing import Optional, Dict, List
import pandas as pd
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from src.config.settings import settings
from src.utils.logger import logger

class ZerodhaService:
    """Service class for Zerodha KiteConnect API operations"""
    
    def __init__(self):
        self.kite: Optional[KiteConnect] = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Initialize and test KiteConnect connection with auto token management
        Returns: True if connection successful, False otherwise
        """
        try:
            if not settings.ZERODHA_API_KEY:
                logger.error("Zerodha API key not provided")
                return False
            
            # Import token manager here to avoid circular imports
            from src.services.token_manager import token_manager
            
            # Get valid token (auto-refresh if needed)
            access_token = token_manager.get_valid_token()
            if not access_token:
                logger.error("Could not obtain valid access token")
                return False
            
            self.kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
            self.kite.set_access_token(access_token)
            
            # Test connection
            profile = self.kite.profile()
            logger.info(f"Connected to Zerodha as: {profile.get('user_name', 'Unknown')}")
            self._connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Zerodha: {e}")
            self._connected = False
            return False
    
    def is_connected(self) -> bool:
        """Check if service is connected to Zerodha"""
        return self._connected and self.kite is not None
    
    def fetch_historical_data(
        self, 
        instrument_token: str, 
        lookback_days: int = 2,
        interval: str = "5minute"
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for given instrument
        
        Args:
            instrument_token: Zerodha instrument token
            lookback_days: Number of days to fetch (default 2)
            interval: Data interval (default 5minute)
            
        Returns:
            DataFrame with OHLCV data
        """
        if not self.is_connected():
            logger.error("Not connected to Zerodha")
            return pd.DataFrame()
        
        try:
            from_date = datetime.now().date() - timedelta(days=lookback_days)
            to_date = datetime.now().date()
            
            historical_data = self.kite.historical_data(
                instrument_token=int(instrument_token),
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            if not historical_data:
                logger.warning(f"No data received for token {instrument_token}")
                return pd.DataFrame()
            
            # Convert to DataFrame and process
            df = pd.DataFrame(historical_data)
            df['datetime'] = pd.to_datetime(df['date'])
            df = df.sort_values('datetime').reset_index(drop=True)
            
            logger.info(f"Fetched {len(df)} candles for token {instrument_token}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for token {instrument_token}: {e}")
            return pd.DataFrame()
    
    def get_quote(self, instrument_token: str) -> Optional[Dict]:
        """
        Get current quote for instrument
        
        Args:
            instrument_token: Zerodha instrument token
            
        Returns:
            Quote data dictionary or None
        """
        if not self.is_connected():
            logger.error("Not connected to Zerodha")
            return None
        
        try:
            quote = self.kite.quote([instrument_token])
            return quote.get(instrument_token)
        except Exception as e:
            logger.error(f"Error fetching quote for {instrument_token}: {e}")
            return None
    
    def get_instruments(self) -> List[Dict]:
        """
        Get list of all instruments
        
        Returns:
            List of instrument dictionaries
        """
        if not self.is_connected():
            logger.error("Not connected to Zerodha")
            return []
        
        try:
            instruments = self.kite.instruments()
            logger.info(f"Fetched {len(instruments)} instruments")
            return instruments
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            return []

# Global service instance
zerodha_service = ZerodhaService()
