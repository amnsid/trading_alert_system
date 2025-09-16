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
        import pytz
        from datetime import datetime
        
        token_valid = token_manager.is_token_valid()
        
        # Check if it's market time
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        cutoff_time = now_ist.replace(hour=14, minute=30, second=0, microsecond=0)
        is_market_time = now_ist < cutoff_time
        
        return {
            "status": "active" if token_valid else "setup_required",
            "token_valid": token_valid,
            "email_configured": bool(settings.EMAIL_USER),
            "monitoring": ["NIFTY", "BANKNIFTY"],
            "current_time_ist": now_ist.strftime('%Y-%m-%d %H:%M:%S IST'),
            "is_market_time": is_market_time,
            "market_cutoff": "14:30 IST"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/logs')
def view_logs():
    """View recent system logs"""
    try:
        import os
        log_file = os.path.join('logs', 'trading_alerts.log')
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_logs = lines[-50:]  # Last 50 lines
        else:
            recent_logs = ["No logs found"]
        
        logs_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Logs</title>
            <style>
                body { font-family: monospace; margin: 20px; }
                .log { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px; }
                .refresh { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>📊 Trading System Logs</h1>
            <a href="/logs" class="refresh">🔄 Refresh</a>
            <a href="/status" class="refresh">📈 Status</a>
            <hr>
            <div>
        """ + "".join([f'<div class="log">{line.strip()}</div>' for line in recent_logs]) + """
            </div>
        </body>
        </html>
        """
        
        return logs_html
        
    except Exception as e:
        return f"❌ Error reading logs: {e}", 500

@app.route('/test_data')
def test_data():
    """Test if we can fetch market data"""
    try:
        from src.services.zerodha_service import zerodha_service
        
        # Test connection
        if not zerodha_service.connect():
            return {"error": "Cannot connect to Zerodha API"}, 500
        
        # Try to fetch NIFTY data
        nifty_data = zerodha_service.fetch_historical_data('256265', lookback_days=1)
        
        if nifty_data.empty:
            return {"error": "No NIFTY data received"}, 500
        
        latest_candle = nifty_data.iloc[-1]
        
        return {
            "status": "✅ Data fetch working",
            "nifty_latest": {
                "datetime": str(latest_candle['datetime']),
                "open": float(latest_candle['open']),
                "high": float(latest_candle['high']),
                "low": float(latest_candle['low']),
                "close": float(latest_candle['close']),
                "volume": int(latest_candle['volume'])
            },
            "total_candles": len(nifty_data)
        }
        
    except Exception as e:
        return {"error": f"Data fetch failed: {e}"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
