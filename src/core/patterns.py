"""
Candlestick pattern detection
"""
from typing import Optional, Dict
from src.utils.logger import logger

class CandlestickPatterns:
    """Class for detecting candlestick patterns"""
    
    @staticmethod
    def detect_pattern(ohlc: Dict[str, float]) -> Optional[str]:
        """
        Detect candlestick patterns from OHLC data
        
        Args:
            ohlc: Dictionary with 'open', 'high', 'low', 'close' keys
            
        Returns:
            Pattern name or None
        """
        try:
            o, h, l, c = ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close']
            
            # Validate OHLC data
            if not all(isinstance(x, (int, float)) for x in [o, h, l, c]):
                logger.warning("Invalid OHLC data provided")
                return None
            
            # Green Hammer (Bullish)
            # Conditions: Close > Open, Long lower shadow (>2x body), Small upper shadow
            if (c > o and 
                (o - l) > 2 * (c - o) and 
                h >= c and 
                (o - l) > (h - c)):
                return "Green_Hammer"
            
            # Red Hammer (Bullish Alternative)  
            # Conditions: Close < Open, Long lower shadow (>2x body), Small upper shadow
            if (c < o and 
                (c - l) > 2 * (o - c) and 
                h >= o and 
                (c - l) > (h - o)):
                return "Red_Hammer"
            
            # Inverted Hammer (Bearish)
            # Conditions: Close < Open, Long upper shadow (>2x body), Small lower shadow
            if (c < o and 
                (h - o) > 2 * (o - c) and 
                l <= c and 
                (h - o) > (c - l)):
                return "Inverted_Hammer"
            
            # Inverted Green Hammer (Bearish Alternative)
            # Conditions: Close > Open, Long upper shadow (>2x body), Small lower shadow
            if (c > o and 
                (h - c) > 2 * (c - o) and 
                l <= o and 
                (h - c) > (o - l)):
                return "Inverted_Green_Hammer"
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return None
    
    @staticmethod
    def is_bullish_pattern(pattern: str) -> bool:
        """Check if pattern is bullish"""
        return pattern in ['Green_Hammer', 'Red_Hammer']
    
    @staticmethod
    def is_bearish_pattern(pattern: str) -> bool:
        """Check if pattern is bearish"""
        return pattern in ['Inverted_Hammer', 'Inverted_Green_Hammer']
