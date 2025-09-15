# 🚀 DEPLOYMENT GUIDE

## ✅ **PERFECT! Deploy First, Token Later!**

### **Step 1: Deploy to Railway (FREE)**

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Trading Alert System"
   git push origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Connect GitHub repository
   - Deploy automatically
   - Get URL: `https://your-app.railway.app`

### **Step 2: Setup Token (After Deployment)**

1. **Visit your deployed URL:**
   `https://your-app.railway.app`

2. **Click "Setup Zerodha Access"**
   - Redirects to Zerodha login
   - Login with credentials
   - Auto-captures token
   - Shows "✅ Setup Complete!"

3. **System Starts Automatically:**
   - Trading system begins monitoring
   - Email alerts activated
   - Runs until 2:30 PM IST daily

---

## 🌐 **How It Works:**

### **Web Interface Mode:**
- ✅ **Shows setup page** if no token
- ✅ **Handles Zerodha OAuth** flow
- ✅ **Captures token** automatically
- ✅ **Saves to system** permanently

### **Trading Mode:**
- ✅ **Starts after** token setup
- ✅ **Monitors markets** automatically  
- ✅ **Sends email alerts**
- ✅ **Runs continuously**

---

## 🔧 **Environment Variables (Set in Railway):**

```env
ZERODHA_API_KEY=2bys3aum1h2tl54z
EMAIL_USER=amnsid31@gmail.com
EMAIL_PASS=bnan jfyh wanv kdry
ALERT_TO=amnkhn31@gmail.com,csarthak.vit@gmail.com
DRY_RUN=false
```

---

## 📊 **Client Experience:**

1. **You deploy** system to cloud
2. **Send client** the setup URL
3. **Client clicks** → Logs into Zerodha → Done!
4. **System runs** 24/7 automatically
5. **Client receives** email alerts

---

## 🎯 **Perfect Solution:**
- ✅ **Deploy without token**
- ✅ **Client setups token** via web
- ✅ **System runs** automatically
- ✅ **Zero maintenance** required

**Deploy now, setup later! 🚀**
