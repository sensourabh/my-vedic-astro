import streamlit as st
import google.generativeai as genai
import datetime
import ephem
from geopy.geocoders import Nominatim

# --- PAGE SETUP ---
st.set_page_config(
    page_title="ASTROMINI", 
    page_icon="🌌", 
    layout="wide"
)

# --- MINIMALIST CSS (CLEAN & READABLE) ---
st.markdown("""
<style>
    /* 1. Main Background - Solid Dark Grey */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: sans-serif;
    }

    /* 2. INPUT FIELDS - High Contrast (White Bg, Black Text) */
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 4px;
    }
    
    /* Dropdown Text Color Fix */
    div[data-baseweb="popover"], div[data-baseweb="menu"], div[data-baseweb="option"] {
        color: black;
    }

    /* 3. SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }

    /* 4. PLANET GRID (Simple Cards) */
    .planet-box {
        background-color: #1C2128;
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 10px;
    }
    .p-name { color: #58A6FF; font-weight: bold; font-size: 1.1em; } /* Blue */
    .p-sign { color: #FFFFFF; font-size: 1em; margin-top: 5px;}
    .p-deg { color: #8B949E; font-size: 0.8em; font-family: monospace; }

    /* 5. CHAT MESSAGES */
    .user-msg {
        background-color: #238636; /* Green */
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        text-align: right;
    }
    .bot-msg {
        background-color: #161B22; /* Dark Grey */
        color: #E6EDF3;
        padding: 10px 15px;
        border-radius: 8px;
        border: 1px solid #30363D;
        margin-bottom: 10px;
    }

    /* 6. BUTTON */
    div.stButton > button {
        background-color: #1F6FEB; /* Professional Blue */
        color: white;
        border: none;
        padding: 10px;
        border-radius: 4px;
        font-weight: 600;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #1A5CB8;
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
    st.warning("⚠️ API Key not found.")

# --- SESSION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "chart_data" not in st.session_state: st.session_state.chart_data = None

# --- LOGIC ---
def get_lat_lon(city):
    if "chhindwara" in city.lower(): return 22.0574, 78.9382
    try:
        geo = Nominatim(user_agent="astro_simple_v2")
        loc = geo.geocode(city, timeout=5)
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
    st.header("⚙️ Settings")
    lang = st.selectbox("Language", ["English", "Hindi", "Hinglish", "Spanish"])
    st.divider()
    
    st.header("👤 Profile")
    name = st.text_input("Name", "User")
    dob = st.date_input("Date of Birth", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time of Birth", value=datetime.time(23, 45))
    city = st.text_input("City", "Chhindwara")
    st.divider()
    
    persona = st.radio("Mode", ["Friend 🤖", "Guru 🧘"])
    st.write("")
    btn = st.button("Generate Horoscope")

# --- HEADER (Simple & Aligned) ---
col1, col2 = st.columns([0.5, 5])
with col1:
    try: st.image("logo.png", width=80)
    except: st.header("🌌")
with col2:
    st.markdown("<h1 style='margin:0; color: #58A6FF;'>ASTROMINI</h1>", unsafe_allow_html=True)
    st.markdown("<span style='color: #8B949E; letter-spacing: 1px;'>GLOBAL ASTROLOGY AI</span>", unsafe_allow_html=True)

# --- MAIN LOGIC ---
if btn and city:
    lat, lon = get_lat_lon(city)
    if lat:
        with st.spinner("Analyzing..."):
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] 
            
            sys = f"""
            Act as ASTROMINI. Lang: {lang}. Mode: {persona}.
            User: {name}, {city}. Chart: {chart}
            1. Welcome {name}. 2. State Moon Sign. 3. Insight. 4. Ask for question.
            """
            st.session_state.messages.append({"role": "user", "content": sys})
            try:
                res = model.generate_content(sys)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except: st.error("Error connecting.")
    else: st.error("City not found.")

# --- CHART GRID ---
if st.session_state.chart_data:
    st.write("")
    st.markdown("##### 🪐 Planetary Positions")
    items = list(st.session_state.chart_data.items())
    cols = st.columns(4)
    for i, (p, info) in enumerate(items):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="planet-box">
                <div class="p-name">{p}</div>
                <div class="p-sign">{info['sign']}</div>
                <div class="p-deg">{info['deg']}</div>
            </div>""", unsafe_allow_html=True)
    st.divider()

# --- CHAT ---
st.markdown("##### 💬 Chat")
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
