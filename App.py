import streamlit as st
import requests
import datetime

# ==================== DATA IMPORTS ====================
try:
    from vegetable_data import vegetables
    from herb_data import herbs
    from flower_data import flowers
    # Combine them for the search/build tab
    all_plants = vegetables + herbs + flowers
except ImportError as e:
    st.error(f"Missing a data file: {e}")
    all_plants = []

st.set_page_config(page_title="ZipPlant 🌱", layout="centered", page_icon="🌱")

# ==================== THEME ====================
st.markdown("""
<style>
    .stApp { background-color: #0b0f14; color: #e6edf3; }
    h1, h2, h3 { color: #9be28f; }
    .stButton>button { background: #1f6f4a; color: white; border-radius: 8px; border: none; width: 100%; }
    .stButton>button:hover { background: #2a8a5c; border: none; }
    .plant-card { background: #161b22; padding: 1.2rem; border-radius: 12px; border: 1px solid #2a3a2f; margin-bottom: 1rem; min-height: 100px; }
    .granny-box { background: #1f2a1f; padding: 1.2rem; border-radius: 12px; border: 2px solid #9be28f; margin-bottom: 1.5rem; }
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

st.title("ZipPlant 🌱")
st.markdown("**Find the best planting day • Build your garden • Grow smarter**")
st.divider()

tabs = st.tabs(["📍 Location", "🌱 Build Garden", "🌿 My Garden"])

# ==================== LOCATION TAB ====================
with tabs[0]:
    col1, col2 = st.columns([3, 1])
    with col1:
        zip_input = st.text_input("Enter ZIP Code", value=st.session_state.zip_code, max_chars=5)
    with col2:
        if st.button("Get Garden Forecast", type="primary"):
            st.session_state.zip_code = zip_input
            with st.spinner("Fetching garden intelligence..."):
                st.session_state.weather = get_weather(zip_input)
                st.session_state.zone = get_hardiness_zone(zip_input)

    if st.session_state.weather:
        w = st.session_state.weather
        st.markdown(f"<div class='granny-box'><strong>🌾 Granny Fanny says:</strong> You're in Zone <strong>{st.session_state.zone}</strong>.</div>", unsafe_allow_html=True)
        st.success(f"**Best Day to Plant:** {best_day(w)}")

        st.subheader("7-Day Garden Forecast")
        for i in range(7):
            date = format_date(w['time'][i])
            with st.expander(f"📅 {date} ({w['temperature_2m_min'][i]}° - {w['temperature_2m_max'][i]}°F)"):
                c = st.columns(4)
                c[0].metric("Rain", f"{w['precipitation_probability_max'][i]}%")
                c[1].metric("UV Max", f"{w['uv_index_max'][i]}")
                et0 = w['et0_fao_evapotranspiration'][i]
                c[2].metric("Thirst", f"{et0:.2f} in")
                c[3].metric("Wind", f"{w['wind_speed_10m_max'][i]} mph")
                
                thirst_val = min(int(et0 * 25), 100)
                st.progress(thirst_val, text=f"Thirst Meter: {thirst_val}%")

# ==================== BUILD GARDEN TAB ====================
with tabs[1]:
    search = st.text_input("🔍 Search Varieties", placeholder="Tomato, Basil, Flower...").lower()
    
    # We check both common_name and cultivar for a thorough search
    filtered = [p for p in all_plants if not search or 
                search in p.get('common_name', '').lower() or 
                search in p.get('cultivar', '').lower()]
    
    cols = st.columns(2)
    for idx, p in enumerate(filtered):
        p_name = p.get('common_name', 'Unknown')
        p_cultivar = p.get('cultivar', '')
        with cols[idx % 2]:
            st.markdown(f"""
            <div class='plant-card'>
                <strong>{p_name}</strong><br>
                <small>{p_cultivar}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Use unique key based on index and name
            if st.button(f"Add {p_name}", key=f"add_{idx}_{p_name}"):
                st.session_state.garden.append(p)
                st.toast(f"✅ Added {p_name} to your garden!")

# ==================== MY GARDEN TAB ====================
with tabs[2]:
    if not st.session_state.garden:
        st.info("Your garden is empty. Add plants in the 'Build Garden' tab!")
    else:
        st.subheader(f"My Garden ({len(st.session_state.garden)} plants)")
        for i, p in enumerate(st.session_state.garden):
            with st.expander(f"🌱 {p.get('common_name')} - {p.get('cultivar')}"):
                st.markdown(f"**🌾 Granny Fanny says:** *{p.get('granny_fanny', 'A fine addition to the homestead!')}*")
                st.write(f"**Spacing (Grid):** {p.get('spacing_grid', 'N/A')}")
                st.write(f"**Method:** {p.get('method', 'N/A')}")
                if st.button("🗑️ Remove", key=f"rm_{i}"):
                    st.session_state.garden.pop(i)
                    st.rerun()

st.caption("Made with ❤️ for Liz")
