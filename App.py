import streamlit as st
import requests
import datetime
from plants_data import plants   # ← This pulls from the separate file

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
</style>
""", unsafe_allow_html=True)

# ==================== HELPERS ====================
def get_weather(zip_code):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}&count=1").json()
        if "results" not in geo: return None
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit"
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
    scores = [weather["temperature_2m_min"][i] - (weather["precipitation_probability_max"][i] * 0.8) for i in range(7)]
    best_idx = scores.index(max(scores))
    return format_date(weather["time"][best_idx])

# ==================== STATE ====================
if "garden" not in st.session_state:
    st.session_state.garden = []
if "weather" not in st.session_state:
    st.session_state.weather = None
if "zone" not in st.session_state:
    st.session_state.zone = None

st.title("ZipPlant 🌱")
st.markdown("**Find the best planting day • Build your garden • Grow smarter**")
st.divider()

tabs = st.tabs(["📍 Location", "🌱 Build Garden", "🌿 My Garden"])

# ==================== LOCATION TAB ====================
with tabs[0]:
    col1, col2 = st.columns([3, 1])
    with col1:
        zip_code = st.text_input("Enter ZIP Code", placeholder="37013", max_chars=5)
    with col2:
        if st.button("Get Forecast", use_container_width=True):
            with st.spinner("Fetching..."):
                st.session_state.weather = get_weather(zip_code)
                st.session_state.zone = get_hardiness_zone(zip_code)

    if st.session_state.weather:
        zone = st.session_state.zone
        st.markdown(f"""
        <div class="granny-box">
            <strong>🌾 Granny Fanny says:</strong><br>
            You are in USDA Hardiness Zone <span style="color:#9be28f; font-size:1.2em;">{zone}</span>.<br>
            That's a wonderful zone for growing all sorts of delicious things, sweetie.
        </div>
        """, unsafe_allow_html=True)

        st.success(f"**Best planting day: {best_day(st.session_state.weather)}**")
        
        st.subheader("7-Day Forecast")
        for i in range(7):
            date = format_date(st.session_state.weather['time'][i])
            temp = st.session_state.weather['temperature_2m_min'][i]
            rain = st.session_state.weather['precipitation_probability_max'][i]
            with st.container():
                st.markdown(f"<div style='background:#161b22; padding:1rem; border-radius:12px; margin-bottom:0.8rem; border:1px solid #2a3a2f;'><strong>{date}</strong></div>", unsafe_allow_html=True)
                col_t, col_r = st.columns([1, 3])
                with col_t: st.write(f"🌡️ **{temp}°F**")
                with col_r: st.write(f"🌧️ Rain chance: **{rain}%**")
                if rain > 70: st.warning("High rain chance")
                elif rain > 40: st.info("Moderate rain chance")
                st.divider()

# ==================== BUILD GARDEN TAB ====================
with tabs[1]:
    st.subheader("Available Plants")
    search_term = st.text_input("🔍 Search plants", placeholder="tomato, basil, okra...")
    
    colf1, colf2 = st.columns(2)
    with colf1:
        category = st.selectbox("Category", ["All", "Tomatoes", "Peppers", "Herbs", "Greens", "Roots", "Vegetables"])
    with colf2:
        sun_pref = st.selectbox("Sun Preference", ["Any", "Full sun", "Partial"])

    filtered = [p for p in plants if 
                (not search_term or search_term.lower() in p["name"].lower() or search_term.lower() in p.get("type","").lower()) and
                (category == "All" or category.lower() in p["type"].lower()) and
                (sun_pref == "Any" or sun_pref.lower() in p["sun"].lower())]

    if not filtered:
        st.info("No plants found. Try broadening your search.")
    else:
        cols = st.columns(2)
        for idx, p in enumerate(filtered):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"""
                    <div class="plant-card">
                        <h3>{p['name']}</h3>
                        <small><em>{p['type']}</em></small><br>
                        <em>{p['pitch']}</em>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write(f"**Spacing:** {p['spacing']}")
                    st.write(f"**Sun:** {p['sun']}")
                    st.write(f"**Harvest:** {p['harvest_days']}")
                    if p["name"] not in [g["name"] for g in st.session_state.garden]:
                        if st.button("Add to Garden", key=f"add_{idx}"):
                            st.session_state.garden.append(p)
                            st.rerun()
                    else:
                        st.success("✓ Already in garden")

# ==================== MY GARDEN TAB ====================
with tabs[2]:
    if not st.session_state.garden:
        st.info("Your garden is empty. Go add some plants!")
    else:
        st.subheader(f"My Garden ({len(st.session_state.garden)} plants)")
        for i, p in enumerate(st.session_state.garden[:]):
            with st.expander(f"🌱 {p['name']}", expanded=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    if st.session_state.weather:
                        st.markdown(f"<span class='success-msg'>🌾 Best day to plant: {best_day(st.session_state.weather)}</span>", unsafe_allow_html=True)
                    st.write(f"**Spacing:** {p['spacing']}")
                    st.write(f"**For a couple:** {p['couple']}")
                    st.write(f"**For family of 4:** {p['family4']}")
                    st.write(f"**Start:** {p['start']}")
                    st.write(f"**Care:** {p['care']}")
                    st.write(f"**Harvest window:** {p['harvest_window']}")
                    st.write(f"**Expected yield:** {p['yield']}")
                    st.write(f"**Companions:** {', '.join(p['companions']) if p['companions'] else 'None listed'}")
                    st.write(f"**Avoid:** {', '.join(p['avoid']) if p['avoid'] else 'None listed'}")
                    st.markdown(f"**🌾 Granny Fanny says:** *{p['granny_says']}*")
                with col_b:
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.garden.pop(i)
                        st.rerun()

st.caption("Made with ❤️ for gardeners")
