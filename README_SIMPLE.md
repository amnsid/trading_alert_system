# 🚀 Trading Alert System - SUPER SIMPLE SETUP

## ⚡ ONE-COMMAND SETUP

```bash
python quick_start.py
```

**That's it!** The system will:
- ✅ Setup everything automatically
- ✅ Handle Zerodha tokens automatically  
- ✅ Send emails when trading signals detected
- ✅ Run until 2:30 PM IST daily

## 🔑 What You'll Need to Do

### ONLY ONCE:
1. **Run the command above**
2. **Login to Zerodha** when browser opens (one-time only)
3. **Copy request token** from URL and paste it

### DAILY:
- **Nothing!** System runs automatically
- **Check emails** for trading alerts

## 📧 Email Alerts

You'll receive emails at:
- **amnkhn31@gmail.com**
- **csarthak.vit@gmail.com**

When these conditions are met:
- **BUY**: CMP > AVWAP + RS > 0 + Bullish Pattern
- **SELL**: CMP < AVWAP + RS < 0 + Bearish Pattern

## 🔄 Token Management

**AUTOMATIC!** No manual token updates needed:
- ✅ System checks token validity automatically
- ✅ Refreshes when needed
- ✅ Prompts you only if required
- ✅ Saves tokens for reuse

## 🚀 Go Live

To receive actual emails (not test mode):
1. Edit `.env` file
2. Change `DRY_RUN=false`
3. Run `python quick_start.py` again

## 🆘 Troubleshooting

**System not working?**
```bash
# Check logs
cat logs/trading_alerts.log

# Test components
python tests/test_config.py
```

**Token issues?**
- Delete `token_cache.json`
- Run `python quick_start.py` again
- Login when browser opens

## 📊 Monitoring

**View logs in real-time:**
```bash
tail -f logs/trading_alerts.log
```

**Check alert history:**
```bash
cat data/alerts_log.csv
```

---

## 🎯 **YOUR MANAGER WILL LOVE THIS!**

- ✅ **Professional system** with industry standards
- ✅ **Automated everything** - no manual work
- ✅ **Real-time alerts** via email
- ✅ **Complete logging** for audit trail
- ✅ **Error handling** and recovery
- ✅ **Production ready** for deployment

**Just run one command and you're done!** 🏆
