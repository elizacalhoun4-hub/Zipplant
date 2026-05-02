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
    .stButton>button {
        background: #1f6f4a;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .plant-card {
        background: #161b22;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #2a3a2f;
        margin-bottom: 1rem;
    }
    .success-msg { color: #9be28f; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ==================== HELPERS ====================
def get_weather(zip_code):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}&count=1").json()
        if "results" not in geo:
            return None
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit"
        r = requests.get(url).json()
        return r["daily"]
    except:
        return None

def format_date(date_str):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%B %d")

def best_day(weather):
    scores = [weather["temperature_2m_min"][i] - (weather["precipitation_probability_max"][i] * 0.8) 
              for i in range(7)]
    best_idx = scores.index(max(scores))
    return format_date(weather["time"][best_idx])

# ==================== STATE ====================
if "garden" not in st.session_state:
    st.session_state.garden = []
if "weather" not in st.session_state:
    st.session_state.weather = None

# ==================== UI ====================
st.title("ZipPlant 🌱")
st.markdown("**Find the best planting day • Build your garden • Grow smarter**")
st.divider()

tabs = st.tabs(["📍 Location", "🌱 Build Garden", "🌿 My Garden"])

# ---------- LOCATION ----------
with tabs[0]:
    col1, col2 = st.columns([3, 1])
    with col1:
        zip_code = st.text_input("Enter ZIP Code", placeholder="37013", max_chars=5)
    with col2:
        if st.button("Get Forecast", use_container_width=True):
            with st.spinner("Fetching weather..."):
                st.session_state.weather = get_weather(zip_code)

    if st.session_state.weather:
        st.success(f"**Best planting day:** {best_day(st.session_state.weather)}")
        st.subheader("7-Day Forecast")
        cols = st.columns(7)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"**{format_date(st.session_state.weather['time'][i])}**")
                st.write(f"🌡️ {st.session_state.weather['temperature_2m_min'][i]}°F")
                st.write(f"🌧️ {st.session_state.weather['precipitation_probability_max'][i]}%")
    else:
        st.info("Enter your ZIP code ↑ and click Get Forecast")

# ---------- BUILD GARDEN ----------
with tabs[1]:
    st.subheader("Available Plants")
    cols = st.columns(2)
    for idx, plant in enumerate(plants):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="plant-card">
                    <h3>{plant['name']}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**Spacing:** {plant['spacing']}")
            st.write(f"**Sun:** {plant['sun']}")
            st.write(f"**Harvest:** {plant['harvest_days']}")
            
            if plant["name"] in [g["name"] for g in st.session_state.garden]:
                st.success("✓ Already in garden")
            else:
                if st.button("Add to Garden", key=f"add_{idx}"):
                    st.session_state.garden.append(plant)
                    st.rerun()

# ---------- MY GARDEN ----------
with tabs[2]:
    if not st.session_state.garden:
        st.info("Your garden is empty. Add some plants!")
    else:
        st.subheader(f"My Garden ({len(st.session_state.garden)} plants)")
        for i, plant in enumerate(st.session_state.garden[:]):
            with st.expander(f"🌱 {plant['name']}", expanded=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    if st.session_state.weather:
                        st.markdown(f"<span class='success-msg'>Best day to plant: {best_day(st.session_state.weather)}</span>", unsafe_allow_html=True)
                    st.write(f"**Spacing:** {plant['spacing']}")
                    st.write(f"**Depth:** {plant['depth']}")
                    st.write(f"**Sun:** {plant['sun']}")
                    st.write(f"**Water:** {plant['water']}")
                    st.write(f"**Harvest:** {plant['harvest_days']} — {plant['yield']}")
                    st.write(f"**Companions:** {', '.join(plant['companions'])}")
                    st.write(f"**Avoid:** {', '.join(plant['avoid'])}")
                    st.write(f"**Care:** {plant['care']}")
                with col_b:
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.garden.pop(i)
                        st.rerun()

st.caption("Made with ❤️ for gardeners")
