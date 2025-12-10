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

# --- VISIBILITY FIX CSS (Clean & Neon) ---
st.markdown("""
<style>
    /* 1. Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');

    /* 2. Main Background */
    .stApp {
        background-color: #050505;
        background-image: linear-gradient(to bottom, #050505, #0a0f1e);
        color: #FFFFFF; /* Default Text White */
        font-family: 'Roboto', sans-serif;
    }
    
    /* 3. Headers (Title) - Solid Colors instead of Transparent Gradient */
    .astromini-header {
        font-family: 'Orbitron', sans-serif;
        color: #00F5FF; /* Electric Blue */
        font-weight: 700;
        font-size: 3.5rem;
        text-align: left;
        margin-bottom: 0px;
        text-shadow: 0px 0px 15px rgba(0, 245, 255, 0.8); /* Glow Effect */
    }
    
    .sub-header {
        font-family: 'Orbitron', sans-serif;
        color: #B026FF; /* Neon Purple */
        font-size: 1.2rem;
        letter-spacing: 2px;
        margin-top: -10px;
        text-shadow: 0px 0px 10px rgba(176, 38, 255, 0.6);
    }
    
    /* 4. Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 2px solid #00F5FF;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #00F5FF !important; /* Force Blue Headers */
        font-family: 'Orbitron', sans-serif !important;
    }
    
    /* 5. Inputs (Text Boxes) Visibility Fix */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #1c1f26 !important;
        color: #FFFFFF !important; /* Bright White Text */
        border: 1px solid #B026FF !important;
    }
    .stSelectSlider div[data-baseweb="slider"] p {
        color: #FFFFFF !important;
    }

    /* 6. Planet Cards */
    .planet-card {
        background: #111620;
        border: 1px solid #00F5FF;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.2);
    }
    .planet-name {
        color: #FFD700; /* Gold for Planet Names */
        font-family: 'Orbitron', sans-serif;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .planet-sign {
        color: #FFFFFF; /* White for Sign */
        font-size: 1.1rem;
        margin: 5px 0;
    }
    .planet-deg {
        color: #00F5FF; /* Blue for Degrees */
        font-family: monospace;
    }

    /* 7. Chat Bubbles */
    .user-msg {
        background-color: #262730;
        color: #FFFFFF;
        padding: 10px 15px;
        border-radius: 15px;
        border-left: 5px solid #FFD700; /* Yellow bar */
        margin: 5px 0;
    }
    .bot-msg {
        background-color: #0E1117;
        color: #E0E0E0;
        padding: 10px 15px;
        border-radius: 15px;
        border-left: 5px solid #00F5FF; /* Blue bar */
        border: 1px solid #333;
        margin: 5px 0;
    }

    /* 8. Buttons */
    div.stButton > button {
        background-color: #00F5FF;
        color: black;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        border-radius: 5px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #B026FF;
        color: white;
    }

</style>
""", unsafe_allow_html=True)

# --- API KEY SETUP ---
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # 👇👇👇 YAHAN APNI KEY DAALNA MAT BHOOLNA 👇👇👇
    GOOGLE_API_KEY = "AIzaSy_YAHAN_TERI_ORIGINAL_KEY"

# --- AI CONNECT ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("🚨 Connection Error. Check API Key.")

# --- SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None

# --- HELPERS ---
def get_lat_lon(city_name):
    try:
        geolocator = Nominatim(user_agent="astromini_bot_fixed")
        loc = geolocator.geocode(city_name)
        if loc: return loc.latitude, loc.longitude
        return None, None
    except:
        return None, None

