# ⚡ Quick Start Guide - AWAAZ360 Pro

## 🎯 Get Running in 3 Steps

### Step 1: Setup (Already Done! ✅)
Your virtual environment is ready with all packages installed.

### Step 2: Run Locally

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Or manually:**
```bash
# Windows
venv\Scripts\activate
streamlit run app.py

# Linux/Mac
source venv/bin/activate
streamlit run app.py
```

### Step 3: Open Browser
The app will automatically open at: `http://localhost:8501`

## 🌐 Deploy to Cloud (5 Minutes)

1. **Create GitHub repo and push code:**
```bash
git init
git add .
git commit -m "AWAAZ360 Pro"
git remote add origin https://github.com/YOUR_USERNAME/awaaz360-pro.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repo
   - Click "Deploy"
   - Done! 🎉

## 📚 Features Overview

| Feature | Description |
|---------|-------------|
| 📝 **Shikayat** | File civic complaints |
| 📋 **Records** | View all complaints |
| 🔍 **Track ID** | Track complaint status |
| ⛽ **Fuel Prices** | Live PSO prices |
| ⚡ **Bill Calc** | Electricity bill estimator |
| 🚨 **Emergency** | Helpline numbers |
| 🩸 **Blood Bank** | Donor registry |
| 🌤️ **Mausam** | Live weather |
| 🕌 **Namaz** | Prayer times |
| 📰 **Khabar** | Latest news (Tavily AI) |
| 🤖 **Help Bot** | AI assistant (Hugging Face) |

## 🔑 API Keys (Already Configured)

- ✅ Tavily API (News)
- ✅ Hugging Face (Chatbot)
- ✅ Open-Meteo (Weather - Free)
- ✅ Al-Adhan (Prayer - Free)

## 📁 Project Structure

```
awaaz360-pro/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── awaaz360_pro.db       # SQLite database (auto-created)
├── fuel_cache.json       # Fuel price cache (auto-created)
├── .streamlit/
│   └── config.toml       # Streamlit theme config
├── venv/                 # Virtual environment
├── README.md             # Project documentation
├── DEPLOYMENT.md         # Detailed deployment guide
├── QUICKSTART.md         # This file
├── run.bat               # Windows run script
└── run.sh                # Linux/Mac run script
```

## 🎨 Customization

### Change Theme Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#00D4AA"      # Teal accent
backgroundColor = "#0D1B2A"    # Dark blue background
```

### Modify Database
Database auto-creates on first run. Tables:
- `complaints` - Complaint records
- `donors` - Blood donor registry

### Add New Features
Edit `app.py` and add new pages in the sidebar navigation.

## 🐛 Common Issues

**Port already in use:**
```bash
streamlit run app.py --server.port 8502
```

**Database locked:**
```bash
# Close all app instances and restart
```

**API not working:**
- Check internet connection
- Verify API keys are valid

## 📞 Need Help?

- Check `DEPLOYMENT.md` for detailed guide
- Read `README.md` for full documentation
- Visit [docs.streamlit.io](https://docs.streamlit.io)

## ✨ Next Steps

1. ✅ Run app locally
2. ✅ Test all features
3. ✅ Deploy to Streamlit Cloud
4. ✅ Share your app URL!

---

**Created by Manan | AWAAZ360 Pro** 🇵🇰
