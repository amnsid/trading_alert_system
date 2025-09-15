"""
Configuration management for Trading Alert System
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    LOGS_DIR: Path = BASE_DIR / "logs"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Zerodha API Configuration
    ZERODHA_API_KEY: str = os.getenv("ZERODHA_API_KEY", "")
    ZERODHA_ACCESS_TOKEN: str = os.getenv("ZERODHA_ACCESS_TOKEN", "")
    
    # Instrument Tokens
    NIFTY_TOKEN: str = os.getenv("NIFTY_TOKEN", "256265")
    BANKNIFTY_TOKEN: str = os.getenv("BANKNIFTY_TOKEN", "260105")
    NIFTY200_TOKEN: str = os.getenv("NIFTY200_TOKEN", "13297412")
    BN200_TOKEN: str = os.getenv("BN200_TOKEN", "260105")
    
    # Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASS: str = os.getenv("EMAIL_PASS", "")
    ALERT_TO: str = os.getenv("ALERT_TO", "")
    
    # System Configuration
    DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Kolkata")
    MARKET_CUTOFF_HOUR: int = int(os.getenv("MARKET_CUTOFF_HOUR", "14"))
    MARKET_CUTOFF_MINUTE: int = int(os.getenv("MARKET_CUTOFF_MINUTE", "30"))
    
    # File paths
    LOG_FILE: str = str(LOGS_DIR / "trading_alerts.log")
    CSV_LOG_FILE: str = str(DATA_DIR / "alerts_log.csv")
    
    # Deployment
    PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    def __init__(self):
        """Initialize settings and create necessary directories"""
        self.LOGS_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)
    
    def validate_required_settings(self) -> list[str]:
        """Validate that all required settings are provided"""
        missing = []
        
        if not self.ZERODHA_API_KEY:
            missing.append("ZERODHA_API_KEY")
        if not self.ZERODHA_ACCESS_TOKEN:
            missing.append("ZERODHA_ACCESS_TOKEN")
        if not self.EMAIL_USER:
            missing.append("EMAIL_USER")
        if not self.EMAIL_PASS:
            missing.append("EMAIL_PASS")
        if not self.ALERT_TO:
            missing.append("ALERT_TO")
            
        return missing
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DRY_RUN

# Global settings instance
settings = Settings()
