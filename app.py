import streamlit as st
import sqlite3
import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from huggingface_hub import InferenceClient
from tavily import TavilyClient

# ════════════════════════════════════════════════════════════
#  CONFIGURATION
# ════════════════════════════════════════════════════════════
DB_FILE = "awaaz360_pro.db"
FUEL_CACHE = "fuel_cache.json"

# API Keys - Use Streamlit secrets or environment variables
try:
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
    HF_API_KEY = st.secrets["HF_API_KEY"]
except (KeyError, FileNotFoundError):
    # Fallback to environment variables for local development
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    HF_API_KEY = os.getenv("HF_API_KEY", "")

# Initialize clients
if TAVILY_API_KEY:
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
else:
    tavily_client = None
    
if HF_API_KEY:
    hf_client = InferenceClient(token=HF_API_KEY)
else:
    hf_client = None

# ════════════════════════════════════════════════════════════
#  DATABASE INITIALIZATION
# ════════════════════════════════════════════════════════════
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS complaints(
            id TEXT PRIMARY KEY, 
            name TEXT, 
            phone TEXT, 
            category TEXT,
            desc TEXT, 
            location TEXT, 
            date TEXT, 
            status TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS donors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, 
            phone TEXT, 
            b_group TEXT, 
            area TEXT, 
            date TEXT
        )''')
        conn.commit()

init_db()

# ════════════════════════════════════════════════════════════
#  STREAMLIT PAGE CONFIG
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AWAAZ360 Pro - Civic Suite",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════
#  CUSTOM CSS
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .main {background-color: #0D1B2A;}
    .stApp {background-color: #0D1B2A;}
    h1, h2, h3 {color: #00D4AA !important;}
    .stButton>button {
        background-color: #00D4AA;
        color: #0D1B2A;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #00FFD0;
        color: #0D1B2A;
    }
    .stat-card {
        background: linear-gradient(135deg, #1B2D45 0%, #162333 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #2a4060;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    .stat-label {
        color: #8899AA;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    div[data-testid="stSidebar"] {
        background-color: #0f1e2e;
    }
    .css-1d391kg {color: #E8F0FE;}
    .stTextInput>div>div>input {
        background-color: #162333;
        color: #E8F0FE;
        border: 1px solid #2a4060;
    }
    .stSelectbox>div>div>select {
        background-color: #162333;
        color: #E8F0FE;
    }
    .stTextArea>div>div>textarea {
        background-color: #162333;
        color: #E8F0FE;
        border: 1px solid #2a4060;
    }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  API HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def get_prayer_times():
    try:
        now = datetime.now()
        url = (f"https://api.aladhan.com/v1/timingsByCity"
               f"?city=Rawalpindi&country=Pakistan&method=1"
               f"&date={now.day}-{now.month}-{now.year}")
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            t = r.json()["data"]["timings"]
            return {
                "Fajr": t["Fajr"],
                "Sunrise": t["Sunrise"],
                "Dhuhr": t["Dhuhr"],
                "Asr": t["Asr"],
                "Maghrib": t["Maghrib"],
                "Isha": t["Isha"]
            }
    except Exception as e:
        st.error(f"Prayer times fetch error: {e}")
    return None

@st.cache_data(ttl=1800)
def get_weather():
    try:
        url = ("https://api.open-meteo.com/v1/forecast"
               "?latitude=33.6007&longitude=73.0679"
               "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
               "&timezone=Asia%2FKarachi")
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            d = r.json()["current"]
            descs = {
                0: "Saaf aasman ☀️", 1: "Mostly saaf 🌤️", 2: "Partly cloudy ⛅",
                3: "Overcast ☁️", 45: "Fog 🌫️", 51: "Halki baarish 🌦️",
                53: "Baarish 🌧️", 61: "Halki baarish 🌦️", 63: "Baarish 🌧️",
                71: "Halki barf ❄️", 73: "Barf ❄️", 80: "Shower 🌦️", 95: "Toofan ⛈️"
            }
            return {
                "temp": d["temperature_2m"],
                "humidity": d["relative_humidity_2m"],
                "wind": d["wind_speed_10m"],
                "desc": descs.get(d["weather_code"], "—")
            }
    except Exception as e:
        st.error(f"Weather fetch error: {e}")
    return None

DEFAULT_PRICES = [("Super Petrol", "366.58"), ("High Speed Diesel", "353.00"), ("LPG (kg)", "304.12")]

def load_fuel_cache():
    try:
        if os.path.exists(FUEL_CACHE):
            with open(FUEL_CACHE) as f:
                d = json.load(f)
                return d.get("prices", DEFAULT_PRICES), d.get("updated", "N/A")
    except Exception:
        pass
    return DEFAULT_PRICES, "N/A"

def save_fuel_cache(prices, updated):
    try:
        with open(FUEL_CACHE, "w") as f:
            json.dump({"prices": prices, "updated": updated}, f)
    except Exception:
        pass

@st.cache_data(ttl=86400)
def fetch_pso():
    try:
        r = requests.get("https://psopk.com/en/fuels/fuel-prices",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code != 200:
            return None, None
        
        soup = BeautifulSoup(r.text, "html.parser")
        lines = [l.strip() for l in soup.get_text().splitlines() if l.strip()]
        pet = hsd = lpg = None
        
        def next_price(idx):
            for j in range(idx+1, min(idx+6, len(lines))):
                try:
                    v = float(lines[j].replace(",", "").replace("Rs", "").replace("rs", "").strip())
                    if 50 < v < 1500:
                        return f"{v:.2f}"
                except Exception:
                    pass
            return None
        
        for i, line in enumerate(lines):
            ll = line.lower()
            if pet is None and any(k in ll for k in ["ms ", "motor spirit", "ron 92", "super petrol"]):
                pet = next_price(i)
            if hsd is None and any(k in ll for k in ["high speed diesel", "hsd"]):
                hsd = next_price(i)
            if lpg is None and any(k in ll for k in ["lpg", "liquefied petroleum"]):
                lpg = next_price(i)
        
        if not pet and not hsd:
            return None, None
        
        return ([("Super Petrol", pet or DEFAULT_PRICES[0][1]),
                ("High Speed Diesel", hsd or DEFAULT_PRICES[1][1]),
                ("LPG (kg)", lpg or DEFAULT_PRICES[2][1])],
                datetime.now().strftime("%d %b %Y %I:%M %p"))
    except Exception:
        return None, None

# ════════════════════════════════════════════════════════════
#  CHATBOT WITH HUGGING FACE
# ════════════════════════════════════════════════════════════
def get_bot_response(user_message):
    if not hf_client:
        return "❌ Chatbot service not configured. Please set HF_API_KEY."
    
    system_prompt = """You are a helpful civic assistant for AWAAZ360, a citizen complaint system created by Manan. 
You help Pakistani citizens with:
- Electricity (LESCO, WAPDA) complaints and info
- Water (WASA) issues
- Gas (SNGPL, SSGC) problems
- Road and infrastructure complaints
- Emergency services (Rescue 1122, Police, Fire)
- Fuel prices and updates
- Prayer times and weather information
- Blood donation queries

Always respond in a mix of Urdu and English (Roman Urdu), be helpful, concise, and provide actionable information.
If you don't know something specific, guide them to the relevant helpline or government portal."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = hf_client.chat_completion(
            messages=messages,
            model="meta-llama/Llama-3.2-3B-Instruct",
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, chatbot service temporarily unavailable. Error: {str(e)}"

# ════════════════════════════════════════════════════════════
#  NEWS FETCHING WITH TAVILY
# ════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def fetch_news_tavily():
    if not tavily_client:
        return get_fallback_news()
    
    try:
        response = tavily_client.search(
            query="Pakistan civic news electricity water gas complaints LESCO WASA",
            max_results=5,
            search_depth="basic"
        )
        
        news_items = []
        for result in response.get('results', []):
            news_items.append({
                'title': result.get('title', 'No title'),
                'link': result.get('url', ''),
                'date': datetime.now().strftime("%d %b %Y"),
                'source': result.get('url', '').split('/')[2] if result.get('url') else 'Unknown'
            })
        
        return news_items if news_items else get_fallback_news()
    except Exception as e:
        st.warning(f"News fetch error: {e}")
        return get_fallback_news()

def get_fallback_news():
    return [
        {"title": "LESCO: Load shedding schedule April 2026 jari", "date": "22 Apr 2026", "source": "LESCO", "link": "https://lesco.gov.pk"},
        {"title": "WASA: Pani supply normal — masla hal ho gaya", "date": "21 Apr 2026", "source": "WASA", "link": "https://wasa.com.pk"},
        {"title": "Punjab Govt: Online shikayat portal launch", "date": "20 Apr 2026", "source": "Punjab Govt", "link": "https://ekhidmat.punjab.gov.pk"},
        {"title": "Rescue 1122: New ambulances Rawalpindi mein shamil", "date": "19 Apr 2026", "source": "Rescue", "link": "https://rescue.gov.pk"},
        {"title": "OGRA: Fuel prices April 18 se naye rates", "date": "18 Apr 2026", "source": "OGRA", "link": "https://ogra.org.pk"},
    ]

# ════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ════════════════════════════════════════════════════════════
st.sidebar.title("🏛️ AWAAZ360 PRO")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📝 Shikayat", "📋 Records", "🔍 Track ID", 
     "⛽ Fuel Prices", "⚡ Bill Calculator", "🚨 Emergency", 
     "🩸 Blood Bank", "🌤️ Mausam", "🕌 Namaz", "📰 Khabar", "🤖 Help Bot"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.info(f"📅 {datetime.now().strftime('%A, %d %b %Y')}")
st.sidebar.info(f"🕐 {datetime.now().strftime('%I:%M %p')}")

# ════════════════════════════════════════════════════════════
#  HOME PAGE
# ════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.title("خوش آمدید — AWAAZ360 Pro")
    st.markdown("### Pakistan ka Civic Platform — Shikayat, Malumat, Madad")
    
    # Stats
    with sqlite3.connect(DB_FILE) as conn:
        total = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        donors = conn.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
        pend = conn.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'").fetchone()[0]
        resol = conn.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'").fetchone()[0]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="stat-card">
            <p class="stat-value" style="color: #4FC3F7;">{total}</p>
            <p class="stat-label">Total Complaints</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-card">
            <p class="stat-value" style="color: #FF4757;">{pend}</p>
            <p class="stat-label">Pending</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-card">
            <p class="stat-value" style="color: #2ED573;">{resol}</p>
            <p class="stat-label">Resolved</p>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="stat-card">
            <p class="stat-value" style="color: #fd79a8;">{donors}</p>
            <p class="stat-label">Blood Donors</p>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Weather and Prayer
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌤️ Mausam — Rawalpindi")
        weather = get_weather()
        if weather:
            st.markdown(f"### {weather['desc']}")
            st.metric("Temperature", f"{weather['temp']}°C")
            st.metric("Humidity", f"{weather['humidity']}%")
            st.metric("Wind Speed", f"{weather['wind']} km/h")
        else:
            st.info("🔄 Fetching weather data...")
    
    with col2:
        st.subheader("🕌 Namaz — Rawalpindi")
        prayer = get_prayer_times()
        if prayer:
            for name, time in prayer.items():
                st.text(f"{name}: {time}")
        else:
            st.info("🔄 Fetching prayer times...")
    
    st.markdown("---")
    
    # Fuel Quick View
    st.subheader("⛽ Fuel Prices")
    prices, updated = load_fuel_cache()
    col1, col2, col3 = st.columns(3)
    for i, (name, price) in enumerate(prices):
        with [col1, col2, col3][i]:
            st.metric(name, f"Rs. {price}")
    st.caption(f"💾 Last updated: {updated}")

# ════════════════════════════════════════════════════════════
#  COMPLAINT FORM
# ════════════════════════════════════════════════════════════
elif page == "📝 Shikayat":
    st.title("📝 New Complaint Register")
    
    with st.form("complaint_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Aapka Naam *", placeholder="e.g. Ahmed Ali")
            category = st.selectbox("Category *", ["", "Electricity", "Water", "Roads", "Sanitation", "Gas", "Drainage", "Other"])
        with col2:
            phone = st.text_input("Phone Number", placeholder="03XX-XXXXXXX")
            location = st.text_input("Area / Location", placeholder="e.g. Satellite Town, Rwp")
        
        desc = st.text_area("Masla Detail mein *", placeholder="Apna masla yahan likhein...", height=120)
        
        priority = st.radio("Priority:", ["Low", "Normal", "High", "Urgent"], horizontal=True, index=1)
        
        submitted = st.form_submit_button("📤 Submit Complaint")
        
        if submitted:
            if not name or not category or not desc:
                st.error("❌ Naam, Category aur Detail zaroor bharein!")
            else:
                import uuid
                cid = "AWZ-" + uuid.uuid4().hex[:8].upper()
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute(
                        "INSERT INTO complaints VALUES (?,?,?,?,?,?,?,?)",
                        (cid, name, phone or "N/A", category, desc, location or "N/A",
                         datetime.now().strftime("%d %b %Y"), "Pending")
                    )
                    conn.commit()
                st.success(f"✅ Darj ho gayi! Aapki Complaint ID: **{cid}**")
                st.balloons()

# ════════════════════════════════════════════════════════════
#  RECORDS
# ════════════════════════════════════════════════════════════
elif page == "📋 Records":
    st.title("📋 Complaint Records")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search by Name or ID", placeholder="Search...")
    with col2:
        status_filter = st.selectbox("Status Filter", ["All", "Pending", "In Progress", "Resolved", "Rejected"])
    
    with sqlite3.connect(DB_FILE) as conn:
        sql = "SELECT id, name, category, location, date, status FROM complaints WHERE (name LIKE ? OR id LIKE ?)"
        params = [f"%{search}%", f"%{search}%"]
        if status_filter != "All":
            sql += " AND status=?"
            params.append(status_filter)
        rows = conn.execute(sql, params).fetchall()
    
    st.dataframe(
        rows,
        column_config={
            0: "ID",
            1: "Name",
            2: "Category",
            3: "Location",
            4: "Date",
            5: "Status"
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"📊 Total: {len(rows)} records")
    
    # Update/Delete
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        update_id = st.text_input("Complaint ID to Update", placeholder="AWZ-XXXXXXXX")
    with col2:
        new_status = st.selectbox("New Status", ["Pending", "In Progress", "Resolved", "Rejected"])
    with col3:
        st.write("")
        st.write("")
        if st.button("✏️ Update Status"):
            if update_id:
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("UPDATE complaints SET status=? WHERE id=?", (new_status, update_id))
                    conn.commit()
                st.success(f"✅ {update_id} updated to {new_status}")
                st.rerun()

# ════════════════════════════════════════════════════════════
#  TRACK BY ID
# ════════════════════════════════════════════════════════════
elif page == "🔍 Track ID":
    st.title("🔍 Track Complaint by ID")
    
    cid = st.text_input("Apna Complaint ID darj karein:", placeholder="AWZ-XXXXXXXX").strip().upper()
    
    if st.button("🔍 Track") and cid:
        with sqlite3.connect(DB_FILE) as conn:
            row = conn.execute("SELECT * FROM complaints WHERE id=?", (cid,)).fetchone()
        
        if row:
            cid_, name, phone, cat, desc, loc, date, status = row
            
            st.success(f"### Complaint: {cid_}")
            
            status_colors = {"Pending": "🟠", "In Progress": "🔵", "Resolved": "🟢", "Rejected": "🔴"}
            st.markdown(f"## {status_colors.get(status, '⚪')} Status: **{status}**")
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**👤 Naam:** {name}")
                st.info(f"**📞 Phone:** {phone}")
                st.info(f"**🏷️ Category:** {cat}")
            with col2:
                st.info(f"**📍 Location:** {loc}")
                st.info(f"**📅 Date:** {date}")
            
            st.markdown("**📝 Detail:**")
            st.write(desc)
            
            # Timeline
            st.markdown("---")
            st.markdown("### 📊 Status Timeline")
            steps = ["Pending", "In Progress", "Resolved"]
            cur_i = steps.index(status) if status in steps else -1
            
            cols = st.columns(len(steps))
            for i, step in enumerate(steps):
                with cols[i]:
                    if i <= cur_i:
                        st.success(f"✅ {step}")
                    else:
                        st.info(f"⬜ {step}")
        else:
            st.error(f"❌ '{cid}' nahi mila")

# ════════════════════════════════════════════════════════════
#  FUEL PRICES
# ════════════════════════════════════════════════════════════
elif page == "⛽ Fuel Prices":
    st.title("⛽ Fuel Prices Pakistan")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔃 Refresh Prices"):
            st.cache_data.clear()
            st.rerun()
    
    prices, updated = load_fuel_cache()
    
    # Try to fetch live prices
    live_prices, live_updated = fetch_pso()
    if live_prices:
        prices, updated = live_prices, live_updated
        save_fuel_cache(prices, updated)
        st.success(f"✅ Live prices — {updated}")
    else:
        st.warning(f"💾 Cached prices — {updated}")
    
    # Display prices
    col1, col2, col3 = st.columns(3)
    icons = ["⛽", "🚛", "🔥"]
    colors = ["#FFD700", "#FF6B35", "#2ED573"]
    
    for i, (name, price) in enumerate(prices):
        with [col1, col2, col3][i]:
            st.markdown(f"""<div class="stat-card">
                <p style="font-size: 2rem;">{icons[i]}</p>
                <p class="stat-label">{name}</p>
                <p class="stat-value" style="color: {colors[i]};">Rs. {price}</p>
                <p class="stat-label">{"per litre" if i < 2 else "per kg"}</p>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("ℹ️ OGRA prices har 15 din mein update hoti hain")

# ════════════════════════════════════════════════════════════
#  ELECTRICITY BILL CALCULATOR
# ════════════════════════════════════════════════════════════
elif page == "⚡ Bill Calculator":
    st.title("⚡ Electricity Bill Estimator")
    
    st.markdown("### Enter your appliance usage:")
    
    appliances = [
        ("💡 Fans", 80),
        ("💡 LED Bulbs", 12),
        ("❄️ AC (1 ton)", 1200),
        ("🖥️ Computer", 200),
        ("📺 TV", 100),
        ("🔌 Iron", 1000),
        ("🫙 Fridge", 150)
    ]
    
    usage = {}
    col1, col2 = st.columns(2)
    
    for i, (name, watt) in enumerate(appliances):
        with col1 if i % 2 == 0 else col2:
            qty = st.number_input(f"{name} ({watt}W)", min_value=0, value=0, step=1, key=f"app_{i}")
            usage[name] = (qty, watt)
    
    st.markdown("---")
    
    if st.button("⚡ Calculate Bill"):
        total_units = sum(qty * watt * 10 * 30 / 1000 for qty, watt in usage.values())
        
        # NEPRA Slabs
        if total_units <= 100:
            bill = total_units * 7.74
        elif total_units <= 200:
            bill = 100 * 7.74 + (total_units - 100) * 10.06
        elif total_units <= 300:
            bill = 100 * 7.74 + 100 * 10.06 + (total_units - 200) * 14.05
        else:
            bill = 100 * 7.74 + 100 * 10.06 + 100 * 14.05 + (total_units - 300) * 19.45
        
        fc = 500
        gst = bill * 0.17
        total = bill + fc + gst
        
        st.success(f"### ⚡ {total_units:.0f} kWh / month")
        st.metric("Total Bill", f"Rs. {total:,.0f}")
        st.caption(f"Energy: Rs.{bill:,.0f} + GST(17%): Rs.{gst:,.0f} + Fixed: Rs.{fc}")
    
    st.info("📊 NEPRA Slabs: 0-100: Rs.7.74 | 101-200: Rs.10.06 | 201-300: Rs.14.05 | 300+: Rs.19.45")

# ════════════════════════════════════════════════════════════
#  EMERGENCY HELPLINES
# ════════════════════════════════════════════════════════════
elif page == "🚨 Emergency":
    st.title("🚨 Emergency Helplines")
    
    services = [
        ("🚑", "Rescue", "1122", "Medical & Rescue"),
        ("🚔", "Police", "15", "Crime & Security"),
        ("🔥", "Fire Brigade", "16", "Fire Emergency"),
        ("🏥", "Edhi", "115", "Ambulance"),
        ("⚡", "LESCO/WAPDA", "118", "Electricity"),
        ("💧", "WASA", "0800-9272", "Water Supply"),
        ("🚘", "Motorway Police", "130", "Motorway"),
        ("☎️", "Aman Helpline", "1717", "Citizen Services")
    ]
    
    cols = st.columns(4)
    for i, (icon, name, num, desc) in enumerate(services):
        with cols[i % 4]:
            st.markdown(f"""<div class="stat-card">
                <p style="font-size: 2rem;">{icon}</p>
                <p style="font-weight: bold; margin: 0.5rem 0;">{name}</p>
                <p class="stat-label">{desc}</p>
                <p style="font-size: 1.2rem; font-weight: bold; color: #00D4AA; margin-top: 0.5rem;">📞 {num}</p>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  BLOOD BANK
# ════════════════════════════════════════════════════════════
elif page == "🩸 Blood Bank":
    st.title("🩸 Blood Donor Directory")
    
    tab1, tab2 = st.tabs(["➕ Register Donor", "🔍 Search Donors"])
    
    with tab1:
        st.subheader("Register as Blood Donor")
        with st.form("donor_form"):
            col1, col2 = st.columns(2)
            with col1:
                d_name = st.text_input("Donor Naam *", placeholder="Poora naam")
                d_group = st.selectbox("Blood Group *", ["", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            with col2:
                d_phone = st.text_input("Phone *", placeholder="03XX-XXXXXXX")
                d_area = st.text_input("Area", placeholder="e.g. Rawalpindi")
            
            submitted = st.form_submit_button("🩸 Register Donor")
            
            if submitted:
                if not d_name or not d_group:
                    st.error("❌ Naam aur Blood Group zaroor!")
                else:
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute(
                            "INSERT INTO donors(name, phone, b_group, area, date) VALUES(?,?,?,?,?)",
                            (d_name, d_phone or "N/A", d_group, d_area or "N/A", 
                             datetime.now().strftime("%d %b %Y"))
                        )
                        conn.commit()
                    st.success(f"✅ {d_name} register ho gaya! Shukriya 🙏")
                    st.balloons()
    
    with tab2:
        st.subheader("Search Blood Donors")
        
        col1, col2 = st.columns(2)
        with col1:
            search_group = st.selectbox("Blood Group", ["All", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        with col2:
            search_area = st.text_input("Area", placeholder="Search area...")
        
        with sqlite3.connect(DB_FILE) as conn:
            sql = "SELECT id, name, phone, b_group, area, date FROM donors WHERE 1=1"
            params = []
            if search_group != "All":
                sql += " AND b_group=?"
                params.append(search_group)
            if search_area:
                sql += " AND area LIKE ?"
                params.append(f"%{search_area}%")
            
            donors = conn.execute(sql, params).fetchall()
        
        if donors:
            st.dataframe(
                donors,
                column_config={
                    0: "ID",
                    1: "Name",
                    2: "Phone",
                    3: "Blood Group",
                    4: "Area",
                    5: "Date"
                },
                use_container_width=True,
                hide_index=True
            )
            st.caption(f"🩸 {len(donors)} donors found")
        else:
            st.info("No donors found matching criteria")

# ════════════════════════════════════════════════════════════
#  WEATHER
# ════════════════════════════════════════════════════════════
elif page == "🌤️ Mausam":
    st.title("🌤️ Mausam — Rawalpindi/Islamabad")
    
    if st.button("🔃 Refresh Weather"):
        st.cache_data.clear()
        st.rerun()
    
    weather = get_weather()
    
    if weather:
        st.markdown(f"## {weather['desc']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌡️ Temperature", f"{weather['temp']}°C")
        with col2:
            st.metric("💧 Humidity", f"{weather['humidity']}%")
        with col3:
            st.metric("💨 Wind Speed", f"{weather['wind']} km/h")
        
        st.info("ℹ️ Source: Open-Meteo | Rawalpindi 33.6°N 73.1°E")
    else:
        st.warning("🔄 Weather data fetch ho raha hai...")

# ════════════════════════════════════════════════════════════
#  PRAYER TIMES
# ════════════════════════════════════════════════════════════
elif page == "🕌 Namaz":
    st.title("🕌 Namaz Awqaat — Rawalpindi")
    
    if st.button("🔃 Refresh Prayer Times"):
        st.cache_data.clear()
        st.rerun()
    
    st.info(f"📅 {datetime.now().strftime('%A, %d %B %Y')} | {datetime.now().strftime('%I:%M %p')}")
    
    prayer = get_prayer_times()
    
    if prayer:
        now_t = datetime.now().strftime("%H:%M")
        prayers = list(prayer.items())
        icons = ["🌅", "🌄", "☀️", "🌤️", "🌅", "🌙"]
        
        for i, (name, time) in enumerate(prayers):
            is_next = time >= now_t
            if is_next:
                st.success(f"### {icons[i]} {name}: **{time}** ← Agla Waqt")
            else:
                st.info(f"{icons[i]} {name}: {time}")
        
        st.caption("ℹ️ Source: Al-Adhan API | Method: UISK Karachi")
    else:
        st.warning("🔄 Prayer times fetch ho rahi hain...")

# ════════════════════════════════════════════════════════════
#  NEWS
# ════════════════════════════════════════════════════════════
elif page == "📰 Khabar":
    st.title("📰 Civic Alerts & News")
    
    if st.button("🔃 Refresh News"):
        st.cache_data.clear()
        st.rerun()
    
    with st.spinner("🔄 News fetch ho rahi hai..."):
        news_items = fetch_news_tavily()
    
    for item in news_items:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### [{item['title']}]({item['link']})")
            with col2:
                st.caption(f"📅 {item['date']}")
            st.caption(f"🔗 Source: {item['source']}")
            st.markdown("---")

# ════════════════════════════════════════════════════════════
#  CHATBOT
# ════════════════════════════════════════════════════════════
elif page == "🤖 Help Bot":
    st.title("🤖 Civic Help Bot")
    st.markdown("**Powered by Hugging Face AI**")
    st.caption("Created by Manan — AWAAZ360 Citizen Complaint System")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main AWAAZ360 Civic Bot hoon.\nPuchh sakte ho: bijli, paani, gas, sadak, fuel, namaz, mausam, emergency, blood, FIR"}
        ]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Quick buttons
    st.markdown("**Quick Questions:**")
    col1, col2, col3, col4 = st.columns(4)
    quick_questions = ["Bijli complaint kaise karein?", "Paani ka masla", "Gas shikayat", "Emergency numbers"]
    
    for i, q in enumerate(quick_questions):
        with [col1, col2, col3, col4][i]:
            if st.button(q, key=f"quick_{i}"):
                st.session_state.messages.append({"role": "user", "content": q})
                with st.spinner("Thinking..."):
                    response = get_bot_response(q)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Apna sawal yahan likhein..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_bot_response(prompt)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# ════════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════════
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏛️ AWAAZ360 Pro")
st.sidebar.caption("Created by **Manan**")
st.sidebar.caption("Pakistan ka Civic Platform")
st.sidebar.caption("Version 2.0 — Streamlit Edition")
