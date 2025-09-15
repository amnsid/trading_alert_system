"""
Email notification service
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
from src.config.settings import settings
from src.utils.logger import logger

class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_server = None
    
    def send_alert(
        self,
        symbol: str,
        signal_type: str,
        close_price: float,
        avwap_value: float,
        avwap_anchor: str,
        rs_value: float,
        pattern: str,
        measure: float = None
    ) -> bool:
        """
        Send trading alert email
        
        Args:
            symbol: Trading symbol (NIFTY/BANKNIFTY)
            signal_type: BUY or SELL
            close_price: Current close price
            avwap_value: AVWAP value used
            avwap_anchor: AVWAP anchor (prev_high/prev_low)
            rs_value: Relative strength value
            pattern: Candlestick pattern detected
            measure: Measure value
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Get current IST time
            ist = pytz.timezone(settings.TIMEZONE)
            current_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')
            
            subject = f"🚨 Trading Alert: {signal_type} {symbol}"
            
            # Create email body
            body = self._create_alert_body(
                symbol, signal_type, current_time, close_price,
                avwap_value, avwap_anchor, rs_value, pattern, measure
            )
            
            if settings.DRY_RUN:
                self._print_dry_run_alert(subject, body)
                return True
            
            return self._send_email(subject, body)
            
        except Exception as e:
            logger.error(f"Error sending alert email: {e}")
            return False
    
    def _create_alert_body(
        self, symbol: str, signal_type: str, timestamp: str,
        close_price: float, avwap_value: float, avwap_anchor: str,
        rs_value: float, pattern: str, measure: float = None
    ) -> str:
        """Create formatted email body"""
        
        signal_emoji = "🟢" if signal_type == "BUY" else "🔴"
        
        body = f"""
{signal_emoji} TRADING ALERT GENERATED!

📊 SIGNAL DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Symbol: {symbol}
Signal: {signal_type}
Time: {timestamp}
Close Price: ₹{close_price:.2f}

📈 TECHNICAL ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AVWAP: ₹{avwap_value:.2f} (anchored at {avwap_anchor})
Relative Strength: {rs_value:.4f}
Pattern: {pattern}
{f'Measure: {measure:.4f}' if measure else ''}

⚠️  DISCLAIMER:
This is an automated alert. Please verify manually before trading.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trading Alert System v1.0
        """
        
        return body.strip()
    
    def _print_dry_run_alert(self, subject: str, body: str):
        """Print alert in dry run mode"""
        logger.info("=" * 60)
        logger.info("DRY RUN - Email Alert (would be sent):")
        logger.info(f"To: {settings.ALERT_TO}")
        logger.info(f"Subject: {subject}")
        logger.info("-" * 60)
        logger.info(body)
        logger.info("=" * 60)
    
    def _send_email(self, subject: str, body: str) -> bool:
        """Send actual email"""
        try:
            # Parse multiple recipients
            recipients = [email.strip() for email in settings.ALERT_TO.split(',')]
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_USER
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
                text = msg.as_string()
                server.sendmail(settings.EMAIL_USER, recipients, text)
            
            logger.info(f"Email alert sent successfully to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test email connection"""
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            
            logger.info("Email connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False

# Global service instance
email_service = EmailService()
