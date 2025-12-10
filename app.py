import streamlit as st
import google.generativeai as genai
import datetime
import ephem
from geopy.geocoders import Nominatim

# --- PAGE SETUP (Sabse upar hona chahiye) ---
st.set_page_config(page_title="Vedic Astro Guide", page_icon="☸️")

# --- API KEY SETUP (Smart Logic) ---
try:
    # Pehle Cloud par secret key dhoondhega
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # Agar Cloud nahi mila (Laptop par), toh ye use karega
    # 👇👇👇 NIche Inverted Commas ke beech apni asli key daalo 👇👇👇
    GOOGLE_API_KEY = "AIzaSyBvbX3VL1Qk33U-DdGYTq8TO2GRFl2fCiE" 

# --- AI CONNECT ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"AI Error: {e}")

# --- SESSION MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None

# --- FUNCTION: LOCATION FINDER ---
def get_lat_lon(city_name):
    try:
        geolocator = Nominatim(user_agent="my_astro_app_v1")
        loc = geolocator.geocode(city_name)
        if loc: return loc.latitude, loc.longitude
        return None, None
    except:
        return None, None

# --- FUNCTION: VEDIC CHART CALCULATOR ---
def get_chart(dob, tob, lat, lon):
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.date = datetime.datetime.combine(dob, tob)
    ayanamsa = 23.86 # Lahiri Ayanamsa Approx
    
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

# --- UI START ---
st.title("☸️ Vedic AI Astrologer")

# --- SIDEBAR ---
with st.sidebar:
    st.header("✨ Birth Details")
    name = st.text_input("Name", "User")
    dob = st.date_input("Date", value=datetime.date(2000, 1, 10))
    tob = st.time_input("Time", value=datetime.time(23, 45))
    city = st.text_input("City", "Chhindwara") # Default city
    
    st.divider()
    style = st.radio("Output Style:", ["Pin Points 🎯", "Detailed 📜"])
    persona = st.radio("Persona:", ["Friend 👊", "Guru 🧘"])
    
    btn = st.button("Generate Kundli")

# --- MAIN LOGIC ---
if btn and city:
    lat, lon = get_lat_lon(city)
    
    if lat:
        with st.spinner("Calculating Planetary Positions..."):
            # 1. Calculate Chart
            chart = get_chart(dob, tob, lat, lon)
            st.session_state.chart_data = chart
            st.session_state.messages = [] # Reset chat on new generation
            
            # 2. Prepare System Prompt
            tone = "Hinglish, slang, emojis" if "Friend" in persona else "Hindi/English, respectful, spiritual"
            fmt = "bullet points only" if "Pin" in style else "detailed paragraphs"
            
            sys_msg = f"""
            Act as an expert Vedic Astrologer. Tone: {tone}. Format: {fmt}.
            
            USER DATA:
            Name: {name}
            Birth City: {city} (Lat: {lat}, Lon: {lon})
            
            PLANETARY CHART (Calculated):
            {chart}
            
            TASK:
            1. Welcome {name}.
            2. Tell them their Moon Sign (Rashi) based on the chart above.
            3. Give a 2-line personality insight.
            4. Ask what they want to know (Career, Love, etc).
            """
            
            # 3. Call AI
            st.session_state.messages.append({"role": "user", "content": sys_msg})
            try:
                response = model.generate_content(sys_msg)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except Exception as e:
                st.error(f"AI Error: {e}")
    else:
        st.error("❌ City not found! Please check spelling.")

# --- DISPLAY CHART (CLEAN GRID) ---
if st.session_state.chart_data:
    st.subheader("🌌 Planetary Positions")
    cols = st.columns(4)
    for i, (planet, info) in enumerate(st.session_state.chart_data.items()):
        cols[i % 4].metric(planet, info['sign'], info['deg'])
    st.divider()

# --- CHAT INTERFACE ---
# Hide system prompt from user view
for msg in st.session_state.messages:
    if msg["role"] == "model":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
    elif msg["role"] == "user" and "Act as an expert" not in msg["content"]:
        with st.chat_message("user"):
            st.markdown(msg["content"])

# --- USER INPUT ---
if user_query := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing stars..."):
            # History convert for AI
            history_ai = []
            for m in st.session_state.messages:
                # System prompt ko user message ki tarah bhejo (Gemini trick)
                role = "user" if m["role"] in ["user", "system"] else "model"
                history_ai.append({"role": role, "parts": [m["content"]]})
            
            try:
                chat = model.start_chat(history=history_ai[:-1])
                response = chat.send_message(user_query)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except Exception as e:
                st.error("Error connecting to AI. Try again.")