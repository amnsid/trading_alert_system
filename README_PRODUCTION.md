# Trading Alert System - Production Setup

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- Zerodha account with API access
- Gmail account with app password

### 2. Setup Environment
```bash
# Clone repository
git clone <your-repo-url>
cd trading_alert_system

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials
```

### 3. Get Zerodha Access Token
```bash
python get_access_token.py
# Follow instructions to get token
# Update ZERODHA_ACCESS_TOKEN in .env
```

### 4. Test System
```bash
# Test configuration
python tests/test_config.py

# Test email system
python test_email.py

# Run system (dry-run mode)
python main.py
```

### 5. Go Live
```bash
# Set DRY_RUN=false in .env
# Run system
python main.py
```

## 🐳 Docker Deployment

### Local Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Cloud Deployment Options

#### Railway.app (Free)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Render.com (Free)
1. Connect GitHub repository
2. Set environment variables in dashboard
3. Deploy automatically

#### Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
heroku config:set ZERODHA_API_KEY=your_key
heroku config:set ZERODHA_ACCESS_TOKEN=your_token
# ... set other env vars
git push heroku main
```

## 📊 System Features

### ✅ Implemented Features
- 5-minute candle monitoring
- AVWAP calculation (anchored to prev day high/low)
- Relative Strength computation
- 4 candlestick patterns detection
- Email alerts to multiple recipients
- CSV logging with all fields
- 2:30 PM IST cutoff
- Duplicate prevention
- Production-grade logging
- Docker support

### 📈 Trading Rules
- **BUY Signal**: CMP > AVWAP + RS > 0 + Bullish Pattern
- **SELL Signal**: CMP < AVWAP + RS < 0 + Bearish Pattern
- **Patterns**: Green Hammer, Red Hammer, Inverted Hammer, Inverted Green Hammer
- **Market Hours**: Until 2:30 PM IST
- **Processing**: Every 5-minute boundary

## 🔧 Configuration

### Required Environment Variables
```env
ZERODHA_API_KEY=your_api_key
ZERODHA_ACCESS_TOKEN=your_access_token
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
ALERT_TO=recipient1@gmail.com,recipient2@gmail.com
```

### Optional Settings
```env
DRY_RUN=false
LOG_LEVEL=INFO
MARKET_CUTOFF_HOUR=14
MARKET_CUTOFF_MINUTE=30
```

## 📋 Monitoring & Logs

### Log Files
- `logs/trading_alerts.log` - System logs
- `data/alerts_log.csv` - Alert history

### Health Checks
```bash
# Check system status
curl http://localhost:8080/health

# View recent logs
tail -f logs/trading_alerts.log
```

## 🚨 Troubleshooting

### Common Issues
1. **Token Expired**: Regenerate access token daily
2. **Email Failed**: Check Gmail app password
3. **No Data**: Verify instrument tokens
4. **Connection Error**: Check internet/API limits

### Support
- Check logs first: `logs/trading_alerts.log`
- Verify .env configuration
- Test components individually

## 🔐 Security Notes
- Never commit .env file
- Use app passwords for Gmail
- Rotate access tokens regularly
- Monitor API usage limits

## 📈 Performance
- Memory usage: ~50MB
- CPU usage: Minimal (only on 5-min boundaries)
- Network: ~1MB/hour during market hours
- Disk: ~10MB/month for logs
