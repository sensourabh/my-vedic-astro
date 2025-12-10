import streamlit as st
import google.generativeai as genai
import datetime
import ephem
from geopy.geocoders import Nominatim

# --- PAGE CONFIG ---
st.set_page_config(page_title="Vedic Astro Guide", page_icon="☸️")

# --- API KEY SETUP (SECURE LOGIC) ---
# Jab Laptop par ho: Niche "except" mein apni key daalo.
# Jab GitHub par dalo: "except" wali key DELETE kar dena.
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # 👇👇👇 LOCAL TESTING KE LIYE YAHAN KEY DAALO 👇👇👇
    GOOGLE_API_KEY = "AIzaSy_YAHAN_TUMHARI_ASLI_KEY_AAYEGI" 
    # 👆👆👆 GITHUB PE UPLOAD KARNE SE PEHLE ISSE HATA DENA

# --- AI SETUP ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("🚨 API Key Error! Check your code or secrets.")

# --- SESSION STATES ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None

# --- LOCATION FINDER ---
def get_lat_lon(city_name):
    try:
        # User agent zaroori hai taaki error na aaye
        geolocator = Nominatim(user_agent="vedic_astro_bot_v2")
        loc = geolocator.geocode(city_name)
        if loc: return loc.latitude, loc.longitude
        return None, None
    except:
        return None, None

# --- VEDIC CHART CALCULATOR ---
def get_chart(dob, tob, lat, lon):
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.date = datetime.datetime.combine(dob, tob)
    
    # Lahiri Ayanamsa (Approx subtraction for Vedic Sidereal)
    ayanamsa = 23.86 
    
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
        # Tropical to Vedic Conversion
        l = (obj.hlon * 180 / 3.14159 - ayanamsa) % 360
        data[p] = {"sign": signs[int(l/30)], "deg": f"{l%30:.2f}°"}
    return data

# --- UI HEADER ---
st.title("☸️ Vedic AI Astrologer")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("📝 Enter Details")
    name = st.text_input("Name", "User")
    dob = st.date_input("Date", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time", value=datetime.time(23, 45))
    city = st.text_input("City", "Chhindwara")
    
    st.divider()
    style = st.radio("Output Style:", ["Pin Points 🎯", "Detailed 📜"])
    persona = st.radio("Mode:", ["Friend 👊", "Guru 🧘"])
    
    btn = st.button("Generate Kundli")

# --- MAIN LOGIC ---
if btn and city:
    lat, lon = get_lat_lon(city)
    
    if lat:
        with st.spinner("Calculating Planetary Positions..."):
            # 1. Calculate Chart
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] # Reset chat
            
            # 2. Tone Setup
            tone = "Hinglish, slang, friendly" if "Friend" in persona else "Hindi/English, respectful, deep"
            fmt = "bullet points only" if "Pin" in style else "detailed paragraphs"
            
            # 3. System Prompt
            sys_msg = f"""
            Act as an expert Vedic Astrologer. 
            **Tone:** {tone}
            **Format:** {fmt}
            
            **USER DATA:**
            Name: {name}
            Birth Details: {dob} at {tob} in {city} (Lat: {lat}, Lon: {lon})
            
            **CALCULATED CHART:**
            {chart}
            
            **INSTRUCTIONS:**
            1. Welcome {name}.
            2. Tell them their Moon Sign (Rashi) based on the chart above.
            3. DO NOT ask for birth time or place again (I have provided it).
            4. Give a short personality insight.
            5. Ask what they want to discuss next.
            """
            
            # 4. First Message to AI (Hidden from User)
            st.session_state.messages.append({"role": "user", "content": sys_msg})
            try:
                response = model.generate_content(sys_msg)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except:
                st.error("AI connection failed. Check API Key.")
    else:
        st.error("❌ City not found! Please check spelling.")

# --- DISPLAY CHART GRID ---
if st.session_state.chart_data:
    st.subheader("🌌 Your Planetary Chart")
    cols = st.columns(4)
    for i, (planet, info) in enumerate(st.session_state.chart_data.items()):
        cols[i % 4].metric(planet, info['sign'], info['deg'])
    st.divider()

# --- CHAT INTERFACE ---
for msg in st.session_state.messages:
    if msg["role"] == "model":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
    elif msg["role"] == "user" and "Act as" not in msg["content"]: 
        # Don't show the huge system prompt to the user
        with st.chat_message("user"):
            st.markdown(msg["content"])

# --- USER INPUT ---
if user_query := st.chat_input("Ask a follow-up question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                # Convert history for Gemini
                history_ai = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] in ["user", "system"] else "model"
                    history_ai.append({"role": role, "parts": [m["content"]]})
                
                chat = model.start_chat(history=history_ai[:-1])
                response = chat.send_message(user_query)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except:
                st.error("Connection Error.")
