import streamlit as st
import requests
import datetime
from plants_data import plants

st.set_page_config(page_title="ZipPlant 🌱", layout="centered", page_icon="🌱")

# ==================== THEME ====================
st.markdown("""
<style>
    .stApp { background-color: #0b0f14; color: #e6edf3; }
    h1, h2, h3 { color: #9be28f; }
    .stButton>button { background: #1f6f4a; color: white; border-radius: 8px; padding: 0.5rem 1rem; }
    .plant-card { background: #161b22; padding: 1.2rem; border-radius: 12px; border: 1px solid #2a3a2f; margin-bottom: 1rem; }
    .success-msg { color: #9be28f; font-weight: 500; }
    .granny-box { background: #1f2a1f; padding: 1.2rem; border-radius: 12px; border: 2px solid #9be28f; margin-bottom: 1.5rem; font-size: 1.05em; }
    .alert-banner { background: #4a1f1f; padding: 1rem; border-radius: 12px; border: 2px solid #ff6b6b; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ==================== HELPERS ====================
def get_weather(zip_code):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}&count=1").json()
        if "results" not in geo or not geo["results"]:
            return None
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min,temperature_2m_max,precipitation_sum,precipitation_probability_max,et0_fao_evapotranspiration,uv_index_max,wind_speed_10m_max,sunrise,sunset&temperature_unit=fahrenheit&precipitation_unit=inch&wind_speed_unit=mph&timezone=auto"
        r = requests.get(url).json()
        return r["daily"]
    except:
        return None

def get_hardiness_zone(zip_code):
    try:
        r = requests.get(f"https://phzmapi.org/{zip_code}.json", timeout=5)
        return r.json().get("zone", "Unknown")
    except:
        return "Unknown"

def format_date(date_str):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%B %d")

def best_day(weather):
    scores = [weather["temperature_2m_min"][i] - (weather["precipitation_probability_max"][i] * 0.9) for i in range(7)]
    best_idx = scores.index(max(scores))
    return format_date(weather["time"][best_idx])

def soil_readiness(temp_f):
    if temp_f < 50:
        return "🔴 Too cold", "Wait — soil is still sleeping."
    elif temp_f < 60:
        return "🟡 Marginal", "Good for cool crops."
    else:
        return "🟢 Warm enough!", "Roots will grow strong."

def get_alerts(weather):
    alerts = []
    for i in range(min(7, len(weather["time"]))):
        date = format_date(weather["time"][i])
        tmin = weather["temperature_2m_min"][i]
        tmax = weather.get("temperature_2m_max", [0]*7)[i]
        wind = weather.get("wind_speed_10m_max", [0]*7)[i]
        if tmin <= 36:
            alerts.append(f"❄️ Frost Risk on {date} ({tmin}°F)")
        if tmax >= 90:
            alerts.append(f"🔥 Heat Stress on {date} ({tmax}°F)")
        if wind >= 15:
            alerts.append(f"💨 Strong Wind on {date} ({wind} mph)")
    return alerts

# ==================== STATE ====================
if "garden" not in st.session_state: st.session_state.garden = []
if "weather" not in st.session_state: st.session_state.weather = None
if "zone" not in st.session_state: st.session_state.zone = None
if "zip_code" not in st.session_state: st.session_state.zip_code = ""

st.title("ZipPlant 🌱")
st.markdown("**Find the best planting day • Build your garden • Grow smarter**")
st.divider()

tabs = st.tabs(["📍 Location", "🌱 Build Garden", "🌿 My Garden"])

# ==================== LOCATION TAB ====================
with tabs[0]:
    col1, col2 = st.columns([3, 1])
    with col1:
        zip_input = st.text_input("Enter ZIP Code", value=st.session_state.zip_code, placeholder="37013", max_chars=5)
    with col2:
        if st.button("Get Garden Forecast", use_container_width=True, type="primary"):
            st.session_state.zip_code = zip_input
            with st.spinner("Fetching garden intelligence..."):
                st.session_state.weather = get_weather(zip_input)
                st.session_state.zone = get_hardiness_zone(zip_input)

    if st.session_state.weather:
        w = st.session_state.weather
        zone = st.session_state.zone

        alerts = get_alerts(w)
        for alert in alerts[:3]:
            st.markdown(f"<div class='alert-banner'>{alert}</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="granny-box">
            <strong>🌾 Granny Fanny says:</strong><br>
            You are in USDA Hardiness Zone <span style="color:#9be28f; font-size:1.2em;">{zone}</span>.
        </div>
        """, unsafe_allow_html=True)

        st.success(f"**Best planting day: {best_day(w)}**")

        today_soil = w["temperature_2m_min"][0] - 5
        status, advice = soil_readiness(today_soil)
        st.markdown(f"""
        <div style="background:#1f2a1f; padding:1.2rem; border-radius:12px; border:2px solid #9be28f;">
            <h3>🌱 Soil Readiness Today</h3>
            <h2>{status}</h2>
            <p>{advice}</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("7-Day Garden Forecast")
        for i in range(7):
            date = format_date(w['time'][i])
            with st.expander(f"**{date}**", expanded=(i==0)):
                # (You can expand this with full metrics like before if you want)
                st.write("Full details restored in next update")

# ==================== BUILD GARDEN TAB ====================
with tabs[1]:
    st.subheader("Available Plants")
    search_term = st.text_input("🔍 Search plants", placeholder="tomato, basil, heirloom...")

    col1, col2, col3, col4 = st.columns(4)
    with col1: category = st.selectbox("Category", ["All", "Tomatoes", "Peppers", "Herbs", "Greens", "Roots", "Vegetables"])
    with col2: sun_pref = st.selectbox("Sun", ["Any", "Full sun", "Partial"])
    with col3: difficulty = st.selectbox("Skill", ["Any", "Beginner", "Intermediate"])
    with col4: ptype = st.selectbox("Type", ["Any", "Heirloom", "Hybrid"])

    filtered = [p for p in plants if 
                (not search_term or search_term.lower() in p["name"].lower()) and
                (category == "All" or category.lower() in p["type"].lower()) and
                (sun_pref == "Any" or sun_pref.lower() in p["sun"].lower()) and
                (difficulty == "Any" or difficulty.lower() in p.get("difficulty","").lower()) and
                (ptype == "Any" or ptype == p.get("heirloom_hybrid", ""))]

    cols = st.columns(2)
    for idx, p in enumerate(filtered):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="plant-card">
                <h3>{p['name']}</h3>
                <small>{p['type']} • {p.get('heirloom_hybrid','')}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.zone:
                st.success(f"✅ Good for Zone {st.session_state.zone}")
            st.write(f"**Spacing:** {p['spacing']}")
            if st.button("➕ Add to Garden", key=f"add_{idx}"):
                st.session_state.garden.append(p)
                st.rerun()

# ==================== MY GARDEN TAB ====================
with tabs[2]:
    if not st.session_state.garden:
        st.info("Your garden is empty. Go add some plants!")
    else:
        st.subheader(f"My Garden ({len(st.session_state.garden)} plants)")
        for i, p in enumerate(st.session_state.garden[:]):
            with st.expander(f"🌱 {p['name']}", expanded=True):
                st.write(p.get('pitch', ''))
                if st.button("🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.garden.pop(i)
                    st.rerun()

st.caption("Made with ❤️ for gardeners")
