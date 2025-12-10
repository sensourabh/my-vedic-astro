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

# --- SIMPLE & CLEAN CSS (HIGH VISIBILITY) ---
st.markdown("""
<style>
    /* 1. Main Background - Clean Dark Blue */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
        font-family: sans-serif;
    }

    /* 2. INPUT BOXES (White Background + Black Text) - Sabse Zaroori Fix */
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important; /* Pure White */
        color: #000000 !important; /* Pitch Black Text */
        border: 1px solid #4B5563 !important;
        border-radius: 5px;
    }
    
    /* Dropdown Menu Text Fix */
    div[data-baseweb="popover"], div[data-baseweb="menu"], div[data-baseweb="option"] {
        color: black;
    }

    /* 3. Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, label {
        color: #FFFFFF !important;
    }

    /* 4. HEADERS - Simple & Bold */
    .astromini-header {
        color: #58A6FF; /* Professional Blue */
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0;
    }
    .sub-header {
        color: #8B949E;
        font-size: 1.1rem;
        margin-top: -5px;
        letter-spacing: 2px;
    }

    /* 5. PLANET CARDS (Clean Grid) */
    .planet-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
    }
    .planet-name {
        color: #FFD700; /* Gold */
        font-weight: bold;
        font-size: 1.1rem;
    }
    .planet-sign {
        color: #FFFFFF;
        font-size: 1rem;
    }
    .planet-deg {
        color: #58A6FF; /* Blue */
        font-size: 0.8rem;
        font-family: monospace;
    }

    /* 6. CHAT BUBBLES (WhatsApp Style Dark) */
    .user-msg {
        background-color: #054740; /* WhatsApp Greenish Dark */
        color: #fff;
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 8px;
        text-align: right;
    }
    .bot-msg {
        background-color: #1F2937; /* Dark Grey */
        color: #E0E0E0;
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #333;
    }

    /* 7. BUTTON */
    div.stButton > button {
        background-color: #238636; /* GitHub Green */
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: bold;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #2EA043;
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
except Exception as e:
    st.error("⚠️ API Key Error")

# --- SESSION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "chart_data" not in st.session_state: st.session_state.chart_data = None

# --- LOCATION FINDER ---
def get_lat_lon(city_name):
    if "chhindwara" in city_name.lower(): return 22.0574, 78.9382
    try:
        geolocator = Nominatim(user_agent="astro_simple_v1")
        loc = geolocator.geocode(city_name, timeout=10)
        if loc: return loc.latitude, loc.longitude
        return None, None
    except: return None, None

def get_chart(dob, tob, lat, lon):
    obs = ephem.Observer(); obs.lat, obs.lon = str(lat), str(lon)
    obs.date = datetime.datetime.combine(dob, tob); ayanamsa = 23.86 
    planets = {
        "Sun": ephem.Sun(obs), "Moon": ephem.Moon(obs), "Mars": ephem.Mars(obs),
        "Mercury": ephem.Mercury(obs), "Jupiter": ephem.Jupiter(obs), 
        "Venus": ephem.Venus(obs), "Saturn": ephem.Saturn(obs)
    }
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    data = {}
    for p, obj in planets.items():
        l = (obj.hlon * 180 / 3.14159 - ayanamsa) % 360
        data[p] = {"sign": signs[int(l/30)], "deg": f"{l%30:.2f}°"}
    return data

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    lang = st.selectbox("Language", ["English", "Hindi", "Hinglish", "Spanish"])
    st.markdown("---")
    st.markdown("### 👤 Profile")
    name = st.text_input("Your Name", "User")
    dob = st.date_input("Date of Birth", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time of Birth", value=datetime.time(23, 45))
    city = st.text_input("City", "Chhindwara")
    st.markdown("---")
    persona = st.radio("Mode", ["Friend 🤖", "Guru 🧘"])
    st.markdown("<br>", unsafe_allow_html=True)
    btn = st.button("Generate Horoscope")

# --- HEADER ---
col1, col2 = st.columns([0.8, 5])
with col1:
    try: st.image("logo.png", width=100)
    except: st.header("🌌")
with col2:
    st.markdown("<h1 class='astromini-header'>ASTROMINI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>GLOBAL ASTROLOGY AI</p>", unsafe_allow_html=True)

# --- MAIN LOGIC ---
if btn and city:
    lat, lon = get_lat_lon(city)
    if lat:
        with st.spinner("Analyzing..."):
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] 
            
            sys_msg = f"""
            Act as ASTROMINI. Language: {lang}. Persona: {persona}.
            User: {name}, {city}. Chart: {chart}
            1. Welcome {name}. 2. State Moon Sign. 3. Insight. 4. Ask for question.
            """
            st.session_state.messages.append({"role": "user", "content": sys_msg})
            try:
                res = model.generate_content(sys_msg)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except: st.error("Error connecting to AI.")
    else: st.error("City not found.")

# --- CHART DISPLAY ---
if st.session_state.chart_data:
    st.markdown("<br><h5>🪐 Planetary Positions</h5>", unsafe_allow_html=True)
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
    st.markdown("<hr>")

# --- CHAT ---
st.markdown("<h5>💬 Chat</h5>", unsafe_allow_html=True)
for m in st.session_state.messages:
    if m["role"] == "model":
        with st.chat_message("assistant"): st.markdown(f"<div class='bot-msg'>{m['content']}</div>", unsafe_allow_html=True)
    elif m["role"] == "user" and "Act as" not in m["content"]:
        with st.chat_message("user"): st.markdown(f"<div class='user-msg'>{m['content']}</div>", unsafe_allow_html=True)

if q := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"): st.markdown(f"<div class='user-msg'>{q}</div>", unsafe_allow_html=True)
    with st.chat_message("assistant"):
        with st.spinner("Typing..."):
            hist = [{"role": "user" if m["role"] in ["user","system"] else "model", "parts": [m["content"]]} for m in st.session_state.messages]
            try:
                res = model.start_chat(history=hist[:-1]).send_message(q)
                st.markdown(f"<div class='bot-msg'>{res.text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except: st.error("Error.")
