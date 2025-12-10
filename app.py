import streamlit as st
import google.generativeai as genai
import datetime
import ephem
import math
from geopy.geocoders import Nominatim

# --- PAGE SETUP ---
st.set_page_config(
    page_title="ASTROMINI Pro", 
    page_icon="🔮", 
    layout="wide"
)

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
    st.error("⚠️ API Key Error.")

# --- SESSION STATES ---
if "messages" not in st.session_state: st.session_state.messages = []
if "report_text" not in st.session_state: st.session_state.report_text = ""
if "chart_positions" not in st.session_state: st.session_state.chart_positions = None # For SVG
if "lagna_sign" not in st.session_state: st.session_state.lagna_sign = 6 # Default Virgo

# --- CUSTOM CSS (WHITE THEME) ---
st.markdown("""
<style>
    /* 1. Main Background - White */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: sans-serif;
    }

    /* 2. Inputs - Clean White */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #333 !important;
    }
    
    /* 3. Report Box */
    .report-box {
        background: #F8F9FA; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #ddd; 
        margin-bottom: 20px;
        color: #000;
    }
    .report-title {
        color: #1F6FEB; 
        font-size: 1.5em; 
        font-weight: bold; 
        margin-bottom: 10px; 
        border-bottom: 1px solid #ccc;
    }

    /* 4. Chart SVG Style (White Mode) */
    .kundli-svg { 
        width: 100%; 
        max-width: 500px; 
        display: block; 
        margin: 0 auto; 
        background-color: #FFFFFF; /* White Background */
        border: 2px solid #000000; /* Black Border */
    }
    .planet-text { font-size: 12px; fill: #D32F2F; font-weight: bold; } /* Red Text for Planets */
    .sign-num { font-size: 10px; fill: #1F6FEB; } /* Blue Text for Signs */
    line, rect { stroke: #000000 !important; stroke-width: 2; } /* Black Lines */
</style>
""", unsafe_allow_html=True)

# --- HELPER: LOCATION ---
def get_lat_lon(city):
    if "chhindwara" in city.lower(): return 22.0574, 78.9382
    try:
        geo = Nominatim(user_agent="astro_white_v3")
        loc = geo.geocode(city, timeout=5)
        if loc: return loc.latitude, loc.longitude
        return None, None
    except: return None, None

