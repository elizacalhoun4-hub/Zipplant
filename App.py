import streamlit as st
import requests
import datetime

# Importing the databases
try:
    from vegetable_data import vegetables
    from herb_data import herbs
    from flower_data import flowers
except ImportError as e:
    st.error(f"Missing Data File: {e}")
    vegetables, herbs, flowers = [], [], []

st.set_page_config(page_title="ZipPlant 🌱", layout="centered", page_icon="🌱")

# ==================== UPGRADED THEME ====================
st.markdown("""
<style>
    .stApp { background-color: #0b0f14; color: #e6edf3; }
    h1, h2, h3 { color: #9be28f; }
    .stButton>button { background: #1f6f4a; color: white; border-radius: 8px; width: 100%; border: none; }
    .stButton>button:hover { background: #2a8a5c; border: none; }
    .plant-card { background: #161b22; padding: 1rem; border-radius: 12px; border: 1px solid #2a3a2f; margin-bottom: 0.5rem; min-height: 120px; }
    .granny-box { background: #1f2a1f; padding: 1.2rem; border-radius: 12px; border: 2px solid #9be28f; margin-bottom: 1.5rem; font-size: 1.05em; line-height: 1.4; }
    .field-label { color: #9be28f; font-weight: bold; margin-top: 8px; display: block; }
    .alert-banner { background: #4a1f1f; padding: 1rem; border-radius: 12px; border: 2px solid #ff6b6b; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ==================== HELPERS ====================
def get_weather(zip_code):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}&count=1").json()
        if "results" not in geo or not geo["results"]: return None
        lat, lon = geo["results"][0]["latitude"], geo["results"][0]["longitude"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min,temperature_2m_max,precipitation_sum,precipitation_probability_max,et0_fao_evapotranspiration,uv_index_max,wind_speed_10m_max,sunrise,sunset&temperature_unit=fahrenheit&precipitation_unit=inch&wind_speed_unit=mph&timezone=auto"
        return requests.get(url).json()["daily"]
    except: 
        return None

def get_hardiness_zone(zip_code):
    try:
        r = requests.get(f"https://phzmapi.org/{zip_code}.json", timeout=5)
        return r.json().get("zone", "Unknown")
    except: 
        return "Unknown"

def get_alerts(weather):
    alerts = []
    for i in range(min(7, len(weather["time"]))):
        tmin = weather["temperature_2m_min"][i]
        tmax = weather.get("temperature_2m_max", [0]*7)[i]
        if tmin <= 36: 
            alerts.append(f"❄️ Frost Risk: {tmin}°F upcoming.")
        if tmax >= 92: 
            alerts.append(f"🔥 Heat Stress: {tmax}°F upcoming.")
    return list(set(alerts))

# Simple best planting day
def best_planting_day(weather):
    if not weather or "time" not in weather:
        return "Check local forecast"
    scores = []
    for i in range(min(7, len(weather["time"]))):
        temp_score = weather["temperature_2m_min"][i] - (weather.get("precipitation_probability_max", [0]*7)[i] * 0.8)
        scores.append(temp_score)
    best_idx = scores.index(max(scores))
    date = datetime.datetime.strptime(weather["time"][best_idx], "%Y-%m-%d")
    return date.strftime("%B %d")

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
        zip_input = st.text_input("Enter ZIP Code", value=st.session_state.zip_code, max_chars=5, placeholder="37013")
    with col2:
        if st.button("Update Forecast", type="primary", use_container_width=True):
            st.session_state.zip_code = zip_input
            with st.spinner("Fetching garden weather..."):
                st.session_state.weather = get_weather(zip_input)
                st.session_state.zone = get_hardiness_zone(zip_input)

    if st.session_state.weather:
        w = st.session_state.weather
        for alert in get_alerts(w)[:2]:
            st.markdown(f"<div class='alert-banner'>{alert}</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='granny-box'>
            <strong>🌾 Granny Fanny says:</strong> You're in Zone <strong>{st.session_state.zone}</strong>. 
            A lovely place to grow!
        </div>
        """, unsafe_allow_html=True)

        st.success(f"**Best Day to Plant this week:** {best_planting_day(w)}")

# ==================== BUILD GARDEN TAB ====================
with tabs[1]:
    st.subheader("Add Varieties to Your Homestead")
    v_tab, h_tab, f_tab = st.tabs(["🥕 Vegetables", "🌿 Herbs", "🌸 Flowers"])

    def render_category(data, emoji, key_prefix):
        query = st.text_input(f"🔍 Search {key_prefix.capitalize()}", key=f"search_{key_prefix}").lower()
        filtered = [p for p in data if not query or query in p['common_name'].lower() or query in p.get('cultivar','').lower()]
        
        cols = st.columns(2)
        for idx, p in enumerate(filtered):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class='plant-card'>
                    <strong>{emoji} {p['common_name']}</strong><br>
                    <small>{p['cultivar']} ({p['type']})</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Add to Garden", key=f"add_{key_prefix}_{idx}"):
                    if not any(g.get("common_name") == p["common_name"] for g in st.session_state.garden):
                        st.session_state.garden.append(p.copy())
                        st.toast(f"✅ Added {p['common_name']}!")
                        st.rerun()

    with v_tab: render_category(vegetables, "🥕", "veg")
    with h_tab: render_category(herbs, "🌿", "herb")
    with f_tab: render_category(flowers, "🌸", "flower")

# ==================== MY GARDEN TAB ====================
with tabs[2]:
    st.subheader(f"My Garden ({len(st.session_state.garden)} plants)")
    if not st.session_state.garden:
        st.info("Your garden is empty. Go add some plants from Build Garden!")
    
    for i, p in enumerate(st.session_state.garden[:]):
        with st.expander(f"🌱 {p['common_name']} – {p['cultivar']}", expanded=True):
            st.markdown(f"""
            <div class='granny-box'>
                <strong>🌾 Granny Fanny says:</strong> <em>"{p.get('granny_fanny', 'Great choice!')}"</em>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<span class='field-label'>Scientific Name</span> {p['scientific_name']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Growth Habit</span> {p['growth_habit']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Method</span> {p['method']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Depth</span> {p['depth']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Spacing (Traditional)</span> {p['spacing_traditional']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Spacing (Grid)</span> {p['spacing_grid']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Yield for Couple</span> {p['yield_family_2']}", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<span class='field-label'>Care</span> {p['care']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Days to Harvest</span> {p['days_to_harvest']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Harvest Indicators</span> {p['harvest_indicators']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Preservation</span> {p['preservation']}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>Companions</span> {', '.join(p.get('companions', []))}", unsafe_allow_html=True)
                st.markdown(f"<span class='field-label'>No-Go</span> {', '.join(p.get('no_go', []))}", unsafe_allow_html=True)

            if st.button("🗑️ Remove", key=f"remove_{i}", use_container_width=True):
                st.session_state.garden.pop(i)
                st.rerun()

st.caption("Made with ❤️ for gardeners")
