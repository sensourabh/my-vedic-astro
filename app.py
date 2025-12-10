import streamlit as st
import google.generativeai as genai
import datetime
import ephem
from geopy.geocoders import Nominatim

# --- PAGE SETUP ---
st.set_page_config(
    page_title="ASTROMINI", 
    page_icon="🔮", 
    layout="wide"
)

# --- API KEY SETUP ---
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # 👇👇👇 APNI KEY YAHAN DAALO 👇👇👇
    GOOGLE_API_KEY = "AIzaSy_YAHAN_TERI_ORIGINAL_KEY"

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("⚠️ API Key Error. Check connection.")

# --- SESSION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "chart_data" not in st.session_state: st.session_state.chart_data = None

# --- LOGIC ---
def get_lat_lon(city):
    # Manual fix for Chhindwara
    if "chhindwara" in city.lower(): return 22.0574, 78.9382
    try:
        geo = Nominatim(user_agent="astro_original_v1")
        loc = geo.geocode(city, timeout=5)
        if loc: return loc.latitude, loc.longitude
        return None, None
    except: return None, None

def get_chart(dob, tob, lat, lon):
    obs = ephem.Observer(); obs.lat, obs.lon = str(lat), str(lon)
    obs.date = datetime.datetime.combine(dob, tob); ayanamsa = 23.86 
    planets = {
        "Sun ☀️": ephem.Sun(obs), "Moon 🌙": ephem.Moon(obs), "Mars ♂️": ephem.Mars(obs),
        "Mercury ☿️": ephem.Mercury(obs), "Jupiter ♃": ephem.Jupiter(obs), 
        "Venus ♀️": ephem.Venus(obs), "Saturn ♄": ephem.Saturn(obs)
    }
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    data = {}
    for p, obj in planets.items():
        l = (obj.hlon * 180 / 3.14159 - ayanamsa) % 360
        data[p] = {"sign": signs[int(l/30)], "deg": f"{l%30:.2f}°"}
    return data

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔮 Settings")
    
    st.subheader("Birth Details")
    name = st.text_input("Name", "User")
    dob = st.date_input("Date of Birth", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time of Birth", value=datetime.time(23, 45))
    city = st.text_input("City", "Chhindwara")
    
    st.divider()
    
    st.subheader("Preferences")
    lang = st.selectbox("Language", ["English", "Hindi", "Hinglish"])
    persona = st.radio("Mode", ["Friend 🤖", "Guru 🧘"])
    style = st.radio("Format", ["Short Points", "Detailed"])
    
    st.write("")
    btn = st.button("Generate Horoscope", type="primary")

# --- MAIN UI ---
col1, col2 = st.columns([0.5, 5])
with col1:
    # Logo attempt
    try: st.image("logo.png", width=80)
    except: st.write("🔮")
with col2:
    st.title("ASTROMINI")
    st.caption("Simple & Accurate Vedic Astrology AI")

st.divider()

# --- MAIN LOGIC ---
if btn and city:
    lat, lon = get_lat_lon(city)
    if lat:
        with st.spinner("Calculating Chart..."):
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] 
            
            sys = f"""
            Act as ASTROMINI. Language: {lang}. Mode: {persona}. Format: {style}.
            User: {name}, {city}. Chart: {chart}
            1. Welcome {name}. 2. Moon Sign (Rashi). 3. Key Insight. 4. Ask for question.
            """
            st.session_state.messages.append({"role": "user", "content": sys})
            try:
                res = model.generate_content(sys)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except: st.error("Error connecting to AI.")
    else: st.error("City not found.")

# --- CHART GRID (Native Streamlit Metrics) ---
if st.session_state.chart_data:
    st.subheader("🪐 Planetary Positions")
    cols = st.columns(4)
    items = list(st.session_state.chart_data.items())
    for i, (p, info) in enumerate(items):
        with cols[i % 4]:
            st.metric(label=p, value=info['sign'], delta=info['deg'])
    st.divider()

# --- CHAT UI (Native Streamlit Chat) ---
st.subheader("💬 Chat")

for m in st.session_state.messages:
    if m["role"] == "model":
        with st.chat_message("assistant", avatar="🔮"):
            st.markdown(m["content"])
    elif m["role"] == "user" and "Act as" not in m["content"]:
        with st.chat_message("user", avatar="👤"):
            st.markdown(m["content"])

if q := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user", avatar="👤"):
        st.markdown(q)
    
    with st.chat_message("assistant", avatar="🔮"):
        with st.spinner("Thinking..."):
            hist = [{"role": "user" if m["role"] in ["user","system"] else "model", "parts": [m["content"]]} for m in st.session_state.messages]
            try:
                res = model.start_chat(history=hist[:-1]).send_message(q)
                st.markdown(res.text)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except: st.error("Error.")
