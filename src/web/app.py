"""
Web interface for token setup
"""
from flask import Flask, request, redirect, render_template_string
import os
import json
from datetime import datetime, timedelta
import pytz
from kiteconnect import KiteConnect
from src.config.settings import settings

app = Flask(__name__)

# HTML Templates
SETUP_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Trading Alert System - Setup</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .btn { background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
        .success { color: green; } .error { color: red; }
    </style>
</head>
<body>
    <h1>🚀 Trading Alert System Setup</h1>
    <p>Click below to setup your Zerodha API access:</p>
    <a href="/auth" class="btn">🔑 Setup Zerodha Access</a>
    <hr>
    <h3>📊 System Status:</h3>
    <p>Email: ✅ Configured (amnsid31@gmail.com)</p>
    <p>Recipients: ✅ amnkhn31@gmail.com, csarthak.vit@gmail.com</p>
    <p>Zerodha API: {{ status }}</p>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Setup Complete!</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
        .success { color: green; font-size: 24px; }
    </style>
</head>
<body>
    <h1 class="success">✅ Setup Complete!</h1>
    <p>Your trading alert system is now active and monitoring:</p>
    <ul style="text-align: left;">
        <li>📊 NIFTY & BANKNIFTY</li>
        <li>⏰ Market hours: 9:15 AM - 2:30 PM IST</li>
        <li>📧 Email alerts when signals detected</li>
        <li>🤖 Fully automated operation</li>
    </ul>
    <hr>
    <p><strong>You can close this page. The system is running automatically!</strong></p>
    <p>Check your email for trading alerts.</p>
</body>
</html>
"""

@app.route('/')
def home():
    """Home page with setup status"""
    try:
        from src.services.token_manager import token_manager
        if token_manager.is_token_valid():
            status = "✅ Connected and Active"
        else:
            status = "❌ Setup Required"
    except:
        status = "❌ Setup Required"
    
    return render_template_string(SETUP_PAGE, status=status)

@app.route('/auth')
def auth():
    """Redirect to Zerodha login"""
    # Get the current domain for callback
    base_url = request.url_root.rstrip('/')
    callback_url = f"{base_url}/callback"
    
    kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
    login_url = kite.login_url()
    
    # Note: Zerodha will redirect to localhost by default
    # We'll handle this in the callback route
    return redirect(login_url)

@app.route('/callback')
def callback():
    """Handle Zerodha callback and setup token"""
    request_token = request.args.get('request_token')
    
    if not request_token:
        return "❌ No request token received", 400
    
    try:
        # Generate access token
        kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
        data = kite.generate_session(request_token, api_secret="3x6qjya3efj9bpjs68nfita8u9df5n75")
        access_token = data["access_token"]
        
        # Save token
        from src.services.token_manager import token_manager
        token_manager.save_token_data(access_token)
        
        # Update environment variable
        os.environ['ZERODHA_ACCESS_TOKEN'] = access_token
        
        return render_template_string(SUCCESS_PAGE)
        
    except Exception as e:
        return f"❌ Setup failed: {e}", 500

@app.route('/status')
def status():
    """System status endpoint"""
    try:
        from src.services.token_manager import token_manager
        from src.services.zerodha_service import zerodha_service
        
        token_valid = token_manager.is_token_valid()
        
        return {
            "status": "active" if token_valid else "setup_required",
            "token_valid": token_valid,
            "email_configured": bool(settings.EMAIL_USER),
            "monitoring": ["NIFTY", "BANKNIFTY"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
