import streamlit as st
import requests
import datetime

# ==================== DATA IMPORTS ====================
try:
    from vegetable_data import vegetables
    from herb_data import herbs
    from flower_data import flowers
except ImportError as e:
    st.error(f"Missing Data File: {e}")
    vegetables, herbs, flowers = [], [], []

st.set_page_config(page_title="Liz's Homestead Planner", layout="centered", page_icon="🌱")

# ==================== PROFESSIONALLY UPGRADED THEME ====================
st.markdown("""
<style>
    .stApp { background-color: #0b0f14; color: #e6edf3; }
    h1, h2, h3 { color: #9be28f; }
    .stButton>button { background: #1f6f4a; color: white; border-radius: 8px; border: none; width: 100%; }
    .plant-card { background: #161b22; padding: 1rem; border-radius: 12px; border: 1px solid #2a3a2f; margin-bottom: 0.5rem; }
    .granny-box { background: #1f2a1f; padding: 1.2rem; border-radius: 12px; border: 2px solid #9be28f; margin-bottom: 1rem; font-size: 1.05em; }
    .alert-banner { background: #4a1f1f; padding: 1rem; border-radius: 12px; border: 2px solid #ff6b6b; margin-bottom: 1rem; }
    .field-label { color: #9be28f; font-weight: bold; }
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
    except: return None

def get_hardiness_zone(zip_code):
    try:
        r = requests.get(f"https://phzmapi.org/{zip_code}.json", timeout=5)
        return r.json().get("zone", "Unknown")
    except: return "Unknown"

def format_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d")

def best_day(weather):
    scores = [weather["temperature_2m_min"][i] - (weather["precipitation_probability_max"][i] * 0.9) for i in range(7)]
    best_idx = scores.index(max(scores))
    return format_date(weather["time"][best_idx])

# ==================== STATE ====================
if "garden" not in st.session_state: st.session_state.garden = []
if "weather" not in st.session_state: st.session_state.weather = None
if "zone" not in st.session_state: st.session_state.zone = None
if "zip_code" not in st.session_state: st.session_state.zip_code = ""

st.title("Liz's Homestead Planner")
st.divider()

main_tabs = st.tabs(["📍 Location", "🌱 Build Garden", "🌿 My Garden"])

# ==================== LOCATION TAB (FULL WEATHER VERSION) ====================
with main_tabs[0]:
    col1, col2 = st.columns([3, 1])
    with col1:
        zip_input = st.text_input("Enter ZIP Code", value=st.session_state.zip_code, max_chars=5)
    with col2:
        if st.button("Get Forecast", type="primary"):
            st.session_state.zip_code = zip_input
            with st.spinner("Fetching garden intelligence..."):
                st.session_state.weather = get_weather(zip_input)
                st.session_state.zone = get_hardiness_zone(zip_input)

    if st.session_state.weather:
        w = st.session_state.weather
        st.markdown(f"<div class='granny-box'><strong>🌾 Granny Fanny says:</strong> You're in Zone <strong>{st.session_state.zone}</strong>.</div>", unsafe_allow_html=True)
        st.success(f"**Best Day to Plant this week:** {best_day(w)}")

        st.subheader("7-Day Garden Forecast")
        for i in range(7):
            date = format_date(w['time'][i])
            tmin, tmax = w['temperature_2m_min'][i], w['temperature_2m_max'][i]
            et0, uv = w['et0_fao_evapotranspiration'][i], w['uv_index_max'][i]
            
            with st.expander(f"📅 {date} — {tmin}°F to {tmax}°F", expanded=(i == 0)):
                cols = st.columns(4)
                cols[0].metric("Rain", f"{w['precipitation_probability_max'][i]}%")
                cols[1].metric("UV Max", str(uv))
                cols[2].metric("Thirst", f"{et0:.2f} in")
                cols[3].metric("Wind", f"{w['wind_speed_10m_max'][i]} mph")
                
                thirst_val = min(int(et0 * 25), 100)
                st.progress(thirst_val, text=f"Thirst Meter: {thirst_val}%")
                
                if uv >= 8:
                    st.warning("☀️ **Granny says:** Sun is fierce today! Mind your delicate starters.")

# ==================== BUILD GARDEN TAB ====================
with main_tabs[1]:
    st.subheader("Add Varieties to Your Homestead")
    sub_tabs = st.tabs(["🥕 Add Vegetables", "🌿 Add Herbs", "🌸 Add Flowers"])

    def render_build_section(data, key_prefix):
        cols = st.columns(2)
        for idx, p in enumerate(data):
            with cols[idx % 2]:
                st.markdown(f"<div class='plant-card'><strong>{p.get('common_name')}</strong><br><small>{p.get('cultivar')}</small></div>", unsafe_allow_html=True)
                if st.button("Add to Garden", key=f"{key_prefix}_{idx}"):
                    st.session_state.garden.append(p)
                    st.toast(f"✅ {p.get('common_name')} added!")

    with sub_tabs[0]: render_build_section(vegetables, "v")
    with sub_tabs[1]: render_build_section(herbs, "h")
    with sub_tabs[2]: render_build_section(flowers, "f")

# ==================== MY GARDEN TAB (FIELD GUIDE) ====================
with main_tabs[2]:
    st.subheader(f"In My Garden ({len(st.session_state.garden)} plants)")
    for i, p in enumerate(st.session_state.garden):
        with st.expander(f"🌱 {p.get('common_name')} - {p.get('cultivar')}", expanded=True):
            st.markdown(f"**🌾 Granny Fanny says:** *{p.get('granny_fanny', 'A fine choice!')}*")
            
            # Formatted list of all your specified fields
            labels = ["Scientific Name", "Cultivar", "Type", "Growth Habit", "Method", "Depth", 
                      "Spacing (Traditional)", "Spacing (Grid)", "Care", "Days to Harvest", 
                      "Harvest Indicators", "Yield for Couple", "Yield for Family of 4", 
                      "When to Pick", "Preservation", "Companions", "No-Go"]
            keys = ["scientific_name", "cultivar", "type", "growth_habit", "method", "depth", 
                    "spacing_traditional", "spacing_grid", "care", "days_to_harvest", 
                    "harvest_indicators", "yield_family_2", "yield_family_4", 
                    "when_to_pick", "preservation", "companions", "no_go"]

            for label, key in zip(labels, keys):
                val = p.get(key, "N/A")
                if isinstance(val, list): val = ", ".join(val)
                st.markdown(f"**{label}:** {val}")

            if st.button("🗑️ Remove", key=f"rm_{i}"):
                st.session_state.garden.pop(i)
                st.rerun()

st.caption("Made with ❤️ for gardeners")
