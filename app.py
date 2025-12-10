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

# --- CUSTOM CSS (MATCHING YOUR LOGO 🎨) ---
st.markdown("""
<style>
    /* Import modern font - Orbitron for sci-fi feel */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');

    /* Main Background - Deep Space matching logo background */
    .stApp {
        background-color: #0A0E14;
        background-image: radial-gradient(circle at 50% 30%, #1a1f2c 0%, #0A0E14 80%);
        color: #E0E0E0;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111620;
        border-right: 1px solid #B026FF; /* Neon Purple from logo */
    }
    
    /* ASTROMINI Header Style - Gradient matching the energy flow */
    .astromini-header {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(to right, #B026FF, #00F5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3.5rem;
        text-shadow: 0 0 15px rgba(176, 38, 255, 0.6);
        margin-bottom: 0px;
    }
    .sub-header {
        color: #00F5FF; /* Neon Blue */
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1.5px;
        font-size: 1.1rem;
        margin-top: -10px;
    }
    
    /* Cyber Planet Cards (Grid) - Glassmorphism aesthetic */
    .planet-card {
        background: rgba(16, 20, 30, 0.8);
        border: 1px solid #00F5FF; /* Neon Blue Border */
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.15);
        transition: all 0.4s ease-in-out;
    }
    .planet-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 0 30px rgba(176, 38, 255, 0.5);
        border-color: #B026FF; /* Glow turns purple on hover */
    }
    .planet-name {
        color: #FFFFFF;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    .planet-sign {
        color: #00F5FF;
        font-size: 1.1rem;
        font-weight: 500;
    }
    .planet-deg {
        color: #B026FF;
        font-size: 0.9rem;
        font-family: monospace;
        opacity: 0.8;
    }

    /* Chat Messages (Modern Bubbles) */
    .user-msg {
        background: linear-gradient(135deg, #2b313e, #1c222d);
        padding: 12px 18px;
        border-radius: 18px 18px 2px 18px;
        border-right: 4px solid #00F5FF; /* Blue accent */
        margin: 10px 0;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
    }
    .bot-msg {
        background: linear-gradient(135deg, #1c222d, #111620);
        padding: 12px 18px;
        border-radius: 18px 18px 18px 2px;
        border-left: 4px solid #B026FF; /* Purple accent */
        margin: 10px 0;
        box-shadow: -4px 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Button Styling (Neon Glow Gradient) */
    div.stButton > button {
        background: linear-gradient(90deg, #B026FF, #00F5FF);
        color: white;
        border: none;
        border-radius: 30px;
        font-weight: 700;
        width: 100%;
        padding: 14px;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
        text-transform: uppercase;
        box-shadow: 0 0 20px rgba(176, 38, 255, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 35px rgba(0, 245, 255, 0.7);
        transform: scale(1.03);
        background: linear-gradient(90deg, #00F5FF, #B026FF); /* Reverse gradient on hover */
    }
    
    /* Sidebar Input Styling to match theme */
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectSlider div[data-baseweb="slider"] {
        background-color: #0A0E14 !important;
        color: #00F5FF !important;
        border: 1px solid #B026FF !important;
        border-radius: 8px;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
         color: #B026FF !important;
         font-family: 'Orbitron', sans-serif;
    }
    
</style>
""", unsafe_allow_html=True)

# --- API KEY SETUP ---
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # 👇👇👇 APNI KEY YAHAN DAALO 👇👇👇
    GOOGLE_API_KEY = "AIzaSy_YAHAN_TERI_ORIGINAL_KEY"

# --- AI CONNECT ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("🚨 Nano-Link Offline. Check API Key.")

# --- SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None

