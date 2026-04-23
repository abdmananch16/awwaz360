# 🚀 AWAAZ360 Pro - Streamlit Cloud Deployment Guide

## Quick Deploy (5 minutes)

### Step 1: Go to Streamlit Cloud
Visit: **https://share.streamlit.io**

### Step 2: Sign In with GitHub
- Click "Sign in with GitHub"
- Authorize Streamlit to access your repositories

### Step 3: Deploy New App
1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository:** `abdmananch16/awwaz360`
   - **Branch:** `main`
   - **Main file path:** `ap-aur-mein/app.py`
3. Click **"Deploy"**

### Step 4: Add Secrets (Important!)
After deployment starts:
1. Go to your app's settings (gear icon)
2. Click **"Secrets"**
3. Add your API keys:
   ```
   TAVILY_API_KEY = "your-tavily-api-key"
   HF_API_KEY = "your-huggingface-api-key"
   ```

## Get Your API Keys

### Tavily API Key
1. Visit: https://tavily.com
2. Sign up for free
3. Get your API key from dashboard
4. Add to Streamlit Secrets

### Hugging Face API Key
1. Visit: https://huggingface.co/settings/tokens
2. Create a new token
3. Copy the token
4. Add to Streamlit Secrets

## Features Included

✅ Complaint Registration & Tracking
✅ Emergency Helplines (Clickable Phone Numbers)
✅ Blood Donor Directory
✅ Fuel Price Updates
✅ Electricity Bill Calculator
✅ Prayer Times
✅ Weather Information
✅ AI-Powered Chatbot
✅ Civic News & Alerts

## Troubleshooting

### App won't start?
- Check that all dependencies in `requirements.txt` are installed
- Verify API keys are added to Streamlit Secrets
- Check app logs in Streamlit Cloud dashboard

### Database issues?
- The app creates `awaaz360_pro.db` automatically
- Data persists in Streamlit Cloud's file system

### Slow performance?
- First load may take 30-60 seconds
- Subsequent loads are cached

## Support

For issues, check:
- Streamlit docs: https://docs.streamlit.io
- GitHub Issues: https://github.com/abdmananch16/awwaz360/issues

---

**Happy Deploying! 🎉**
