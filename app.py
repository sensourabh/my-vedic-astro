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

# --- CUSTOM CSS (DARK MODE & FONT FIX) ---
st.markdown("""
<style>
    /* 1. New Fonts: Orbitron (Headers) & Exo 2 (Body Text) */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Exo+2:wght@300;400;600&display=swap');
    
    /* 2. Remove Top/Bottom White Space (Padding Fix) */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* 3. Main Background */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 20% 50%, #0d121f 0%, #000000 100%);
        color: #E0E0E0;
        font-family: 'Exo 2', sans-serif; /* Readable Font */
    }

    /* 4. Input Fields (Darker, No White Background) */
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0E121A !important; /* Deep Dark Blue/Grey */
        color: #00F5FF !important; /* Cyan Text */
        font-family: 'Exo 2', sans-serif !important;
        font-weight: 600;
        border: 1px solid #333 !important;
        border-radius: 8px;
    }
    /* Focus Effect on Inputs */
    .stTextInput input:focus, .stDateInput input:focus {
        border-color: #00F5FF !important;
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.2);
    }
    
    /* Dropdown Menu Fix */
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #0E121A;
        border: 1px solid #333;
    }
    div[data-baseweb="option"] {
        color: #E0E0E0;
    }

    /* 5. Typography (Headers) */
    .astromini-header {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #FFFFFF, #00F5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        letter-spacing: 2px;
        margin-bottom: 0;
    }
    .sub-header {
        font-family: 'Exo 2', sans-serif;
        color: #888888;
        font-size: 1rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-top: -5px;
    }
    
    /* 6. Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #080a0f;
        border-right: 1px solid #222;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #00F5FF !important;
        font-family: 'Orbitron', sans-serif !important;
    }

    /* 7. Chat Bubbles (Clean Left Alignment) */
    .user-msg { 
        background: #1A1F2E; 
        color: #E0E0E0; 
        padding: 12px 16px; 
        border-radius: 12px; 
        border-left: 4px solid #00F5FF; 
        font-family: 'Exo 2', sans-serif; 
        margin-bottom: 8px;
    }
    .bot-msg { 
        background: #0E121A; 
        color: #B0C4DE; 
        padding: 12px 16px; 
        border-radius: 12px; 
        border: 1px solid #333; 
        font-family: 'Exo 2', sans-serif; 
        margin-bottom: 8px;
    }
    
    /* 8. Buttons */
    div.stButton > button { 
        background: linear-gradient(90deg, #00F5FF, #0099FF); 
        color: #000; 
        border: none; 
        border-radius: 6px; 
        font-weight: bold; 
        font-family: 'Orbitron', sans-serif; 
        padding: 0.75rem 1rem;
        transition: 0.3s;
    }
    div.stButton > button:hover { 
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.5); 
        color: white;
    }
    
    /* 9. Planet Card */
    .planet-card { 
        background: #0E121A; 
        border: 1px solid #222; 
        border-radius: 10px; 
        padding: 15px; 
        text-align: left; /* Left Aligned as requested */
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .planet-name { color: #FFFFFF; font-family: 'Orbitron', sans-serif; font-size: 1.1rem; font-weight: 600; }
    .planet-sign { color: #00F5FF; font-family: 'Exo 2', sans-serif; font-size: 0.95rem; }
    .planet-deg { color: #666; font-family: monospace; font-size: 0.8rem; }
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
    if "chhindwara" in city_name.lower():
        return 22.0574, 78.9382
    try:
        geolocator = Nominatim(user_agent="astromini_global_v2")
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
        "Sun": ephem.Sun(obs), "Moon": ephem.Moon(obs), 
        "Mars": ephem.Mars(obs), "Mercury": ephem.Mercury(obs), 
        "Jupiter": ephem.Jupiter(obs), "Venus": ephem.Venus(obs), 
        "Saturn": ephem.Saturn(obs)
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
    st.markdown("### 🌍 SETTINGS")
    lang = st.selectbox("Language", 
                        ["English", "Hindi (हिंदी)", "Hinglish", "Spanish", "French"])
    
    st.markdown("---")
    st.markdown("### 👤 PROFILE")
    name = st.text_input("Username", "User")
    dob = st.date_input("Birth Date", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Birth Time", value=datetime.time(23, 45))
    city = st.text_input("Location", "Chhindwara")
    
    st.markdown("---")
    style = st.select_slider("Format", options=["Short ⚡", "Deep 📜"])
    persona = st.radio("Mode", ["Cyber-Buddy 🤖", "Mystic Guru 🧘"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    btn = st.button("🚀 INITIATE SCAN")

# --- HEADER (Aligned Left) ---
col1, col2 = st.columns([0.8, 5])
with col1:
    try: st.image("logo.png", width=100)
    except: st.markdown("## 👾")
with col2:
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
            
            sys_msg = f"""
            Act as ASTROMINI. Language: {lang}. Persona: {persona}. Format: {"Bullet points" if "Short" in style else "Detailed"}.
            User: {name}, {city}.
            Chart: {chart}
            1. Welcome {name} in {lang}.
            2. State Moon Sign.
            3. Personality insight.
            4. Ask for question.
            """
            st.session_state.messages.append({"role": "user", "content": sys_msg})
            try:
                res = model.generate_content(sys_msg)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except:
                st.error("⚡ System Failure.")
    else:
        st.error(f"❌ '{city}' Not Found.")

# --- DISPLAY CHART (Clean List) ---
if st.session_state.chart_data:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 🪐 PLANETARY DATA")
    items = list(st.session_state.chart_data.items())
    
    # 4 Columns for better space usage
    cols = st.columns(4)
    for i, (p, info) in enumerate(items):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="planet-card">
                <div>
                    <div class="planet-name">{p}</div>
                    <div class="planet-deg">{info['deg']}</div>
                </div>
                <div class="planet-sign">{info['sign']}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)

# --- CHAT UI ---
st.markdown("##### 💬 NEURO-LINK CHAT")

for m in st.session_state.messages:
    if m["role"] == "model":
        with st.chat_message("assistant", avatar="👾"): st.markdown(f"<div class='bot-msg'>{m['content']}</div>", unsafe_allow_html=True)
    elif m["role"] == "user" and "Act as" not in m["content"]:
        with st.chat_message("user", avatar="🧑‍🚀"): st.markdown(f"<div class='user-msg'>{m['content']}</div>", unsafe_allow_html=True)

if q := st.chat_input("Enter your query..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user", avatar="🧑‍🚀"): st.markdown(f"<div class='user-msg'>{q}</div>", unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="👾"):
        with st.spinner("Analyzing..."):
            hist = [{"role": "user" if m["role"] in ["user","system"] else "model", "parts": [m["content"]]} for m in st.session_state.messages]
            try:
                res = model.start_chat(history=hist[:-1]).send_message(q)
                st.markdown(f"<div class='bot-msg'>{res.text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except: st.error("Error.")
