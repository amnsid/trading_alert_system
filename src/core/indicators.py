"""
Technical indicators for trading analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, Optional, Dict
import pytz
from src.config.settings import settings
from src.utils.logger import logger

class TechnicalIndicators:
    """Class containing all technical indicator calculations"""
    
    @staticmethod
    def compute_previous_day_high_low(candles_df: pd.DataFrame) -> Tuple[Optional[float], Optional[float]]:
        """
        Compute previous trading day's high and low
        
        Args:
            candles_df: DataFrame with OHLCV data
            
        Returns:
            Tuple of (prev_high, prev_low)
        """
        if candles_df.empty:
            return None, None
        
        try:
            ist = pytz.timezone(settings.TIMEZONE)
            today = datetime.now(ist).date()
            
            # Filter for previous day's data
            prev_day_data = candles_df[candles_df['datetime'].dt.date < today]
            
            if prev_day_data.empty:
                logger.warning("No previous day data available")
                return None, None
            
            # Get the most recent previous day
            latest_prev_day = prev_day_data['datetime'].dt.date.max()
            prev_day_candles = prev_day_data[prev_day_data['datetime'].dt.date == latest_prev_day]
            
            prev_high = prev_day_candles['high'].max()
            prev_low = prev_day_candles['low'].min()
            
            logger.info(f"Previous day High: {prev_high}, Low: {prev_low}")
            return prev_high, prev_low
            
        except Exception as e:
            logger.error(f"Error computing previous day high/low: {e}")
            return None, None
    
    @staticmethod
    def compute_avwap_from_anchor(
        candles_df: pd.DataFrame, 
        anchor_price: float, 
        anchor_type: str
    ) -> Optional[float]:
        """
        Compute Anchored VWAP from a specific anchor price
        
        Args:
            candles_df: DataFrame with OHLCV data
            anchor_price: Anchor price (previous day high/low)
            anchor_type: 'high' or 'low' for identification
            
        Returns:
            AVWAP value or None
        """
        try:
            if candles_df.empty:
                return None
            
            ist = pytz.timezone(settings.TIMEZONE)
            today = datetime.now(ist).date()
            
            # Filter for today's data only
            today_data = candles_df[candles_df['datetime'].dt.date == today].copy()
            
            if today_data.empty:
                logger.warning("No today's data for AVWAP calculation")
                return None
            
            # Calculate typical price * volume for each candle
            today_data['typical_price'] = (today_data['high'] + today_data['low'] + today_data['close']) / 3
            today_data['price_volume'] = today_data['typical_price'] * today_data['volume']
            
            # Calculate cumulative sums
            cum_price_volume = today_data['price_volume'].cumsum()
            cum_volume = today_data['volume'].cumsum()
            
            # AVWAP is the latest cumulative price*volume / cumulative volume
            if cum_volume.iloc[-1] > 0:
                latest_avwap = cum_price_volume.iloc[-1] / cum_volume.iloc[-1]
                logger.info(f"AVWAP from {anchor_type} anchor ({anchor_price}): {latest_avwap}")
                return latest_avwap
            
            return None
            
        except Exception as e:
            logger.error(f"Error computing AVWAP: {e}")
            return None
    
    @staticmethod
    def compute_relative_strength(symbol_close: float, reference_close: float) -> Optional[float]:
        """
        Compute Relative Strength: RS = (Symbol Close / Reference Close) - 1
        
        Args:
            symbol_close: Current symbol close price
            reference_close: Reference index close price
            
        Returns:
            Relative strength value or None
        """
        try:
            if symbol_close and reference_close and reference_close != 0:
                rs = (symbol_close / reference_close) - 1
                return rs
            return None
        except Exception as e:
            logger.error(f"Error computing RS: {e}")
            return None
