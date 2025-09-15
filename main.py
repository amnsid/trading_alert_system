#!/usr/bin/env python3
"""
Trading Alert System - Main Application
======================================
Production-ready NIFTY/BANKNIFTY trading alert system
"""
import time
import sys
from datetime import datetime
import pytz

from src.config.settings import settings
from src.utils.logger import logger
from src.services.zerodha_service import zerodha_service
from src.services.email_service import email_service
from src.services.token_manager import token_manager
from src.core.trading_engine import trading_engine

class TradingAlertSystem:
    """Main application class"""
    
    def __init__(self):
        self.symbols_config = [
            ('NIFTY', settings.NIFTY_TOKEN, settings.NIFTY200_TOKEN),
            ('BANKNIFTY', settings.BANKNIFTY_TOKEN, settings.BN200_TOKEN)
        ]
    
    def validate_configuration(self) -> bool:
        """Validate all required configuration"""
        logger.info("Validating configuration...")
        
        missing_settings = settings.validate_required_settings()
        if missing_settings:
            logger.error(f"Missing required settings: {', '.join(missing_settings)}")
            logger.error("Please check your .env file and ensure all required variables are set")
            return False
        
        logger.info("✅ Configuration validation passed")
        return True
    
    def initialize_services(self) -> bool:
        """Initialize all services"""
        logger.info("Initializing services...")
        
        # Initialize Zerodha connection
        if not zerodha_service.connect():
            logger.error("❌ Failed to connect to Zerodha API")
            return False
        
        logger.info("✅ Zerodha API connected successfully")
        
        # Test email service if not in dry run
        if not settings.DRY_RUN:
            if not email_service.test_connection():
                logger.error("❌ Email service connection failed")
                return False
            logger.info("✅ Email service connected successfully")
        else:
            logger.info("🔧 Running in DRY_RUN mode - emails will be printed to console")
        
        return True
    
    def is_market_time(self) -> bool:
        """Check if current time is before market cutoff (2:30 PM IST)"""
        ist = pytz.timezone(settings.TIMEZONE)
        now_ist = datetime.now(ist)
        cutoff_time = now_ist.replace(
            hour=settings.MARKET_CUTOFF_HOUR, 
            minute=settings.MARKET_CUTOFF_MINUTE, 
            second=0, 
            microsecond=0
        )
        return now_ist < cutoff_time
    
    def is_5min_boundary(self) -> bool:
        """Check if current time is on a 5-minute boundary"""
        ist = pytz.timezone(settings.TIMEZONE)
        now_ist = datetime.now(ist)
        return now_ist.minute % 5 == 0 and now_ist.second < 30
    
    def run_monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting monitoring loop...")
        logger.info(f"📊 Monitoring symbols: {[symbol[0] for symbol in self.symbols_config]}")
        logger.info(f"⏰ Market cutoff: {settings.MARKET_CUTOFF_HOUR}:{settings.MARKET_CUTOFF_MINUTE:02d} IST")
        
        while True:
            try:
                # Check if it's market time
                if not self.is_market_time():
                    ist = pytz.timezone(settings.TIMEZONE)
                    current_time = datetime.now(ist).strftime('%H:%M:%S')
                    logger.info(f"🔚 Market time ended (after {settings.MARKET_CUTOFF_HOUR}:{settings.MARKET_CUTOFF_MINUTE:02d} IST). Current time: {current_time}")
                    break
                
                # Only process on 5-minute boundaries
                if self.is_5min_boundary():
                    logger.info("⏱️  Processing 5-minute candle boundary...")
                    
                    for symbol_name, symbol_token, ref_token in self.symbols_config:
                        try:
                            alert_generated = trading_engine.process_symbol(
                                symbol_name, symbol_token, ref_token
                            )
                            
                            if alert_generated:
                                logger.info(f"🚨 Alert generated for {symbol_name}")
                            else:
                                logger.info(f"📊 No signal for {symbol_name}")
                                
                        except Exception as e:
                            logger.error(f"❌ Error processing {symbol_name}: {e}")
                            continue
                    
                    # Clean up old processed candles
                    trading_engine.cleanup_old_processed_candles()
                    
                    # Check token validity periodically (every hour)
                    if datetime.now(pytz.timezone(settings.TIMEZONE)).minute == 0:
                        token_manager.auto_refresh_token_if_needed()
                    
                    # Wait to avoid processing the same candle multiple times
                    logger.info("⏳ Waiting 30 seconds before next check...")
                    time.sleep(30)
                
                else:
                    # Wait 1 minute before next check
                    time.sleep(60)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal. Shutting down...")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {e}")
                time.sleep(60)  # Wait before retrying
        
        logger.info("🔚 Trading Alert System stopped")
    
    def run(self):
        """Main entry point"""
        logger.info("=" * 60)
        logger.info("🚀 TRADING ALERT SYSTEM STARTING")
        logger.info("=" * 60)
        logger.info(f"📍 Environment: {'PRODUCTION' if settings.is_production else 'DEVELOPMENT'}")
        logger.info(f"🔧 Dry Run: {'ENABLED' if settings.DRY_RUN else 'DISABLED'}")
        
        # Validate configuration
        if not self.validate_configuration():
            logger.error("❌ Configuration validation failed. Exiting...")
            sys.exit(1)
        
        # Initialize services
        if not self.initialize_services():
            logger.error("❌ Service initialization failed. Exiting...")
            sys.exit(1)
        
        # Start monitoring
        try:
            self.run_monitoring_loop()
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            sys.exit(1)

def main():
    """Application entry point"""
    app = TradingAlertSystem()
    app.run()

if __name__ == "__main__":
    main()