# --- HELPERS ---
def get_lat_lon(city_name):
    try:
        geolocator = Nominatim(user_agent="astromini_bot_v4")
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
    st.markdown("### 🕹️ Initialize Deck")
    
    name = st.text_input("Username", "User")
    dob = st.date_input("Date Cycle", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time Cycle (24h)", value=datetime.time(23, 45))
    city = st.text_input("Location Node", "Chhindwara")
    
    st.markdown("---")
    st.markdown("### ⚙️ Protocols")
    style = st.select_slider("Data Density", options=["Nano ⚡", "Mega 📜"])
    persona = st.radio("AI Personality", ["Cyber-Buddy 🤖", "Vedic Oracle 🧘"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    btn = st.button("🚀 ACTIVATE ASTROMINI")

# --- MAIN AREA HEADER (LOGO INTEGRATED) ---
col1, col2 = st.columns([1, 5])
with col1:
    # ✅ YAHAN LOGO LAGEGA
    # Make sure 'logo.png' is in the same folder as app.py
    try:
        st.image("logo.png", width=130)
    except:
        # Agar logo file nahi mili toh ye dikhega
        st.markdown("<div style='font-size: 4rem; text-align: center;'>👾</div>", unsafe_allow_html=True)
        st.caption("Save logo.png in folder")

with col2:
    # Title text alignment fix
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='astromini-header'>ASTROMINI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Pocket-Sized Cosmic Intelligence</p>", unsafe_allow_html=True)


# LOGIC
if btn and city:
    lat, lon = get_lat_lon(city)
    if lat:
        with st.spinner("📡 Establishing uplink to celestial data..."):
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] 
            
            tone = "Tech-savvy, Hinglish, slang, Emojis like 🤖🚀" if "Cyber" in persona else "Mystical, deep, Sanskrit terms, respectful"
            fmt = "Bullet points, sharp, concise" if "Nano" in style else "Detailed analysis, descriptive paragraphs"
            
            sys_msg = f"""
            Act as ASTROMINI, an advanced AI Vedic Astrologer. 
            **Tone:** {tone}
            **Format:** {fmt}
            
            **USER DATA:**
            Name: {name}
            Birth Details: {dob} at {tob} in {city} (Lat: {lat}, Lon: {lon})
            
            **CALCULATED VEDIC CHART:**
            {chart}
            
            **INITIAL PROTOCOL:**
            1. Welcome {name} to the ASTROMINI interface.
            2. Confirm their 'Moon Node' (Rashi) based on the chart data.
            3. Process a quick, powerful insight about their core programming (personality).
            4. Prompt for next directive (Career DB, Love module, etc.).
            """
            
            st.session_state.messages.append({"role": "user", "content": sys_msg})
            try:
                res = model.generate_content(sys_msg)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except:
                st.error("⚡ System Failure: API connection lost.")
    else:
        st.error("❌ Location Node not found.")

# --- DISPLAY CHART (CYBER GRID) ---
if st.session_state.chart_data:
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-header'>🪐 Planetary Data Blocks</h3>", unsafe_allow_html=True)
    
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
            </div>
            """, unsafe_allow_html=True)
            
    for i in range(4, 7):
        p, info = items[i]
        with row2[i-4]:
            st.markdown(f"""
            <div class="planet-card">
                <div class="planet-name">{p}</div>
                <div class="planet-sign">{info['sign']}</div>
                <div class="planet-deg">{info['deg']}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br><hr><br>", unsafe_allow_html=True)

# --- CHAT UI (MODERN BUBBLES) ---
st.markdown("<h3 class='sub-header'>💬 Neuro-Link Chat</h3>", unsafe_allow_html=True)

for m in st.session_state.messages:
    if m["role"] == "model":
        # Bot Avatar: Logo use kar sakte hain ya emoji
        with st.chat_message("assistant", avatar="👾"):
            st.markdown(f"<div class='bot-msg'>{m['content']}</div>", unsafe_allow_html=True)
    elif m["role"] == "user" and "Act as ASTROMINI" not in m["content"]:
        with st.chat_message("user", avatar="🧑‍🚀"):
            st.markdown(f"<div class='user-msg'>{m['content']}</div>", unsafe_allow_html=True)

if q := st.chat_input("Input command..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(f"<div class='user-msg'>{q}</div>", unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="👾"):
        with st.spinner("PROCESSING..."):
            history_ai = []
            for m in st.session_state.messages:
                role = "user" if m["role"] in ["user", "system"] else "model"
                history_ai.append({"role": role, "parts": [m["content"]]})
            
            try:
                chat = model.start_chat(history=history_ai[:-1])
                response = chat.send_message(q)
                st.markdown(f"<div class='bot-msg'>{response.text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except:
                st.error("⚡ Connection interrupted.")
