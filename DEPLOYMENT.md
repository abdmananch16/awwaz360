# 🚀 Deployment Guide - AWAAZ360 Pro

## 📋 Prerequisites

- Python 3.8 or higher
- Git (for version control)
- GitHub account (for Streamlit Cloud deployment)

## 🏠 Local Development

### Windows

1. **Open Command Prompt or PowerShell**

2. **Navigate to project directory**
```bash
cd path\to\awaaz360-pro
```

3. **Run the app**
```bash
run.bat
```

Or manually:
```bash
venv\Scripts\activate
streamlit run app.py
```

### Linux/Mac

1. **Open Terminal**

2. **Navigate to project directory**
```bash
cd path/to/awaaz360-pro
```

3. **Make run script executable**
```bash
chmod +x run.sh
```

4. **Run the app**
```bash
./run.sh
```

Or manually:
```bash
source venv/bin/activate
streamlit run app.py
```

## ☁️ Streamlit Cloud Deployment

### Step 1: Prepare Repository

1. **Create GitHub repository**
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name it (e.g., `awaaz360-pro`)
   - Make it public or private

2. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit - AWAAZ360 Pro"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/awaaz360-pro.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

2. **Create New App**
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/awaaz360-pro`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy!"

3. **Wait for Deployment**
   - Streamlit will install dependencies from `requirements.txt`
   - Usually takes 2-5 minutes
   - You'll get a public URL like: `https://your-app-name.streamlit.app`

### Step 3: Configure Secrets (Required for Full Features)

For Streamlit Cloud deployment, add your API keys as secrets:

1. **In Streamlit Cloud Dashboard**
   - Go to your app settings
   - Click "Secrets"
   - Add:
```toml
TAVILY_API_KEY = "your-tavily-api-key-here"
HF_API_KEY = "your-huggingface-api-key-here"
```

2. **Get API Keys**
   - Tavily: https://tavily.com
   - Hugging Face: https://huggingface.co/settings/tokens

3. **For Local Development**
   - Create `.streamlit/secrets.toml` in your project
   - Add the same keys there
   - This file is in `.gitignore` (won't be committed)

## 🔧 Troubleshooting

### Issue: App won't start locally

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Database errors

**Solution:**
```bash
# Delete old database
rm awaaz360_pro.db  # Linux/Mac
del awaaz360_pro.db  # Windows

# Restart app (database will be recreated)
```

### Issue: API errors

**Check:**
- Internet connection
- API keys are valid
- API rate limits not exceeded

### Issue: Streamlit Cloud deployment fails

**Common fixes:**
1. Check `requirements.txt` has all dependencies
2. Ensure Python version compatibility
3. Check app logs in Streamlit Cloud dashboard
4. Verify no hardcoded local paths in code

## 📊 Resource Limits

### Streamlit Cloud (Free Tier)
- **RAM**: 1 GB
- **CPU**: Shared
- **Storage**: Limited
- **Apps**: 1 public app
- **Uptime**: Apps sleep after inactivity

### Recommendations
- Use caching (`@st.cache_data`) for API calls
- Keep database small or use external DB for production
- Optimize images and assets

## 🔐 Security Best Practices

1. **Never commit secrets**
   - Use `.gitignore` for sensitive files
   - Use Streamlit secrets for API keys

2. **Database security**
   - For production, use PostgreSQL or MySQL
   - Add authentication for admin features

3. **Input validation**
   - Sanitize user inputs
   - Prevent SQL injection (use parameterized queries)

## 📱 Custom Domain (Optional)

Streamlit Cloud Pro allows custom domains:
1. Upgrade to Streamlit Cloud Pro
2. Add CNAME record in your DNS settings
3. Configure in Streamlit Cloud dashboard

## 🆘 Support

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Create issue in your repository

## ✅ Deployment Checklist

- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] App runs locally without errors
- [ ] Database initializes correctly
- [ ] API keys configured
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud app created
- [ ] App deployed successfully
- [ ] All features tested on live URL
- [ ] README updated with live URL

---

**Happy Deploying! 🚀**

Created by **Manan** | AWAAZ360 Pro
