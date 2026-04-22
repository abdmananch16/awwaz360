# 🏛️ AWAAZ360 Pro - Civic Suite

**Pakistan ka Civic Platform — Shikayat, Malumat, Madad**

Created by **Manan**

## 🌟 Features

- **📝 Complaint System**: Register and track civic complaints
- **🩸 Blood Bank**: Donor registration and search
- **⛽ Live Fuel Prices**: Real-time PSO fuel prices
- **⚡ Bill Calculator**: Electricity bill estimator
- **🚨 Emergency Helplines**: Quick access to emergency services
- **🌤️ Weather**: Live weather for Rawalpindi/Islamabad
- **🕌 Prayer Times**: Accurate namaz timings
- **📰 News**: Latest civic news powered by Tavily AI
- **🤖 AI Chatbot**: Intelligent assistant powered by Hugging Face

## 🚀 Installation

### Local Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd awaaz360-pro
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the app**
```bash
streamlit run app.py
```

## ☁️ Deploy on Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

**Note**: The app uses embedded API keys for Tavily and Hugging Face. For production, use Streamlit secrets.

## 🔑 API Keys Used

- **Tavily API**: For news fetching
- **Hugging Face**: For AI chatbot (Llama 3.2 3B)
- **Open-Meteo**: For weather data (free, no key needed)
- **Al-Adhan**: For prayer times (free, no key needed)

## 📊 Database

Uses SQLite (`awaaz360_pro.db`) for:
- Complaint records
- Blood donor registry

## 🎨 Theme

Dark theme with teal accents inspired by Pakistani civic colors.

## 📱 Pages

1. **Home** - Dashboard with stats and quick info
2. **Shikayat** - File new complaints
3. **Records** - View and manage complaints
4. **Track ID** - Track complaint status
5. **Fuel Prices** - Live fuel prices from PSO
6. **Bill Calculator** - Estimate electricity bills
7. **Emergency** - Emergency helpline numbers
8. **Blood Bank** - Donor registration and search
9. **Mausam** - Weather information
10. **Namaz** - Prayer times
11. **Khabar** - Latest civic news
12. **Help Bot** - AI-powered assistant

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite3
- **APIs**: Tavily, Hugging Face, Open-Meteo, Al-Adhan
- **Web Scraping**: BeautifulSoup4, Requests
- **AI Model**: Meta Llama 3.2 3B Instruct

## 📝 License

Created for educational and civic purposes.

## 👨‍💻 Developer

**Manan**  
AWAAZ360 - Pakistan's Civic Platform

---

**خوش آمدید — Welcome to AWAAZ360 Pro!** 🇵🇰