# --- HELPER: CALCULATION ---
def get_chart_data(dob, tob, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = datetime.datetime.combine(dob, tob)
    ayanamsa = 23.86 
    
    # Planets
    planets = {
        "Sun": ephem.Sun(obs), "Moon": ephem.Moon(obs), "Mars": ephem.Mars(obs),
        "Mercury": ephem.Mercury(obs), "Jupiter": ephem.Jupiter(obs), 
        "Venus": ephem.Venus(obs), "Saturn": ephem.Saturn(obs),
        "Rahu": ephem.Uranus(obs), "Ketu": ephem.Neptune(obs)
    }
    
    # 1. Planet Details (For AI)
    data_text = {}
    
    # 2. Planet Positions (For Drawing Chart - Keys 1 to 12)
    planet_positions = {i: [] for i in range(1, 13)}
    
    signs_list = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sa", "Cp", "Aq", "Pi"]
    
    for p, obj in planets.items():
        l = (obj.hlon * 180 / math.pi - ayanamsa) % 360
        sign_idx = int(l/30) + 1 # 1 to 12
        deg = l % 30
        
        # Save for AI
        data_text[p] = {"sign": signs_list[sign_idx-1], "deg": f"{deg:.2f}"}
        
        # Save for Chart Drawing (Short Name)
        planet_positions[sign_idx].append(p[:2]) 
        
    # 3. Calculate Lagna (Approx for Drawing)
    # Using Sidereal Time (RAMC) to estimate Rising Sign
    st = obs.sidereal_time() * 180 / math.pi
    # Simple logic: Add Longitude, subtract Ayanamsa
    # This is a rough estimation. For production, PySwisseph is recommended.
    # We will let AI confirm, but for Drawing we need a number.
    lagna_degree = (st + float(lon) - ayanamsa) % 360
    lagna_sign = int(lagna_degree / 30) + 1
    
    return data_text, planet_positions, lagna_sign

# --- HELPER: DRAW CHART (FIXED) ---
def draw_north_indian_chart(planet_positions, lagna_sign):
    # Mapping House Numbers to Signs based on Lagna
    houses = {}
    for h in range(1, 13):
        sign_in_house = ((lagna_sign + h - 2) % 12) + 1
        houses[h] = {"sign": sign_in_house, "planets": planet_positions[sign_in_house]}

    svg = f"""
    <svg viewBox="0 0 400 400" class="kundli-svg">
        <rect x="0" y="0" width="400" height="400" fill="none" stroke="black" stroke-width="2"/>
        <line x1="0" y1="0" x2="400" y2="400" stroke="black" stroke-width="2"/>
        <line x1="400" y1="0" x2="0" y2="400" stroke="black" stroke-width="2"/>
        <line x1="200" y1="0" x2="0" y2="200" stroke="black" stroke-width="2"/>
        <line x1="200" y1="0" x2="400" y2="200" stroke="black" stroke-width="2"/>
        <line x1="0" y1="200" x2="200" y2="400" stroke="black" stroke-width="2"/>
        <line x1="400" y1="200" x2="200" y2="400" stroke="black" stroke-width="2"/>
        
        <text x="200" y="80" text-anchor="middle" class="planet-text">{','.join(houses[1]['planets'])}</text>
        <text x="200" y="130" text-anchor="middle" class="sign-num">{houses[1]['sign']}</text>
        
        <text x="100" y="40" text-anchor="middle" class="planet-text">{','.join(houses[2]['planets'])}</text>
        <text x="170" y="20" text-anchor="middle" class="sign-num">{houses[2]['sign']}</text>

        <text x="40" y="100" text-anchor="middle" class="planet-text">{','.join(houses[3]['planets'])}</text>
        <text x="20" y="170" text-anchor="middle" class="sign-num">{houses[3]['sign']}</text>

        <text x="80" y="200" text-anchor="middle" class="planet-text">{','.join(houses[4]['planets'])}</text>
        <text x="130" y="200" text-anchor="middle" class="sign-num">{houses[4]['sign']}</text>

        <text x="100" y="360" text-anchor="middle" class="planet-text">{','.join(houses[5]['planets'])}</text>
        <text x="20" y="230" text-anchor="middle" class="sign-num">{houses[5]['sign']}</text>
        
        <text x="100" y="300" text-anchor="middle" class="planet-text">{','.join(houses[6]['planets'])}</text>
        <text x="170" y="380" text-anchor="middle" class="sign-num">{houses[6]['sign']}</text>

        <text x="200" y="320" text-anchor="middle" class="planet-text">{','.join(houses[7]['planets'])}</text>
        <text x="200" y="270" text-anchor="middle" class="sign-num">{houses[7]['sign']}</text>

        <text x="300" y="300" text-anchor="middle" class="planet-text">{','.join(houses[8]['planets'])}</text>
        <text x="230" y="380" text-anchor="middle" class="sign-num">{houses[8]['sign']}</text>

        <text x="300" y="360" text-anchor="middle" class="planet-text">{','.join(houses[9]['planets'])}</text>
        <text x="380" y="230" text-anchor="middle" class="sign-num">{houses[9]['sign']}</text>

        <text x="320" y="200" text-anchor="middle" class="planet-text">{','.join(houses[10]['planets'])}</text>
        <text x="270" y="200" text-anchor="middle" class="sign-num">{houses[10]['sign']}</text>

        <text x="360" y="100" text-anchor="middle" class="planet-text">{','.join(houses[11]['planets'])}</text>
        <text x="380" y="170" text-anchor="middle" class="sign-num">{houses[11]['sign']}</text>

        <text x="300" y="40" text-anchor="middle" class="planet-text">{','.join(houses[12]['planets'])}</text>
        <text x="230" y="20" text-anchor="middle" class="sign-num">{houses[12]['sign']}</text>
    </svg>
    """
    return svg

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔮 Controls")
    
    with st.expander("👤 Birth Details", expanded=True):
        name = st.text_input("Name", "User")
        dob = st.date_input("Date", value=datetime.date(2000, 1, 10))
        tob = st.time_input("Time", value=datetime.time(23, 45))
        city = st.text_input("City", "Chhindwara")
        
    lang = st.selectbox("Language", ["English", "Hindi", "Hinglish"])
    btn = st.button("Generate Report 🚀", type="primary")

    if st.session_state.report_text:
        st.download_button("📥 Download Report", st.session_state.report_text, "Astro_Report.txt")

# --- HEADER ---
col1, col2 = st.columns([0.5, 5])
with col1:
    try: st.image("logo.png", width=70)
    except: st.write("🔮")
with col2:
    st.title("ASTROMINI")
    st.caption("Advanced Vedic AI")

st.divider()

# --- MAIN ENGINE ---
if btn and city:
    lat, lon = get_lat_lon(city)
    if lat:
        with st.spinner("⚡ Calculating Charts..."):
            
            # 1. Get ALL Data (Fix for KeyError)
            # data_text = AI ke liye info
            # p_positions = Chart drawing ke liye {1:[], 2:[]}
            # lagna = Ascendant Sign Number
            data_text, p_positions, lagna = get_chart_data(dob, tob, lat, lon)
            
            # Save to Session
            st.session_state.chart_data = data_text
            st.session_state.chart_positions = p_positions
            st.session_state.lagna_sign = lagna
            
            # 2. Generate Report
            sys_prompt = f"""
            Act as ASTROMINI. Language: {lang}. 
            User: {name}, {city}, {dob} {tob}.
            Chart Data: {data_text}
            Lagna (Ascendant) Sign Index: {lagna}
            
            TASK: Generate a COMPLETE REPORT.
            1. Basic Details.
            2. Personality.
            3. Career & Wealth.
            4. Love & Marriage.
            5. Health.
            6. Remedies.
            """
            
            try:
                response = model.generate_content(sys_prompt)
                st.session_state.report_text = response.text
                st.session_state.messages = [{"role": "model", "content": "Here is your full report. Ask follow-up questions below."}]
            except:
                st.error("AI Connection Failed.")
    else:
        st.error("City not found.")

# --- DISPLAY AREA ---
if st.session_state.report_text:
    
    # 1. SHOW CHART (Visual - White Bg, Black Lines)
    st.subheader("🌌 North Indian Chart")
    
    # Using saved positions (Error Fixed Here)
    if st.session_state.chart_positions:
        svg_code = draw_north_indian_chart(st.session_state.chart_positions, st.session_state.lagna_sign)
        st.markdown(svg_code, unsafe_allow_html=True)
    
    # 2. SHOW REPORT
    st.write("")
    st.markdown(f"<div class='report-box'><div class='report-title'>📜 Full Horoscope Analysis</div>{st.session_state.report_text}</div>", unsafe_allow_html=True)

# --- CHAT AREA ---
st.subheader("💬 Ask Follow-up")
if q := st.chat_input("Ask about specific problem..."):
    st.session_state.messages.append({"role": "user", "content": q})
    for m in st.session_state.messages:
        if m["role"] != "system":
            with st.chat_message("assistant" if m["role"]=="model" else "user"):
                st.markdown(m["content"])
    
    try:
        full_ctx = f"Context: {st.session_state.report_text}\n\nUser Question: {q}"
        res = model.generate_content(full_ctx)
        st.markdown(res.text)
        st.session_state.messages.append({"role": "model", "content": res.text})
    except:
        st.error("Error.")