def get_chart(dob, tob, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = datetime.datetime.combine(dob, tob)
    ayanamsa = 23.86 
    
    planets = {
        "Sun ☀️": ephem.Sun(obs), "Moon 🌙": ephem.Moon(obs), 
        "Mars ♂️": ephem.Mars(obs), "Mercury ☿️": ephem.Mercury(obs), 
        "Jupiter ♃": ephem.Jupiter(obs), "Venus ♀️": ephem.Venus(obs), 
        "Saturn ♄": ephem.Saturn(obs)
    }
    signs = ["Aries ♈", "Taurus ♉", "Gemini ♊", "Cancer ♋", "Leo ♌", "Virgo ♍", 
             "Libra ♎", "Scorpio ♏", "Sagittarius ♐", "Capricorn ♑", "Aquarius ♒", "Pisces ♓"]
    
    data = {}
    for p, obj in planets.items():
        l = (obj.hlon * 180 / 3.14159 - ayanamsa) % 360
        data[p] = {"sign": signs[int(l/30)], "deg": f"{l%30:.2f}°"}
    return data

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🕹️ User Controls")
    
    name = st.text_input("Name", "User")
    dob = st.date_input("Date", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time", value=datetime.time(23, 45))
    city = st.text_input("City", "Chhindwara")
    
    st.markdown("---")
    style = st.select_slider("Response Type", options=["Short ⚡", "Detailed 📜"])
    persona = st.radio("AI Persona", ["Cyber-Buddy 🤖", "Vedic Oracle 🧘"])
    
    btn = st.button("🚀 LAUNCH SYSTEM")

# --- HEADER SECTION ---
col1, col2 = st.columns([1, 5])
with col1:
    # Logo Display Logic
    try:
        st.image("logo.png", width=120)
    except:
        st.markdown("# 👾") # Fallback if logo missing

with col2:
    st.markdown("<h1 class='astromini-header'>ASTROMINI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>NEURO-LINKED ASTROLOGY</p>", unsafe_allow_html=True)

# --- MAIN LOGIC ---
if btn and city:
    lat, lon = get_lat_lon(city)
    if lat:
        with st.spinner("🔄 Processing Cosmic Data..."):
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] 
            
            tone = "Tech-savvy, Hinglish, Cool" if "Cyber" in persona else "Deep, Spiritual, Hindi/English"
            fmt = "Bullet points" if "Short" in style else "Detailed analysis"
            
            sys_msg = f"""
            Act as ASTROMINI (AI Astrologer). Tone: {tone}. Format: {fmt}.
            User: {name}. Location: {city}.
            Chart: {chart}
            
            1. Welcome {name}.
            2. State their Moon Sign (Rashi).
            3. Give a powerful insight about their nature.
            4. Ask what they want to know (Love/Career).
            """
            
            st.session_state.messages.append({"role": "user", "content": sys_msg})
            try:
                res = model.generate_content(sys_msg)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except:
                st.error("System Error: Check API.")
    else:
        st.error("❌ City Not Found.")

# --- PLANET GRID ---
if st.session_state.chart_data:
    st.markdown("---")
    st.markdown("### 🪐 Planetary Coordinates")
    data = st.session_state.chart_data
    items = list(data.items())
    
    row1 = st.columns(4)
    row2 = st.columns(3)
    
    for i in range(4):
        p, info = items[i]
        with row1[i]:
            st.markdown(f"""
            <div class="planet-card">
                <div class="planet-name">{p}</div>
                <div class="planet-sign">{info['sign']}</div>
                <div class="planet-deg">{info['deg']}</div>
            </div>""", unsafe_allow_html=True)
            
    for i in range(4, 7):
        p, info = items[i]
        with row2[i-4]:
            st.markdown(f"""
            <div class="planet-card">
                <div class="planet-name">{p}</div>
                <div class="planet-sign">{info['sign']}</div>
                <div class="planet-deg">{info['deg']}</div>
            </div>""", unsafe_allow_html=True)

# --- CHAT AREA ---
st.markdown("---")
st.markdown("### 💬 Data Uplink")

for m in st.session_state.messages:
    if m["role"] == "model":
        with st.chat_message("assistant", avatar="👾"):
            st.markdown(f"<div class='bot-msg'>{m['content']}</div>", unsafe_allow_html=True)
    elif m["role"] == "user" and "Act as" not in m["content"]:
        with st.chat_message("user", avatar="🧑‍🚀"):
            st.markdown(f"<div class='user-msg'>{m['content']}</div>", unsafe_allow_html=True)

if q := st.chat_input("Enter query..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(f"<div class='user-msg'>{q}</div>", unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="👾"):
        with st.spinner("Calculating..."):
            history_ai = [{"role": "user" if m["role"] in ["user", "system"] else "model", "parts": [m["content"]]} for m in st.session_state.messages]
            try:
                chat = model.start_chat(history=history_ai[:-1])
                res = chat.send_message(q)
                st.markdown(f"<div class='bot-msg'>{res.text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except:
                st.error("Error.")
