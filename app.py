import streamlit as st
import google.generativeai as genai
import datetime
import ephem
from geopy.geocoders import Nominatim

# --- PAGE SETUP ---
st.set_page_config(
    page_title="ASTROMINI Global", 
    page_icon="🌍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (GLOWING FONTS & GLOBAL THEME) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');
    
    /* Main Background */
    .stApp {
        background-color: #050505;
        background-image: linear-gradient(to bottom, #050505 0%, #0b1021 100%);
        color: #FFFFFF;
    }

    /* Input Fields */
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #121826 !important;
        color: #FFFFFF !important;
        font-family: 'Orbitron', sans-serif !important;
        border: 1px solid #00F5FF !important;
        border-radius: 8px;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }
    
    /* Dropdown Text Fix */
    div[data-baseweb="popover"] {
        background-color: #121826;
    }
    div[data-baseweb="menu"] {
        background-color: #121826;
        color: white;
    }

    /* Header Styles */
    .astromini-header {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(to right, #B026FF, #00F5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3.5rem;
        filter: drop-shadow(0 0 15px rgba(176, 38, 255, 0.6));
    }
    .sub-header {
        font-family: 'Orbitron', sans-serif;
        color: #FFFFFF;
        font-size: 1.2rem;
        letter-spacing: 4px;
        text-shadow: 0 0 10px #00F5FF;
        margin-top: -10px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid #B026FF;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        color: #00F5FF !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 5px rgba(0, 245, 255, 0.4);
    }

    /* Chat Bubbles */
    .user-msg { background: #1F2937; color: #fff; padding: 12px 18px; border-radius: 15px 15px 0 15px; border-right: 3px solid #00F5FF; font-family: 'Roboto', sans-serif; }
    .bot-msg { background: #111827; color: #E0E0E0; padding: 12px 18px; border-radius: 15px 15px 15px 0; border-left: 3px solid #B026FF; font-family: 'Roboto', sans-serif; border: 1px solid #333; }
    
    /* Button */
    div.stButton > button { background: linear-gradient(90deg, #B026FF, #00F5FF); color: white; border: none; border-radius: 8px; font-weight: bold; font-family: 'Orbitron', sans-serif; padding: 12px; }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(0, 245, 255, 0.6); }
    
    /* Planet Card */
    .planet-card { background: rgba(20, 25, 40, 0.7); border: 1px solid #00F5FF; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 0 15px rgba(0, 245, 255, 0.1); }
    .planet-name { color: #FFD700; font-family: 'Orbitron', sans-serif; font-size: 1.2rem; font-weight: bold; }
    .planet-sign { color: #FFFFFF; font-size: 1rem; }
    .planet-deg { color: #B026FF; font-family: monospace; }
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
    st.error("🚨 Nano-Link Offline. Check API Key.")

# --- SESSION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "chart_data" not in st.session_state: st.session_state.chart_data = None

# --- WORLDWIDE LOCATION FINDER ---
def get_lat_lon(city_name):
    # Special fix for Chhindwara (as per user request)
    if "chhindwara" in city_name.lower():
        return 22.0574, 78.9382
        
    try:
        # User agent is critical for global search
        geolocator = Nominatim(user_agent="astromini_global_v1")
        # Global search enabled
        loc = geolocator.geocode(city_name, timeout=10)
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

# --- SIDEBAR (INPUTS) ---
with st.sidebar:
    st.markdown("### 🌍 Global Settings")
    
    # 1. LANGUAGE SELECTION
    lang = st.selectbox("Select Language / भाषा", 
                        ["English", "Hindi (हिंदी)", "Hinglish", "Spanish", "French", "German", "Japanese"])
    
    st.markdown("---")
    st.markdown("### 👤 User Profile")
    name = st.text_input("Name", "User")
    dob = st.date_input("Date of Birth", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time of Birth", value=datetime.time(23, 45))
    
    # 2. WORLDWIDE CITY INPUT
    city = st.text_input("Birth City (e.g. London, Tokyo)", "Chhindwara")
    
    st.markdown("---")
    st.markdown("### ⚙️ Preferences")
    style = st.select_slider("Detail Level", options=["Quick ⚡", "Deep 📜"])
    persona = st.radio("AI Vibe", ["Cyber-Buddy 🤖", "Mystic Guru 🧘"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    btn = st.button("🚀 ACTIVATE SYSTEM")

# --- HEADER (LOGO) ---
col1, col2 = st.columns([1, 5])
with col1:
    try: st.image("logo.png", width=140)
    except: st.markdown("<h1 style='text-align:center;'>👾</h1>", unsafe_allow_html=True)
with col2:
    st.markdown("<div style='padding-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='astromini-header'>ASTROMINI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>GLOBAL COSMIC INTELLIGENCE</p>", unsafe_allow_html=True)

# --- MAIN LOGIC ---
if btn and city:
    lat, lon = get_lat_lon(city)
    if lat:
        with st.spinner(f"📡 Connecting to {city} coordinates..."):
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] 
            
            # Dynamic Prompting based on Language
            sys_msg = f"""
            Act as ASTROMINI, an advanced AI Astrologer.
            
            **SETTINGS:**
            - **Target Language:** {lang} (Strictly respond in this language).
            - **Persona:** {persona}
            - **Format:** {"Bullet points" if "Quick" in style else "Detailed paragraphs"}
            
            **USER DATA:**
            - Name: {name}
            - Location: {city} (Lat: {lat}, Lon: {lon})
            - Birth: {dob} at {tob}
            
            **CHART DATA (Vedic/Sidereal):**
            {chart}
            
            **INITIAL TASK:**
            1. Welcome {name} in {lang}.
            2. Tell them their Moon Sign (Rashi) clearly.
            3. Give a specific personality insight based on the chart.
            4. Ask what they want to know (Love, Career, Future).
            """
            
            st.session_state.messages.append({"role": "user", "content": sys_msg})
            try:
                res = model.generate_content(sys_msg)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except:
                st.error("⚡ System Failure: API connection lost.")
    else:
        st.error(f"❌ Could not find '{city}'. Try adding the country name (e.g., '{city}, Country').")

# --- DISPLAY CHART ---
if st.session_state.chart_data:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-header'>🪐 Planetary Data</h3>", unsafe_allow_html=True)
    items = list(st.session_state.chart_data.items())
    row1 = st.columns(4); row2 = st.columns(3)
    for i in range(4):
        p, info = items[i]
        with row1[i]: st.markdown(f"""<div class="planet-card"><div class="planet-name">{p}</div><div class="planet-sign">{info['sign']}</div><div class="planet-deg">{info['deg']}</div></div>""", unsafe_allow_html=True)
    for i in range(4, 7):
        p, info = items[i]
        with row2[i-4]: st.markdown(f"""<div class="planet-card"><div class="planet-name">{p}</div><div class="planet-sign">{info['sign']}</div><div class="planet-deg">{info['deg']}</div></div>""", unsafe_allow_html=True)
    st.markdown("<br><hr style='border-color: #00F5FF;'><br>", unsafe_allow_html=True)

# --- CHAT UI ---
st.markdown("<h3 class='sub-header'>💬 Neuro-Link Chat</h3>", unsafe_allow_html=True)

for m in st.session_state.messages:
    if m["role"] == "model":
        with st.chat_message("assistant", avatar="👾"): st.markdown(f"<div class='bot-msg'>{m['content']}</div>", unsafe_allow_html=True)
    elif m["role"] == "user" and "Act as" not in m["content"]:
        with st.chat_message("user", avatar="🧑‍🚀"): st.markdown(f"<div class='user-msg'>{m['content']}</div>", unsafe_allow_html=True)

if q := st.chat_input("Input command..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user", avatar="🧑‍🚀"): st.markdown(f"<div class='user-msg'>{q}</div>", unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="👾"):
        with st.spinner("PROCESSING..."):
            hist = [{"role": "user" if m["role"] in ["user","system"] else "model", "parts": [m["content"]]} for m in st.session_state.messages]
            try:
                res = model.start_chat(history=hist[:-1]).send_message(q)
                st.markdown(f"<div class='bot-msg'>{res.text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except: st.error("Connection Error.")
