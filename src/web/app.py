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
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Trading Alert System &mdash; Setup</title>
    <style>
        :root {
            color-scheme: light;
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        body {
            margin: 0;
            background: #f4f6fb;
            color: #1f2933;
        }

        .layout {
            max-width: 960px;
            margin: 0 auto;
            padding: 40px 24px 80px;
            display: grid;
            gap: 24px;
        }

        .page-header h1 {
            font-size: 2rem;
            margin: 0;
        }

        .subtitle {
            margin-top: 8px;
            color: #52606d;
            font-size: 1rem;
        }

        .card {
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
        }

        .card h2 {
            margin: 0;
            font-size: 1.25rem;
        }

        .primary-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 14px 24px;
            background: #1c64f2;
            color: #ffffff;
            font-weight: 600;
            text-decoration: none;
            border-radius: 8px;
            margin-top: 18px;
            transition: background 0.2s ease;
        }

        .primary-button:hover {
            background: #1554c0;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            padding: 6px 16px;
            border-radius: 999px;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .status-ready {
            background: #e3f9e5;
            color: #116149;
        }

        .status-warning {
            background: #fde8e8;
            color: #aa2e25;
        }

        .details {
            list-style: none;
            padding: 0;
            margin: 20px 0 0;
            display: grid;
            gap: 12px;
        }

        .details li {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .details span {
            color: #52606d;
            font-size: 0.95rem;
        }

        .details strong {
            font-size: 0.95rem;
        }

        .hint {
            margin-top: 12px;
            font-size: 0.9rem;
            color: #52606d;
            line-height: 1.5;
        }

        .steps {
            counter-reset: step;
            list-style: none;
            padding: 0;
            margin: 20px 0 0;
            display: grid;
            gap: 14px;
        }

        .steps li {
            position: relative;
            padding-left: 42px;
            line-height: 1.6;
            color: #1f2933;
        }

        .steps li::before {
            counter-increment: step;
            content: counter(step);
            position: absolute;
            left: 0;
            top: 0;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #1c64f2;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
        }

        .footer-note {
            font-size: 0.85rem;
            color: #687385;
            text-align: center;
        }

        .link-group {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-top: 20px;
        }

        .secondary-link {
            color: #1c64f2;
            text-decoration: none;
            font-weight: 600;
        }

        .secondary-link:hover {
            text-decoration: underline;
        }

        @media (max-width: 640px) {
            .layout {
                padding: 24px 16px 60px;
            }

            .card {
                padding: 20px;
            }

            .card-header {
                align-items: flex-start;
            }

            .details li {
                flex-direction: column;
                align-items: flex-start;
            }

            .steps li {
                padding-left: 36px;
            }
        }
    </style>
</head>
<body>
    <main class="layout">
        <header class="page-header">
            <h1>Trading Alert System</h1>
            <p class="subtitle">Complete the secure Zerodha authentication to activate automated monitoring.</p>
        </header>

        <section class="card">
            <div class="card-header">
                <h2>Zerodha connection</h2>
                <span class="status-pill {{ status_class }}">{{ status_label }}</span>
            </div>
            <p>Launch the Zerodha authentication flow to grant the trading alert system access. Once completed, the refresh token is stored securely and daily renewals happen automatically.</p>
            <a href="/auth" class="primary-button">Start Zerodha Authentication</a>
            <p class="hint">You only need to sign in once per deployment. Subsequent restarts reuse the cached refresh token.</p>
            <div class="link-group">
                <a href="/status" class="secondary-link">View API status JSON</a>
                <a href="/logs" class="secondary-link">View recent logs</a>
            </div>
        </section>

        <section class="card">
            <div class="card-header">
                <h2>Configuration summary</h2>
            </div>
            <ul class="details">
                <li><span>Email sender</span><strong>{{ email_user }}</strong></li>
                <li><span>Alert recipients</span><strong>{{ recipients }}</strong></li>
                <li><span>Zerodha API key</span><strong>{{ api_key }}</strong></li>
                <li><span>Environment</span><strong>{{ environment_mode }}</strong></li>
                <li><span>Market cutoff</span><strong>{{ market_cutoff }}</strong></li>
            </ul>
            <p class="hint">These values are loaded from the active environment. Update the deployment variables to make permanent changes.</p>
        </section>

        <section class="card">
            <div class="card-header">
                <h2>Operations checklist</h2>
            </div>
            <ol class="steps">
                <li>Initiate the authentication flow using the button above and complete the Zerodha login.</li>
                <li>Confirm that the status indicator shows <strong>Connected and active</strong>.</li>
                <li>Leave the service running during market hours. Alerts are emailed automatically to the configured recipients.</li>
            </ol>
        </section>

        <p class="footer-note">Need help? Review the deployment documentation or contact the system administrator.</p>
    </main>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Trading Alert System &mdash; Authentication complete</title>
    <style>
        body {
            margin: 0;
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f4f6fb;
            color: #1f2933;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 24px;
        }

        .panel {
            background: #ffffff;
            border-radius: 12px;
            padding: 32px;
            max-width: 520px;
            text-align: center;
            box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
        }

        h1 {
            margin-top: 0;
            font-size: 1.75rem;
        }

        p {
            line-height: 1.6;
            margin: 12px 0;
        }

        ul {
            text-align: left;
            padding-left: 18px;
            margin: 18px 0;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="panel">
        <h1>Authentication complete</h1>
        <p>The Zerodha session is now active and credentials have been stored securely. Automated refresh cycles keep the access token current.</p>
        <ul>
            <li>Markets monitored: NIFTY and BANKNIFTY</li>
            <li>Operational window: 9:15 AM to 2:30 PM IST</li>
            <li>Email notifications sent to the configured recipients</li>
        </ul>
        <p>You may close this window. The trading alert system continues to run in the background.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Home page with setup status"""
    email_user = settings.EMAIL_USER or "Not configured"
    raw_recipients = settings.ALERT_TO
    if isinstance(raw_recipients, str):
        parsed_recipients = [value.strip() for value in raw_recipients.split(',') if value.strip()]
        recipients = ", ".join(parsed_recipients) if parsed_recipients else "Not configured"
    else:
        recipients = "Not configured"
    api_key = settings.ZERODHA_API_KEY or "Not configured"
    environment_mode = "Dry run" if settings.DRY_RUN else "Live trading"
    market_cutoff = f"{settings.MARKET_CUTOFF_HOUR:02d}:{settings.MARKET_CUTOFF_MINUTE:02d} IST"

    try:
        from src.services.token_manager import token_manager
        if token_manager.is_token_valid():
            status_label = "Connected and active"
            status_class = "status-ready"
        else:
            status_label = "Setup required"
            status_class = "status-warning"
    except Exception:
        status_label = "Setup required"
        status_class = "status-warning"

    return render_template_string(
        SETUP_PAGE,
        status_label=status_label,
        status_class=status_class,
        email_user=email_user,
        recipients=recipients,
        api_key=api_key,
        environment_mode=environment_mode,
        market_cutoff=market_cutoff,
    )

@app.route('/auth')
def auth():
    """Redirect to Zerodha login"""
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
        return "No request token received", 400

    try:
        # Generate access token
        kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
        if not settings.ZERODHA_API_SECRET:
            return "Zerodha API secret is not configured", 500

        data = kite.generate_session(request_token, api_secret=settings.ZERODHA_API_SECRET)
        access_token = data["access_token"]
        refresh_token = data.get("refresh_token")

        # Save token
        from src.services.token_manager import token_manager
        token_manager.save_token_data(access_token, refresh_token=refresh_token)

        # Update environment variable
        os.environ['ZERODHA_ACCESS_TOKEN'] = access_token

        return render_template_string(SUCCESS_PAGE)

    except Exception as e:
        return f"Setup failed: {e}", 500

@app.route('/status')
def status():
    """System status endpoint"""
    try:
        from src.services.token_manager import token_manager
        import pytz
        from datetime import datetime
        
        token_valid = token_manager.is_token_valid()
        
        # Check if it's market time
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        cutoff_time = now_ist.replace(
            hour=settings.MARKET_CUTOFF_HOUR,
            minute=settings.MARKET_CUTOFF_MINUTE,
            second=0,
            microsecond=0,
        )
        is_market_time = now_ist < cutoff_time

        return {
            "status": "active" if token_valid else "setup_required",
            "token_valid": token_valid,
            "email_configured": bool(settings.EMAIL_USER),
            "monitoring": ["NIFTY", "BANKNIFTY"],
            "current_time_ist": now_ist.strftime('%Y-%m-%d %H:%M:%S IST'),
            "is_market_time": is_market_time,
            "market_cutoff": f"{settings.MARKET_CUTOFF_HOUR:02d}:{settings.MARKET_CUTOFF_MINUTE:02d} IST",
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
        <html lang=\"en\">
        <head>
            <meta charset=\"UTF-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
            <title>Trading Alert System &mdash; Logs</title>
            <style>
                body {
                    margin: 0;
                    background: #0f172a;
                    color: #e2e8f0;
                    font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                }

                .wrapper {
                    max-width: 960px;
                    margin: 0 auto;
                    padding: 32px 20px 80px;
                }

                header {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                    margin-bottom: 24px;
                }

                h1 {
                    margin: 0;
                    font-size: 1.8rem;
                    font-weight: 600;
                }

                .actions {
                    display: flex;
                    gap: 12px;
                    flex-wrap: wrap;
                    margin-top: 12px;
                }

                .button {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    padding: 10px 18px;
                    border-radius: 6px;
                    font-weight: 600;
                    text-decoration: none;
                    transition: opacity 0.2s ease;
                }

                .button.primary {
                    background: #1c64f2;
                    color: #ffffff;
                }

                .button.secondary {
                    background: rgba(148, 163, 184, 0.2);
                    color: #e2e8f0;
                }

                .button:hover {
                    opacity: 0.85;
                }

                .log-container {
                    background: rgba(15, 23, 42, 0.85);
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.12);
                    overflow: auto;
                    max-height: 70vh;
                }

                .log-entry {
                    font-family: 'Source Code Pro', 'Fira Code', monospace;
                    font-size: 0.9rem;
                    padding: 8px 12px;
                    border-radius: 6px;
                    background: rgba(30, 41, 59, 0.65);
                    margin-bottom: 8px;
                    white-space: pre-wrap;
                    word-break: break-word;
                }

                .log-entry:last-child {
                    margin-bottom: 0;
                }

                @media (max-width: 640px) {
                    .wrapper {
                        padding: 24px 16px 60px;
                    }

                    h1 {
                        font-size: 1.5rem;
                    }
                }
            </style>
        </head>
        <body>
            <div class="wrapper">
                <header>
                    <h1>Trading system logs</h1>
                    <p>Review the latest activity from the monitoring service.</p>
                    <div class="actions">
                        <a href="/logs" class="button primary">Refresh log view</a>
                        <a href="/" class="button secondary">Return to setup</a>
                        <a href="/status" class="button secondary">View status JSON</a>
                    </div>
                </header>
                <div class="log-container">
        """ + "".join([f'<div class="log-entry">{line.strip()}</div>' for line in recent_logs]) + """
                </div>
            </div>
        </body>
        </html>
        """
        
        return logs_html

    except Exception as e:
        return f"Error reading logs: {e}", 500

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
            "status": "Data fetch working",
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
