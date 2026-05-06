import streamlit as st
import requests
import datetime
from vegetable_data import vegetables
from herb_data import herbs
from flower_data import flowers

st.set_page_config(page_title="ZipPlant 🌱", layout="centered", page_icon="🌱")

# ==================== THEME ====================
st.markdown("""
<style>
    .stApp { background-color: #0b0f14; color: #e6edf3; }
    h1, h2, h3 { color: #9be28f; }
    .stButton>button { background: #1f6f4a; color: white; border-radius: 8px; padding: 0.5rem 1rem; }
    .plant-card { background: #161b22; padding: 1.2rem; border-radius: 12px; border: 1px solid #2a3a2f; margin-bottom: 1rem; }
    .granny-box { background: #1f2a1f; padding: 1.2rem; border-radius: 12px; border: 2px solid #9be28f; margin-bottom: 1.5rem; font-size: 1.05em; }
    .alert-banner { background: #4a1f1f; padding: 1rem; border-radius: 12px; border: 2px solid #ff6b6b; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ==================== HELPERS ====================
def get_weather(zip_code):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}&count=1").json()
        if "results" not in geo or not geo["results"]: return None
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
        return "🔴 Too chilly! Wait until it hits 60°F.", "Soil is still sleeping."
    elif temp_f < 60:
        return "🟡 Marginal", "Good for cool crops only."
    else:
        return "🟢 Warm enough!", "Roots will wake up and grow strong."

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

# ==================== LOCATION TAB - FULL RICH VERSION (UNCHANGED) ====================
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

        for alert in get_alerts(w)[:3]:
            st.markdown(f"<div class='alert-banner'>{alert}</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="granny-box">
            <strong>🌾 Granny Fanny says:</strong><br>
            You are in USDA Hardiness Zone <span style="color:#9be28f; font-size:1.2em;">{zone}</span>.<br>
            That's a wonderful zone for growing all sorts of delicious things, sweetie.
        </div>
        """, unsafe_allow_html=True)

        st.success(f"**Best planting day: {best_day(w)}**")

        today_soil = w["temperature_2m_min"][0] - 5
        status, advice = soil_readiness(today_soil)
        st.markdown(f"""
        <div style="background:#1f2a1f; padding:1.2rem; border-radius:12px; border:2px solid #9be28f; margin:1rem 0;">
            <h3>🌱 Soil Readiness Today</h3>
            <h2>{status}</h2>
            <p>{advice}</p>
            <small>Estimated surface soil temp: \~{today_soil:.0f}°F</small>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("7-Day Garden Forecast")
        for i in range(7):
            date = format_date(w['time'][i])
            tmin = w['temperature_2m_min'][i]
            tmax = w.get('temperature_2m_max', [tmin+15]*7)[i]
            rain_prob = w['precipitation_probability_max'][i]
            rain_in = w['precipitation_sum'][i]
            et0 = w.get('et0_fao_evapotranspiration', [0]*7)[i]
            uv = w.get('uv_index_max', [0]*7)[i]
            wind = w.get('wind_speed_10m_max', [0]*7)[i]
            sunrise = w['sunrise'][i][-5:]
            sunset = w['sunset'][i][-5:]

            with st.expander(f"**{date}** — {tmin}°F to {tmax}°F", expanded=(i == 0)):
                cols = st.columns(4)
                with cols[0]: st.metric("🌡️ Low/High", f"{tmin}° / {tmax}°F")
                with cols[1]: st.metric("🌧️ Rain", f"{rain_prob}% ({rain_in:.2f} in)")
                with cols[2]: st.metric("☀️ UV Max", str(uv))
                with cols[3]: st.metric("💧 ET₀", f"{et0:.2f} in")

                st.write(f"**Daylight:** {sunrise} — {sunset}")
                st.write(f"**Wind:** {wind} mph")

                thirst = min(int(et0 * 25), 100)
                st.progress(thirst, text=f"Thirst Meter: {thirst}% — {'Water deeply today' if thirst > 60 else 'Normal watering'}")

                if uv >= 8:
                    st.warning("☀️ **Granny says:** Strong sun today! Don't leave your indoor babies out for more than an hour or they’ll sunburn!")

        total_rain = sum(w['precipitation_sum'])
        avg_et0 = sum(w.get('et0_fao_evapotranspiration', [0]*7)) / 7
        st.info(f"**Week Summary:** {total_rain:.2f} inches expected rain • Avg ET₀ {avg_et0:.2f} in/day")

# ==================== BUILD GARDEN TAB - NEW SUB-TABS (VEGETABLES / HERBS / FLOWERS) ====================
with tabs[1]:
    st.subheader("Build Your Garden")
    veg_tab, herb_tab, flower_tab = st.tabs(["🥕 Add Vegetables", "🌿 Add Herbs", "🌸 Add Flowers"])

    def add_to_garden(plant):
        if not any(g.get("common_name") == plant.get("common_name") for g in st.session_state.garden):
            st.session_state.garden.append(plant.copy())
            st.rerun()

    # ====================== VEGETABLES TAB ======================
    with veg_tab:
        veg_search = st.text_input("🔍 Search vegetables", placeholder="tomato, pepper, squash...", key="veg_search")
        filtered_veg = [
            p for p in vegetables
            if not veg_search or veg_search.lower() in p["common_name"].lower() or veg_search.lower() in p.get("cultivar", "").lower()
        ]
        if not filtered_veg:
            st.info("No vegetables found. Try broadening your search.")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(filtered_veg):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="plant-card">
                        <h3>🥕 {p['common_name']}</h3>
                        <small><em>{p['type']} • {p['cultivar']}</em></small><br>
                        <em>{p['granny_fanny'][:110]}...</em>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"**Days to Harvest:** {p['days_to_harvest']} | **Type:** {p['type']}")
                    if not any(g.get("common_name") == p["common_name"] for g in st.session_state.garden):
                        if st.button("➕ Add to My Garden", key=f"add_veg_{idx}", use_container_width=True):
                            add_to_garden(p)
                    else:
                        st.success("✅ Already in garden")

    # ====================== HERBS TAB ======================
    with herb_tab:
        herb_search = st.text_input("🔍 Search herbs", placeholder="basil, cilantro, rosemary...", key="herb_search")
        filtered_herb = [
            p for p in herbs
            if not herb_search or herb_search.lower() in p["common_name"].lower() or herb_search.lower() in p.get("cultivar", "").lower()
        ]
        if not filtered_herb:
            st.info("No herbs found. Try broadening your search.")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(filtered_herb):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="plant-card">
                        <h3>🌿 {p['common_name']}</h3>
                        <small><em>{p['type']} • {p['cultivar']}</em></small><br>
                        <em>{p['granny_fanny'][:110]}...</em>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"**Days to Harvest:** {p['days_to_harvest']} | **Type:** {p['type']}")
                    if not any(g.get("common_name") == p["common_name"] for g in st.session_state.garden):
                        if st.button("➕ Add to My Garden", key=f"add_herb_{idx}", use_container_width=True):
                            add_to_garden(p)
                    else:
                        st.success("✅ Already in garden")

    # ====================== FLOWERS TAB ======================
    with flower_tab:
        flower_search = st.text_input("🔍 Search flowers", placeholder="marigold, zinnia, sunflower...", key="flower_search")
        filtered_flower = [
            p for p in flowers
            if not flower_search or flower_search.lower() in p["common_name"].lower() or flower_search.lower() in p.get("cultivar", "").lower()
        ]
        if not filtered_flower:
            st.info("No flowers found. Try broadening your search.")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(filtered_flower):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="plant-card">
                        <h3>🌸 {p['common_name']}</h3>
                        <small><em>{p['type']} • {p['cultivar']}</em></small><br>
                        <em>{p['granny_fanny'][:110]}...</em>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"**Days to Bloom:** {p['days_to_harvest']} | **Type:** {p['type']}")
                    if not any(g.get("common_name") == p["common_name"] for g in st.session_state.garden):
                        if st.button("➕ Add to My Garden", key=f"add_flower_{idx}", use_container_width=True):
                            add_to_garden(p)
                    else:
                        st.success("✅ Already in garden")

# ==================== MY GARDEN TAB - EXACT MOCKUP LAYOUT ====================
with tabs[2]:
    if not st.session_state.garden:
        st.info("Your garden is empty. Go add some plants from the Build Garden tab!")
    else:
        st.subheader(f"My Garden ({len(st.session_state.garden)} plants)")
        for i, p in enumerate(st.session_state.garden[:]):
            # Determine emoji for header
            common_lower = p["common_name"].lower()
            if "tomato" in common_lower:
                emoji = "🍅"
            elif "pepper" in common_lower:
                emoji = "🌶️"
            elif "basil" in common_lower or "herb" in p.get("type", "").lower():
                emoji = "🌿"
            elif any(x in common_lower for x in ["marigold", "zinnia", "sunflower", "nasturtium"]):
                emoji = "🌸"
            else:
                emoji = "🌱"

            header_title = f"{emoji} {p['common_name']}"

            with st.expander(header_title, expanded=True):
                # Granny Fanny highlight (exact mockup style)
                st.markdown(f"""
                <div class="granny-box">
                    <strong>🌾 Granny Fanny says:</strong> <em>{p.get('granny_fanny', 'Great choice for your homestead!')}</em>
                </div>
                """, unsafe_allow_html=True)

                # Detailed vertical field guide
                st.write(f"**Scientific Name:** {p['scientific_name']}")
                st.write(f"**Cultivar:** {p['cultivar']}")
                st.write(f"**Type:** {p['type']}")
                st.write(f"**Growth Habit:** {p['growth_habit']}")

                st.write(f"**Method:** {p['method']}")
                st.write(f"**Depth:** {p['depth']}")
                st.write(f"**Spacing (Traditional):** {p['spacing_traditional']}")
                st.write(f"**Spacing (Grid):** {p['spacing_grid']}")

                st.write(f"**Care:** {p['care']}")
                st.write(f"**Days to Harvest:** {p['days_to_harvest']}")
                st.write(f"**Harvest Indicators:** {p['harvest_indicators']}")

                st.write(f"**Yield for Couple:** {p.get('yield_family_2', 'N/A')}")
                st.write(f"**Yield for Family of 4:** {p.get('yield_family_4', 'N/A')}")
                st.write(f"**When to Pick:** {p.get('when_to_pick', 'Mid-summer through first frost.')}")

                st.write(f"**Preservation:** {p['preservation']}")
                st.write(f"**Companions:** {', '.join(p.get('companions', [])) or 'None listed'}")
                st.write(f"**No-Go:** {', '.join(p.get('no_go', [])) or 'None listed'}")

                # Remove button (exact mockup style)
                if st.button("🗑️ Remove", key=f"remove_{i}", use_container_width=True):
                    st.session_state.garden.pop(i)
                    st.rerun()

st.caption("Made with ❤️ for gardeners")
