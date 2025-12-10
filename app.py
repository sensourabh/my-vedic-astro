import streamlit as st
import google.generativeai as genai
import datetime
import ephem
from geopy.geocoders import Nominatim

# --- PAGE SETUP ---
st.set_page_config(
    page_title="ASTROMINI", 
    page_icon="🌌", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (THE ORIGINAL GLOWING THEME 🌟) ---
st.markdown("""
<style>
    /* 1. Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');

    /* 2. Main Background - Deep Space */
    .stApp {
        background-color: #050505;
        background-image: linear-gradient(to bottom, #050505 0%, #0b1021 100%);
        color: #FFFFFF;
    }

    /* 3. INPUT FIELDS (Dark with Neon Glow) */
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #121826 !important; /* Dark background */
        color: #FFFFFF !important; /* White Text */
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 500;
        border: 1px solid #00F5FF !important; /* Neon Blue Border */
        border-radius: 8px;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
    }
    
    /* Dropdown Menu Colors */
    div[data-baseweb="popover"], div[data-baseweb="menu"], div[data-baseweb="option"] {
        background-color: #121826;
        color: white;
    }

    /* Labels */
    .stTextInput label, .stDateInput label, .stTimeInput label, .stSelectSlider label, .stRadio label {
        color: #00F5FF !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.9rem !important;
        text-shadow: 0 0 5px rgba(0, 245, 255, 0.5);
    }

    /* 4. HEADERS (Gradient Text) */
    .astromini-header {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(to right, #B026FF, #00F5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3.5rem;
        filter: drop-shadow(0 0 15px rgba(176, 38, 255, 0.6));
        margin-bottom: 0;
    }
    .sub-header {
        font-family: 'Orbitron', sans-serif;
        color: #FFFFFF;
        font-size: 1.2rem;
        letter-spacing: 4px;
        text-shadow: 0 0 10px #00F5FF;
        margin-top: -10px;
    }

    /* 5. SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid #B026FF;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        text-shadow: 0 0 8px #B026FF;
    }

    /* 6. PLANET CARDS (Glassmorphism) */
    .planet-card {
        background: rgba(20, 25, 40, 0.7);
        border: 1px solid #00F5FF;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.1);
        backdrop-filter: blur(5px);
        margin-bottom: 10px;
    }
    .planet-name {
        color: #FFD700; /* Gold */
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    .planet-sign {
        color: #FFFFFF;
        font-size: 1rem;
        text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
    }
    .planet-deg {
        color: #B026FF;
        font-family: monospace;
    }

    /* 7. CHAT BUBBLES */
    .user-msg {
        background: #1F2937;
        color: #fff;
        padding: 12px 18px;
        border-radius: 15px 15px 0 15px;
        border-right: 3px solid #00F5FF;
        font-family: 'Roboto', sans-serif;
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.1);
        margin-bottom: 10px;
    }
    .bot-msg {
        background: #111827;
        color: #E0E0E0;
        padding: 12px 18px;
        border-radius: 15px 15px 15px 0;
        border-left: 3px solid #B026FF;
        font-family: 'Roboto', sans-serif;
        box-shadow: 0 0 10px rgba(176, 38, 255, 0.1);
        margin-bottom: 10px;
        border: 1px solid #333;
    }

    /* 8. BUTTONS */
    div.stButton > button {
        background: linear-gradient(90deg, #B026FF, #00F5FF);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        font-family: 'Orbitron', sans-serif;
        padding: 12px;
        text-shadow: 0 0 5px black;
        box-shadow: 0 0 15px rgba(176, 38, 255, 0.4);
        width: 100%;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 245, 255, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# --- API KEY ---
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # 👇👇👇 APNI KEY YAHAN DAALO 👇👇👇
    GOOGLE_API_KEY = "AIzaSy_YAHAN_TERI_ORIGINAL_KEY"

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    st.error("🚨 Nano-Link Offline. Check API Key.")

# --- SESSION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "chart_data" not in st.session_state: st.session_state.chart_data = None

# --- LOGIC ---
def get_lat_lon(city_name):
    if "chhindwara" in city_name.lower(): return 22.0574, 78.9382
    try:
        geo = Nominatim(user_agent="astromini_glow_v2")
        loc = geo.geocode(city_name, timeout=10)
        if loc: return loc.latitude, loc.longitude
        return None, None
    except: return None, None

def get_chart(dob, tob, lat, lon):
    obs = ephem.Observer(); obs.lat, obs.lon = str(lat), str(lon)
    obs.date = datetime.datetime.combine(dob, tob); ayanamsa = 23.86 
    planets = {
        "Sun ☀️": ephem.Sun(obs), "Moon 🌙": ephem.Moon(obs), 
        "Mars ♂️": ephem.Mars(obs), "Mercury ☿️": ephem.Mercury(obs), 
        "Jupiter ♃": ephem.Jupiter(obs), "Venus ♀️": ephem.Venus(obs), 
        "Saturn ♄": ephem.Saturn(obs)
    }
    signs = ["Aries ♈", "Taurus ♉", "Gemini ♊", "Cancer ♋", "Leo ♌", "Virgo ♍", "Libra ♎", "Scorpio ♏", "Sagittarius ♐", "Capricorn ♑", "Aquarius ♒", "Pisces ♓"]
    data = {}
    for p, obj in planets.items():
        l = (obj.hlon * 180 / 3.14159 - ayanamsa) % 360
        data[p] = {"sign": signs[int(l/30)], "deg": f"{l%30:.2f}°"}
    return data

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🕹️ Controls")
    lang = st.selectbox("Language", ["English", "Hindi", "Hinglish", "Spanish"])
    st.markdown("---")
    name = st.text_input("Username", "User")
    dob = st.date_input("Date Cycle", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time Cycle (24h)", value=datetime.time(23, 45))
    city = st.text_input("Location Node", "Chhindwara")
    st.markdown("---")
    style = st.select_slider("Density", options=["Nano ⚡", "Mega 📜"])
    persona = st.radio("AI Core", ["Cyber-Buddy 🤖", "Vedic Oracle 🧘"])
    st.markdown("<br>", unsafe_allow_html=True)
    btn = st.button("🚀 ACTIVATE SYSTEM")

# --- HEADER (LOGO + TITLE) ---
col1, col2 = st.columns([0.8, 5])
with col1:
    try: st.image("logo.png", width=120)
    except: st.markdown("# 👾")
with col2:
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='astromini-header'>ASTROMINI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>GLOBAL COSMIC INTELLIGENCE</p>", unsafe_allow_html=True)

# --- MAIN LOGIC ---
if btn and city:
    lat, lon = get_lat_lon(city)
    if lat:
        with st.spinner("📡 Uplink Established..."):
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] 
            
            sys = f"""
            Act as ASTROMINI. Lang: {lang}. Persona: {persona}. Format: {style}.
            User: {name}, {city}. Chart: {chart}
            1. Welcome {name}. 2. Moon Sign. 3. Insight. 4. Question?
            """
            st.session_state.messages.append({"role": "user", "content": sys})
            try:
                res = model.generate_content(sys)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except: st.error("Link Failed.")
    else: st.error("❌ Node Not Found.")

# --- CHART DISPLAY ---
if st.session_state.chart_data:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🪐 Planetary Data")
    items = list(st.session_state.chart_data.items())
    cols = st.columns(4)
    for i, (p, info) in enumerate(items):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="planet-card">
                <div class="planet-name">{p}</div>
                <div class="planet-sign">{info['sign']}</div>
                <div class="planet-deg">{info['deg']}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br><hr style='border-color: #00F5FF;'><br>", unsafe_allow_html=True)

# --- CHAT UI ---
st.markdown("### 💬 Neuro-Chat")
for m in st.session_state.messages:
    if m["role"] == "model":
        with st.chat_message("assistant", avatar="👾"): st.markdown(f"<div class='bot-msg'>{m['content']}</div>", unsafe_allow_html=True)
    elif m["role"] == "user" and "Act as" not in m["content"]:
        with st.chat_message("user", avatar="🧑‍🚀"): st.markdown(f"<div class='user-msg'>{m['content']}</div>", unsafe_allow_html=True)

if q := st.chat_input("Enter command..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user", avatar="🧑‍🚀"): st.markdown(f"<div class='user-msg'>{q}</div>", unsafe_allow_html=True)
    with st.chat_message("assistant", avatar="👾"):
        with st.spinner("Calculating..."):
            hist = [{"role": "user" if m["role"] in ["user","system"] else "model", "parts": [m["content"]]} for m in st.session_state.messages]
            try:
                res = model.start_chat(history=hist[:-1]).send_message(q)
                st.markdown(f"<div class='bot-msg'>{res.text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except: st.error("Error.")
