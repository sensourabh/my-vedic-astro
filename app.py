import streamlit as st
import google.generativeai as genai
import datetime
import ephem
import math
import base64
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
if "chart_positions" not in st.session_state: st.session_state.chart_positions = None 
if "lagna_sign" not in st.session_state: st.session_state.lagna_sign = 6 

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #000000; font-family: sans-serif; }
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #F0F2F6 !important; color: #000000 !important; border: 1px solid #ccc !important;
    }
    .report-box { background: #F8F9FA; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; color: #000; }
    .report-title { color: #1F6FEB; font-size: 1.5em; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #ccc; }
    .disclaimer-box { font-size: 0.8em; color: #666; background: #fff3cd; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- HELPER: LOCATION ---
def get_lat_lon(city):
    if "chhindwara" in city.lower(): return 22.0574, 78.9382
    try:
        geo = Nominatim(user_agent="astro_final_v100")
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
    
    planets = {
        "Sun": ephem.Sun(obs), "Moon": ephem.Moon(obs), "Mars": ephem.Mars(obs),
        "Mercury": ephem.Mercury(obs), "Jupiter": ephem.Jupiter(obs), 
        "Venus": ephem.Venus(obs), "Saturn": ephem.Saturn(obs)
    }
    
    data_text = {}
    planet_positions = {i: [] for i in range(1, 13)}
    signs_list = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sa", "Cp", "Aq", "Pi"]
    
    for p, obj in planets.items():
        l = (obj.hlon * 180 / math.pi - ayanamsa) % 360
        sign_idx = int(l/30) + 1 
        deg = l % 30
        data_text[p] = {"sign": signs_list[sign_idx-1], "deg": f"{deg:.2f}"}
        planet_positions[sign_idx].append(p[:2]) 
        
    st_time = obs.sidereal_time() * 180 / math.pi
    lagna_degree = (st_time + float(lon) - ayanamsa) % 360
    lagna_sign = int(lagna_degree / 30) + 1
    
    return data_text, planet_positions, lagna_sign

# --- HELPER: DRAW CHART (Fixed Image Rendering) ---
def render_chart_image(planet_positions, lagna_sign):
    houses = {}
    for h in range(1, 13):
        sign_in_house = ((lagna_sign + h - 2) % 12) + 1
        p_list = planet_positions.get(sign_in_house, [])
        houses[h] = {"sign": sign_in_house, "planets": ",".join(p_list)}

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" style="background-color: white;">
        <defs>
            <style>
                .line {{ stroke: #000000; stroke-width: 2; fill: none; }}
                .p-text {{ font-size: 14px; fill: #D32F2F; font-weight: bold; font-family: sans-serif; }}
                .s-num {{ font-size: 12px; fill: #1976D2; font-family: sans-serif; }}
            </style>
        </defs>
        <rect x="2" y="2" width="396" height="396" class="line"/>
        <line x1="0" y1="0" x2="400" y2="400" class="line"/>
        <line x1="400" y1="0" x2="0" y2="400" class="line"/>
        <line x1="200" y1="0" x2="0" y2="200" class="line"/>
        <line x1="200" y1="0" x2="400" y2="200" class="line"/>
        <line x1="0" y1="200" x2="200" y2="400" class="line"/>
        <line x1="400" y1="200" x2="200" y2="400" class="line"/>

        <text x="200" y="90" text-anchor="middle" class="p-text">{houses[1]['planets']}</text>
        <text x="200" y="130" text-anchor="middle" class="s-num">{houses[1]['sign']}</text>
        <text x="100" y="45" text-anchor="middle" class="p-text">{houses[2]['planets']}</text>
        <text x="170" y="25" text-anchor="middle" class="s-num">{houses[2]['sign']}</text>
        <text x="45" y="100" text-anchor="middle" class="p-text">{houses[3]['planets']}</text>
        <text x="25" y="170" text-anchor="middle" class="s-num">{houses[3]['sign']}</text>
        <text x="80" y="205" text-anchor="middle" class="p-text">{houses[4]['planets']}</text>
        <text x="130" y="200" text-anchor="middle" class="s-num">{houses[4]['sign']}</text>
        <text x="100" y="360" text-anchor="middle" class="p-text">{houses[5]['planets']}</text>
        <text x="25" y="230" text-anchor="middle" class="s-num">{houses[5]['sign']}</text>
        <text x="100" y="300" text-anchor="middle" class="p-text">{houses[6]['planets']}</text>
        <text x="170" y="380" text-anchor="middle" class="s-num">{houses[6]['sign']}</text>
        <text x="200" y="320" text-anchor="middle" class="p-text">{houses[7]['planets']}</text>
        <text x="200" y="270" text-anchor="middle" class="s-num">{houses[7]['sign']}</text>
        <text x="300" y="300" text-anchor="middle" class="p-text">{houses[8]['planets']}</text>
        <text x="230" y="380" text-anchor="middle" class="s-num">{houses[8]['sign']}</text>
        <text x="300" y="360" text-anchor="middle" class="p-text">{houses[9]['planets']}</text>
        <text x="375" y="230" text-anchor="middle" class="s-num">{houses[9]['sign']}</text>
        <text x="320" y="205" text-anchor="middle" class="p-text">{houses[10]['planets']}</text>
        <text x="270" y="200" text-anchor="middle" class="s-num">{houses[10]['sign']}</text>
        <text x="355" y="100" text-anchor="middle" class="p-text">{houses[11]['planets']}</text>
        <text x="375" y="170" text-anchor="middle" class="s-num">{houses[11]['sign']}</text>
        <text x="300" y="45" text-anchor="middle" class="p-text">{houses[12]['planets']}</text>
        <text x="230" y="25" text-anchor="middle" class="s-num">{houses[12]['sign']}</text>
    </svg>
    """
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}" width="500"/>'

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔮 Controls")
    with st.expander("👤 Birth Details", expanded=True):
        name = st.text_input("Name", "User")
        dob = st.date_input("Date", value=datetime.date(2000, 1, 10))
        tob = st.time_input("Time", value=datetime.time(23, 45))
        city = st.text_input("City", "Chhindwara")
        
    lang = st.selectbox("Language", ["English", "Hindi", "Hinglish"])
    btn = st.button("Generate Full Report 🚀", type="primary")

    if st.session_state.report_text:
        st.download_button("📥 Download Report", st.session_state.report_text, "Astro_Report.txt")
        
    # --- DISCLAIMER NOTICE ---
    st.markdown("""
    <div class="disclaimer-box">
        <b>⚠️ Notice:</b><br>
        This report is generated by AI for entertainment & guidance purposes. 
        We do not claim 100% accuracy. Please consult a professional astrologer for serious decisions.
    </div>
    """, unsafe_allow_html=True)

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
            data_text, p_positions, lagna = get_chart_data(dob, tob, lat, lon)
            st.session_state.chart_data = data_text
            st.session_state.chart_positions = p_positions
            st.session_state.lagna_sign = lagna
            
            sys_prompt = f"""
            Act as ASTROMINI. Language: {lang}. 
            User: {name}, {city}, {dob} {tob}.
            Chart Data: {data_text}
            Lagna (Ascendant) Sign Index: {lagna}
            
            TASK: Generate a COMPLETE REPORT.
            1. Basic Details. 2. Personality. 3. Career. 4. Love. 5. Health. 6. Remedies.
            IMPORTANT: Add a disclaimer at the end stating AI limitations.
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
    
    st.warning("⚠️ Disclaimer: Not 100% accurate. For entertainment purposes only.")
    
    # 1. SHOW CHART
    st.subheader("🌌 North Indian Chart")
    if st.session_state.chart_positions:
        html_chart = render_chart_image(st.session_state.chart_positions, st.session_state.lagna_sign)
        st.markdown(f"<div style='text-align:center;'>{html_chart}</div>", unsafe_allow_html=True)
    
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
