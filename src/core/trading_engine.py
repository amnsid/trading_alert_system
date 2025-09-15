"""
Main trading engine for signal evaluation and alert generation
"""
import csv
import os
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
import pytz
import pandas as pd

from src.config.settings import settings
from src.utils.logger import logger
from src.services.zerodha_service import zerodha_service
from src.services.email_service import email_service
from src.core.indicators import TechnicalIndicators
from src.core.patterns import CandlestickPatterns

class TradingEngine:
    """Main trading engine for processing symbols and generating alerts"""
    
    def __init__(self):
        self.processed_candles = set()  # To avoid duplicate alerts
        self.indicators = TechnicalIndicators()
        self.patterns = CandlestickPatterns()
    
    def evaluate_buy_setup(
        self, 
        close: float, 
        avwap_high: float, 
        avwap_low: float, 
        rs: float, 
        pattern: str
    ) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        Evaluate BUY setup conditions
        
        Returns:
            Tuple of (is_buy_signal, avwap_used, measure)
        """
        # Check if CMP > AVWAP (either anchor)
        cmp_above_avwap = False
        avwap_used = None
        measure = None
        
        if avwap_high and close > avwap_high:
            cmp_above_avwap = True
            avwap_used = avwap_high
            measure = (close - avwap_high) / avwap_high
        elif avwap_low and close > avwap_low:
            cmp_above_avwap = True
            avwap_used = avwap_low
            measure = (close - avwap_low) / avwap_low
        
        # Check all BUY conditions
        conditions = [
            cmp_above_avwap,                                    # CMP > AVWAP
            measure and measure > 0,                            # Measure > 0
            rs and rs > 0,                                      # RS > 0
            self.patterns.is_bullish_pattern(pattern)           # Bullish patterns
        ]
        
        is_buy = all(conditions)
        
        logger.info(f"BUY evaluation - CMP above AVWAP: {cmp_above_avwap}, "
                   f"Measure > 0: {measure and measure > 0}, "
                   f"RS > 0: {rs and rs > 0}, "
                   f"Bullish pattern: {self.patterns.is_bullish_pattern(pattern)}")
        
        return is_buy, avwap_used, measure
    
    def evaluate_sell_setup(
        self, 
        close: float, 
        avwap_high: float, 
        avwap_low: float, 
        rs: float, 
        pattern: str
    ) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        Evaluate SELL setup conditions
        
        Returns:
            Tuple of (is_sell_signal, avwap_used, measure)
        """
        # Check if CMP < AVWAP (either anchor)
        cmp_below_avwap = False
        avwap_used = None
        measure = None
        
        if avwap_high and close < avwap_high:
            cmp_below_avwap = True
            avwap_used = avwap_high
            measure = (avwap_high - close) / avwap_high
        elif avwap_low and close < avwap_low:
            cmp_below_avwap = True
            avwap_used = avwap_low
            measure = (avwap_low - close) / avwap_low
        
        # Check all SELL conditions
        conditions = [
            cmp_below_avwap,                                    # CMP < AVWAP
            measure and measure > 0,                            # Measure > 0
            rs and rs < 0,                                      # RS < 0
            self.patterns.is_bearish_pattern(pattern)           # Bearish patterns
        ]
        
        is_sell = all(conditions)
        
        logger.info(f"SELL evaluation - CMP below AVWAP: {cmp_below_avwap}, "
                   f"Measure > 0: {measure and measure > 0}, "
                   f"RS < 0: {rs and rs < 0}, "
                   f"Bearish pattern: {self.patterns.is_bearish_pattern(pattern)}")
        
        return is_sell, avwap_used, measure
    
    def process_symbol(
        self, 
        symbol_name: str, 
        symbol_token: str, 
        reference_token: str
    ) -> bool:
        """
        Process a single symbol for trading signals
        
        Args:
            symbol_name: Symbol name (NIFTY/BANKNIFTY)
            symbol_token: Symbol instrument token
            reference_token: Reference index token for RS calculation
            
        Returns:
            True if alert was generated, False otherwise
        """
        try:
            # Generate unique candle ID to avoid duplicates
            ist = pytz.timezone(settings.TIMEZONE)
            current_time = datetime.now(ist)
            candle_id = f"{symbol_name}_{current_time.strftime('%Y%m%d_%H%M')}"
            
            if candle_id in self.processed_candles:
                logger.info(f"Already processed {candle_id}, skipping")
                return False
            
            logger.info(f"Processing {symbol_name}...")
            
            # 1. Fetch 5-minute candle data
            symbol_data = zerodha_service.fetch_historical_data(symbol_token)
            ref_data = zerodha_service.fetch_historical_data(reference_token)
            
            if symbol_data.empty or ref_data.empty:
                logger.warning(f"Insufficient data for {symbol_name}")
                return False
            
            # 2. Get latest candle
            latest_candle = symbol_data.iloc[-1]
            latest_ref_candle = ref_data.iloc[-1]
            
            latest_close = latest_candle['close']
            ref_close = latest_ref_candle['close']
            
            # 3. Compute previous day high/low for AVWAP anchoring
            prev_high, prev_low = self.indicators.compute_previous_day_high_low(symbol_data)
            if not prev_high or not prev_low:
                logger.warning(f"Cannot compute previous day high/low for {symbol_name}")
                return False
            
            # 4. Compute AVWAP from both anchors
            avwap_high = self.indicators.compute_avwap_from_anchor(symbol_data, prev_high, 'high')
            avwap_low = self.indicators.compute_avwap_from_anchor(symbol_data, prev_low, 'low')
            
            if not avwap_high or not avwap_low:
                logger.warning(f"Cannot compute AVWAP for {symbol_name}")
                return False
            
            # 5. Detect candlestick pattern
            ohlc = {
                'open': latest_candle['open'],
                'high': latest_candle['high'],
                'low': latest_candle['low'],
                'close': latest_candle['close']
            }
            pattern = self.patterns.detect_pattern(ohlc)
            
            # 6. Compute Relative Strength
            rs_value = self.indicators.compute_relative_strength(latest_close, ref_close)
            
            logger.info(f"{symbol_name} - Close: {latest_close}, AVWAP(H): {avwap_high:.2f}, "
                       f"AVWAP(L): {avwap_low:.2f}, RS: {rs_value:.4f if rs_value else 'N/A'}, Pattern: {pattern}")
            
            # 7. Evaluate BUY setup
            is_buy, buy_avwap, buy_measure = self.evaluate_buy_setup(
                latest_close, avwap_high, avwap_low, rs_value, pattern
            )
            
            # 8. Evaluate SELL setup  
            is_sell, sell_avwap, sell_measure = self.evaluate_sell_setup(
                latest_close, avwap_high, avwap_low, rs_value, pattern
            )
            
            # 9. Generate alerts
            alert_generated = False
            
            if is_buy:
                logger.info(f"🟢 BUY SIGNAL for {symbol_name}!")
                avwap_anchor = "prev_high" if buy_avwap == avwap_high else "prev_low"
                
                # Send email alert
                email_service.send_alert(
                    symbol_name, "BUY", latest_close, buy_avwap, 
                    avwap_anchor, rs_value, pattern, buy_measure
                )
                
                # Log to CSV
                self._log_to_csv(
                    symbol_name, "BUY", latest_close, avwap_anchor, 
                    buy_avwap, rs_value, pattern, buy_measure
                )
                alert_generated = True
                
            elif is_sell:
                logger.info(f"🔴 SELL SIGNAL for {symbol_name}!")
                avwap_anchor = "prev_high" if sell_avwap == avwap_high else "prev_low"
                
                # Send email alert
                email_service.send_alert(
                    symbol_name, "SELL", latest_close, sell_avwap,
                    avwap_anchor, rs_value, pattern, sell_measure
                )
                
                # Log to CSV
                self._log_to_csv(
                    symbol_name, "SELL", latest_close, avwap_anchor,
                    sell_avwap, rs_value, pattern, sell_measure
                )
                alert_generated = True
            
            # Mark this candle as processed
            self.processed_candles.add(candle_id)
            
            return alert_generated
            
        except Exception as e:
            logger.error(f"Error processing {symbol_name}: {e}")
            return False
    
    def _log_to_csv(
        self, 
        symbol: str, 
        signal_type: str, 
        close: float, 
        avwap_anchor: str, 
        avwap_value: float, 
        rs_value: float, 
        pattern: str,
        measure: float = None
    ):
        """Log alert to CSV file"""
        try:
            ist = pytz.timezone(settings.TIMEZONE)
            timestamp = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
            
            # Create log file if it doesn't exist
            file_exists = os.path.isfile(settings.CSV_LOG_FILE)
            
            with open(settings.CSV_LOG_FILE, 'a', newline='') as csvfile:
                fieldnames = [
                    'timestamp_ist', 'symbol', 'signal', 'close', 
                    'avwap_anchor', 'avwap_value', 'rs_value', 
                    'pattern', 'measure'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow({
                    'timestamp_ist': timestamp,
                    'symbol': symbol,
                    'signal': signal_type,
                    'close': close,
                    'avwap_anchor': avwap_anchor,
                    'avwap_value': avwap_value,
                    'rs_value': rs_value,
                    'pattern': pattern,
                    'measure': measure
                })
            
            logger.info(f"Alert logged to {settings.CSV_LOG_FILE}")
            
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
    
    def cleanup_old_processed_candles(self):
        """Clean up old processed candles to prevent memory buildup"""
        ist = pytz.timezone(settings.TIMEZONE)
        current_date = datetime.now(ist).strftime('%Y%m%d')
        
        # Keep only today's candles
        self.processed_candles = {
            candle_id for candle_id in self.processed_candles 
            if candle_id.split('_')[1].startswith(current_date)
        }
        
        logger.info(f"Cleaned up old processed candles, keeping {len(self.processed_candles)} for today")

# Global trading engine instance
trading_engine = TradingEngine()
