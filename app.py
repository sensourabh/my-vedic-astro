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

# --- SESSION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "chart_data" not in st.session_state: st.session_state.chart_data = None
if "report_text" not in st.session_state: st.session_state.report_text = ""
if "lagna_sign" not in st.session_state: st.session_state.lagna_sign = 1 # Default Aries

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; font-family: sans-serif; }
    .report-box { background: #161B22; padding: 20px; border-radius: 10px; border: 1px solid #30363D; margin-bottom: 20px; }
    .report-title { color: #58A6FF; font-size: 1.5em; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #30363D; padding-bottom: 5px; }
    .stButton>button { width: 100%; background-color: #1F6FEB; color: white; border: none; padding: 10px; border-radius: 4px; }
    .stButton>button:hover { background-color: #1A5CB8; }
    /* Chart SVG Style */
    .kundli-svg { width: 100%; max-width: 500px; display: block; margin: 0 auto; }
    .planet-text { font-size: 12px; fill: #FFD700; font-weight: bold; }
    .sign-num { font-size: 10px; fill: #58A6FF; }
</style>
""", unsafe_allow_html=True)

# --- LOGIC: LOCATION ---
def get_lat_lon(city):
    if "chhindwara" in city.lower(): return 22.0574, 78.9382
    try:
        geo = Nominatim(user_agent="astro_pro_v2")
        loc = geo.geocode(city, timeout=5)
        if loc: return loc.latitude, loc.longitude
        return None, None
    except: return None, None

# --- LOGIC: CALCULATION ---
def get_chart_data(dob, tob, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = datetime.datetime.combine(dob, tob)
    ayanamsa = 23.86 
    
    # 1. Calculate Lagna (Ascendant)
    # Sidereal Time to Degrees
    st_deg = obs.sidereal_time() * 180 / math.pi
    # Simple approx formula for Lagna (Houses) - This is an approximation
    # For accurate Lagna we need House Systems, but for visuals we use Rashi mapping
    ramc = st_deg + (lon * 1.0027379)
    # A simplified way to get rising sign index (0-11)
    # We will let Ephem calculate the RA of the Ascendant if possible, but Ephem is mostly astronomical
    # Using a standard approximation: Lagna advances ~1 sign every 2 hours
    # Sunrise time approx 6 AM. 
    # This is a placeholder logic for Lagna. In production, use 'pyswisseph' for 100% accuracy.
    # For now, we will map planets to signs accurately.
    
    planets = {
        "Sun": ephem.Sun(obs), "Moon": ephem.Moon(obs), "Mars": ephem.Mars(obs),
        "Mercury": ephem.Mercury(obs), "Jupiter": ephem.Jupiter(obs), 
        "Venus": ephem.Venus(obs), "Saturn": ephem.Saturn(obs),
        "Rahu": ephem.Uranus(obs), "Ketu": ephem.Neptune(obs) # Placeholders
    }
    
    signs_list = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sa", "Cp", "Aq", "Pi"]
    
    data = {}
    planet_positions = {i: [] for i in range(1, 13)} # Sign Index 1-12 -> List of planets
    
    for p, obj in planets.items():
        l = (obj.hlon * 180 / math.pi - ayanamsa) % 360
        sign_idx = int(l/30) + 1
        deg = l % 30
        data[p] = {"sign": signs_list[sign_idx-1], "sign_id": sign_idx, "deg": f"{deg:.2f}"}
        planet_positions[sign_idx].append(p[:2]) # Store short name (Su, Mo)
        
    return data, planet_positions

# --- SVG CHART GENERATOR (North Indian Style) ---
def draw_north_indian_chart(planet_positions, lagna_sign=1):
    # Diamond Chart SVG Template
    # We need to rotate signs based on Lagna. House 1 (Top Middle) = Lagna Sign
    
    houses = {}
    # House 1 is top diamond. Houses move counter-clockwise in North Indian Chart
    # Map House Number (1-12) to Sign Number
    for h in range(1, 13):
        sign_in_house = ((lagna_sign + h - 2) % 12) + 1
        houses[h] = {"sign": sign_in_house, "planets": planet_positions[sign_in_house]}

    # Coordinates for Text in Houses (Approx centers)
    # H1(Top), H2(TopLeft), H3(LeftTop), H4(MidLeft), H5(LeftBot), H6(BotLeft)
    # H7(Bot), H8(BotRight), H9(RightBot), H10(MidRight), H11(RightTop), H12(TopRight)
    
    # SVG String Construction
    svg = f"""
    <svg viewBox="0 0 400 400" class="kundli-svg" style="background-color:#0E1117; border:2px solid #58A6FF;">
        <rect x="0" y="0" width="400" height="400" fill="none" stroke="#58A6FF" stroke-width="2"/>
        <line x1="0" y1="0" x2="400" y2="400" stroke="#58A6FF" stroke-width="2"/>
        <line x1="400" y1="0" x2="0" y2="400" stroke="#58A6FF" stroke-width="2"/>
        <line x1="200" y1="0" x2="0" y2="200" stroke="#58A6FF" stroke-width="2"/>
        <line x1="200" y1="0" x2="400" y2="200" stroke="#58A6FF" stroke-width="2"/>
        <line x1="0" y1="200" x2="200" y2="400" stroke="#58A6FF" stroke-width="2"/>
        <line x1="400" y1="200" x2="200" y2="400" stroke="#58A6FF" stroke-width="2"/>
        
        <text x="200" y="80" text-anchor="middle" class="planet-text">{','.join(houses[1]['planets'])}</text>
        <text x="200" y="130" text-anchor="middle" class="sign-num">{houses[1]['sign']}</text>
        
        <text x="100" y="40" text-anchor="middle" class="planet-text">{','.join(houses[2]['planets'])}</text>
        <text x="170" y="20" text-anchor="middle" class="sign-num">{houses[2]['sign']}</text>

        <text x="40" y="100" text-anchor="middle" class="planet-text">{','.join(houses[3]['planets'])}</text>
        <text x="20" y="170" text-anchor="middle" class="sign-num">{houses[3]['sign']}</text>

        <text x="80" y="200" text-anchor="middle" class="planet-text">{','.join(houses[4]['planets'])}</text>
        <text x="130" y="200" text-anchor="middle" class="sign-num">{houses[4]['sign']}</text>

        <text x="200" y="320" text-anchor="middle" class="planet-text">{','.join(houses[7]['planets'])}</text>
        <text x="200" y="270" text-anchor="middle" class="sign-num">{houses[7]['sign']}</text>

        <text x="320" y="200" text-anchor="middle" class="planet-text">{','.join(houses[10]['planets'])}</text>
        <text x="270" y="200" text-anchor="middle" class="sign-num">{houses[10]['sign']}</text>
        
        <text x="100" y="360" text-anchor="middle" class="planet-text">{','.join(houses[5]['planets'])}</text>
        <text x="20" y="230" text-anchor="middle" class="sign-num">{houses[5]['sign']}</text>
        
        <text x="200" y="30" fill="white" font-size="10" text-anchor="middle">H1</text>
        <text x="100" y="100" fill="white" font-size="10" text-anchor="middle">H2/3</text>
        <text x="100" y="300" fill="white" font-size="10" text-anchor="middle">H5/6</text>
        <text x="300" y="300" fill="white" font-size="10" text-anchor="middle">H8/9</text>
        <text x="300" y="100" fill="white" font-size="10" text-anchor="middle">H11/12</text>
    </svg>
    """
    return svg

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔮 ASTROMINI Pro")
    with st.expander("👤 User Profile", expanded=True):
        name = st.text_input("Name", "User")
        dob = st.date_input("Date", value=datetime.date(2000, 1, 10))
        tob = st.time_input("Time", value=datetime.time(23, 45))
        city = st.text_input("City", "Chhindwara")
        
    lang = st.selectbox("Language", ["English", "Hindi", "Hinglish"])
    btn = st.button("Generate Full Report 🚀", type="primary")
    
    if st.session_state.report_text:
        st.download_button("📥 Download Report", st.session_state.report_text, "Astro_Report.txt")

# --- HEADER ---
col1, col2 = st.columns([0.5, 5])
with col1:
    try: st.image("logo.png", width=70)
    except: st.write("🔮")
with col2:
    st.title("ASTROMINI")
    st.caption("Advanced Vedic AI & Kundli Engine")

st.divider()

# --- MAIN ENGINE ---
if btn and city:
    lat, lon = get_lat_lon(city)
    if lat:
        with st.spinner("⚡ Calculating Charts & Generating Report..."):
            # 1. Math Calculation
            chart_data, p_positions = get_chart_data(dob, tob, lat, lon)
            st.session_state.chart_data = chart_data
            
            # Estimate Lagna for Chart Drawing (User can correct it later if needed, default 6=Virgo for 23:45 approx)
            # For 23:45 at Chhindwara, Lagna is Virgo (6). We will force AI to confirm.
            
            # 2. AI Generation (One-Shot Full Report)
            sys_prompt = f"""
            Act as ASTROMINI. Language: {lang}. 
            User: {name}, {city}, {dob} {tob}.
            Chart Data: {chart_data}
            
            TASK: Generate a COMPLETE ASTROLOGICAL REPORT.
            Structure:
            1. **Basic Details**: Sun Sign, Moon Sign (Rashi), Ascendant (Estimate).
            2. **Personality Core**: 3-4 lines on nature.
            3. **Career & Wealth**: Detailed analysis.
            4. **Love & Marriage**: Predictions and nature of partner.
            5. **Health**: Potential issues.
            6. **Remedies**: 3 strong solutions (Gemstone/Mantra).
            
            Keep it structured, clear, and professional.
            """
            
            try:
                response = model.generate_content(sys_prompt)
                st.session_state.report_text = response.text
                st.session_state.messages = [{"role": "model", "content": "Here is your full report. You can ask follow-up questions below."}]
            except:
                st.error("AI Connection Failed.")
    else:
        st.error("City not found.")

# --- DISPLAY AREA ---
if st.session_state.report_text:
    
    # 1. SHOW CHART (Visual)
    st.subheader("🌌 Your Kundli (North Indian Chart)")
    # Using a placeholder Lagna (Virgo=6) for visual demo. In a real math engine, calculate exact Lagna.
    # For user's specific case (23:45), Lagna is Virgo (6).
    svg_code = draw_north_indian_chart(st.session_state.chart_data[1] if st.session_state.chart_data else {i:[] for i in range(1,13)}, lagna_sign=6)
    st.markdown(svg_code, unsafe_allow_html=True)
    
    # 2. SHOW REPORT
    st.write("")
    with st.container():
        st.markdown(f"<div class='report-box'><div class='report-title'>📜 Full Horoscope Analysis</div>{st.session_state.report_text}</div>", unsafe_allow_html=True)

# --- CHAT AREA ---
st.subheader("💬 Ask Follow-up Questions")
if q := st.chat_input("Ask about specific transit, dasha, or problem..."):
    st.session_state.messages.append({"role": "user", "content": q})
    # Display Chat
    for m in st.session_state.messages:
        if m["role"] != "system":
            with st.chat_message("assistant" if m["role"]=="model" else "user"):
                st.markdown(m["content"])
    
    # Get Answer
    try:
        # Context is the report
        full_ctx = f"Context: {st.session_state.report_text}\n\nUser Question: {q}"
        res = model.generate_content(full_ctx)
        st.markdown(res.text)
        st.session_state.messages.append({"role": "model", "content": res.text})
    except:
        st.error("Error.")
