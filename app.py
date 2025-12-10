import streamlit as st
import google.generativeai as genai
import datetime
import ephem
from geopy.geocoders import Nominatim

# --- PAGE SETUP ---
st.set_page_config(page_title="Vedic Astro Guide", page_icon="☸️")

# --- API KEY SETUP (SECURE WAY) ---
try:
    # Ye line secrets.toml se key uthayegi (Local aur Cloud dono jagah)
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("🚨 API Key Missing! Please set GEMINI_API_KEY in .streamlit/secrets.toml")
    st.stop()

# --- SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LOCATION ---
def get_lat_lon(city_name):
    try:
        geolocator = Nominatim(user_agent="vedic_astro_bot_v2")
        loc = geolocator.geocode(city_name)
        if loc: return loc.latitude, loc.longitude
        return None, None
    except:
        return None, None

# --- VEDIC MATHS ---
def get_chart(dob, tob, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = datetime.datetime.combine(dob, tob)
    ayanamsa = 23.86 # Lahiri Ayanamsa
    
    planets = {
        "Sun ☀️": ephem.Sun(obs), "Moon 🌙": ephem.Moon(obs), 
        "Mars ♂️": ephem.Mars(obs), "Mercury ☿️": ephem.Mercury(obs), 
        "Jupiter ♃": ephem.Jupiter(obs), "Venus ♀️": ephem.Venus(obs), 
        "Saturn ♄": ephem.Saturn(obs)
    }
    
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    data = {}
    for p, obj in planets.items():
        # Tropical to Sidereal Conversion
        l = (obj.hlon * 180 / 3.14159 - ayanamsa) % 360
        data[p] = {"sign": signs[int(l/30)], "deg": f"{l%30:.2f}°"}
    return data

# --- UI LAYOUT ---
st.title("☸️ Vedic AI Astrologer")

with st.sidebar:
    st.header("✨ Birth Details")
    name = st.text_input("Name", "User")
    dob = st.date_input("Date", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time", value=datetime.time(23, 45))
    city = st.text_input("City", "Chhindwara")
    
    st.divider()
    style = st.radio("Output:", ["Pin Points 🎯", "Detailed 📜"])
    persona = st.radio("Guide:", ["Friend 👊", "Guru 🧘"])
    
    btn = st.button("Generate Kundli")

# --- MAIN LOGIC ---
if btn and city:
    lat, lon = get_lat_lon(city)
    
    if lat:
        with st.spinner("Aligning Stars..."):
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] # Reset Chat
            
            tone = "Hinglish, slangy" if "Friend" in persona else "Formal, Hindi/English mix"
            fmt = "bullet points" if "Pin" in style else "detailed paragraphs"
            
            sys_msg = f"""
            Act as a Vedic Astrologer. Tone: {tone}. Format: {fmt}.
            User: {name}. City: {city}.
            CHART: {chart}
            
            Task:
            1. Welcome {name}.
            2. Tell their Moon Sign (Rashi) from chart.
            3. Give 2 lines on their nature.
            4. Ask for a question.
            """
            
            st.session_state.messages.append({"role": "user", "content": sys_msg})
            try:
                res = model.generate_content(sys_msg)
                st.session_state.messages.append({"role": "model", "content": res.text})
            except Exception as e:
                st.error(f"AI Error: {e}")
    else:
        st.error("City not found!")

# --- DISPLAY ---
if getattr(st.session_state, 'chart_data', None):
    st.subheader("🌌 Planetary Positions")
    c1, c2, c3, c4 = st.columns(4)
    items = list(st.session_state.chart_data.items())
    for i, (p, info) in enumerate(items):
        [c1, c2, c3, c4][i%4].metric(p, info['sign'], info['deg'])
    st.divider()

# --- CHAT ---
for m in st.session_state.messages:
    if m["role"] == "model":
        with st.chat_message("assistant"): st.markdown(m["content"])
    elif m["role"] == "user" and "Act as" not in m["content"]:
        with st.chat_message("user"): st.markdown(m["content"])

if q := st.chat_input("Ask about future..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"): st.markdown(q)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            hist = [{"role": "user" if m["role"] in ["user","system"] else "model", "parts": [m["content"]]} for m in st.session_state.messages]
            try:
                chat = model.start_chat(history=hist[:-1])
                r = chat.send_message(q)
                st.markdown(r.text)
                st.session_state.messages.append({"role": "model", "content": r.text})
            except:
                st.error("Error connecting.")
