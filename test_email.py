#!/usr/bin/env python3
"""
Test email functionality
"""
import sys
from pathlib import Path
import os

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Set environment variables for testing
os.environ['EMAIL_USER'] = 'amnsid31@gmail.com'
os.environ['EMAIL_PASS'] = 'bnan jfyh wanv kdry'
os.environ['ALERT_TO'] = 'amnkhn31@gmail.com,csarthak.vit@gmail.com'
os.environ['DRY_RUN'] = 'false'  # Set to false to actually send email

def test_email():
    """Test email sending"""
    print("📧 Testing Email System...")
    
    try:
        from src.services.email_service import email_service
        
        # Test connection first
        print("🔗 Testing SMTP connection...")
        if email_service.test_connection():
            print("✅ SMTP connection successful!")
        else:
            print("❌ SMTP connection failed!")
            return False
        
        # Send test alert
        print("📨 Sending test alert...")
        success = email_service.send_alert(
            symbol="NIFTY",
            signal_type="BUY",
            close_price=18500.50,
            avwap_value=18400.25,
            avwap_anchor="prev_high",
            rs_value=0.0275,
            pattern="Green_Hammer",
            measure=0.0054
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print("📧 Check your email inboxes:")
            print("   - amnkhn31@gmail.com")
            print("   - csarthak.vit@gmail.com")
            return True
        else:
            print("❌ Failed to send test email!")
            return False
            
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📧 EMAIL SYSTEM TEST")
    print("=" * 60)
    
    if test_email():
        print("\n✅ EMAIL SYSTEM WORKING!")
        print("🚀 Ready to proceed with full system setup")
    else:
        print("\n❌ EMAIL SYSTEM FAILED!")
        print("🔧 Please check your email credentials")
