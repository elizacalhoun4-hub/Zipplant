import streamlit as st
import requests
from plants_data import plants

st.set_page_config(page_title="ZipPlant", layout="centered")

# ---------- HARD THEME LOCK ----------
st.markdown("""
<style>

/* GLOBAL */
html, body, [class*="css"] {
    background-color: #0b0f14 !important;
    color: #e6edf3 !important;
}

/* MAIN APP */
.stApp {
    background-color: #0b0f14 !important;
}

/* HEADERS */
h1, h2, h3 {
    color: #9be28f !important;
}

/* CARDS */
div[data-testid="stVerticalBlock"] > div {
    background: #111826 !important;
    border: 1px solid #1f2a3a !important;
    border-radius: 14px !important;
    padding: 14px !important;
    margin-bottom: 12px !important;
}

/* BUTTONS */
button {
    background-color: #1f6f4a !important;
    color: white !important;
    border-radius: 8px !important;
}

/* SUCCESS BOX */
.stSuccess {
    background-color: #133d2b !important;
    color: #9be28f !important;
}

/* INPUTS */
input {
    background-color: #111826 !important;
    color: #e6edf3 !important;
}

/* SELECT BOX */
div[data-baseweb="select"] {
    background-color: #111826 !important;
}

/* EXPANDERS */
details {
    background-color: #111826 !important;
    border-radius: 10px;
    padding: 8px;
}

</style>
""", unsafe_allow_html=True)

# ---------- WEATHER ----------
def get_weather(zip):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip}").json()
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit"
        r = requests.get(url).json()

        return r["daily"]
    except:
        return None

def planting_score(temp, rain):
    if temp < 36:
        return "❌ Too cold"
    if rain > 70:
        return "❌ Heavy rain"
    if temp < 50 or rain > 40:
        return "⚠️ Caution"
    return "✅ Good"

# ---------- TYPES ----------
TYPE_OPTIONS = {
    "tomato": ["Slicing","Paste","Cherry"],
    "pepper": ["Bell","Hot","Sweet","Wax"],
    "lettuce": ["Romaine","Leaf","Butterhead"],
    "basil": ["Genovese","Thai","Lemon"],
    "parsley": ["Flat Leaf","Curly"]
}

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("ZipPlant 🌱")
tabs = st.tabs(["Location","Build","Garden"])

# ---------- LOCATION ----------
with tabs[0]:
    zip = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        st.session_state.weather = get_weather(zip)

    if "weather" in st.session_state and st.session_state.weather:
        for i in range(7):
            temp = st.session_state.weather["temperature_2m_min"][i]
            rain = st.session_state.weather["precipitation_probability_max"][i]
            date = st.session_state.weather["time"][i]

            st.write(f"{date} — {temp}°F | Rain {rain}% → {planting_score(temp,rain)}")

# ---------- BUILD ----------
with tabs[1]:

    group_filter = st.selectbox("Group",["All","Vegetable","Herb","Flower"])
    type_filter = st.selectbox("Category",["All","Root","Leafy","Fruit"])

    for i,p in enumerate(plants):

        if group_filter != "All" and p["group"] != group_filter:
            continue
        if type_filter != "All" and p["category"] != type_filter:
            continue

        st.subheader(p["name"])

        plant_type = None
        for key in TYPE_OPTIONS:
            if key in p["name"].lower():
                plant_type = st.selectbox("Type", TYPE_OPTIONS[key], key=f"type{i}")

        final_name = f"{p['name']} - {plant_type}" if plant_type else p["name"]

        if final_name in [g["name"] for g in st.session_state.garden]:
            st.success("Added")
        else:
            if st.button("Add", key=i):
                st.session_state.garden.append({
                    "name": final_name,
                    "data": p
                })

# ---------- GARDEN ----------
with tabs[2]:

    if not st.session_state.garden:
        st.info("Add plants first")
    else:
        for g in st.session_state.garden:

            p = g["data"]

            st.subheader(g["name"])

            if "weather" in st.session_state and st.session_state.weather:
                temp = st.session_state.weather["temperature_2m_min"][0]
                rain = st.session_state.weather["precipitation_probability_max"][0]
                st.success(planting_score(temp,rain))

            st.write("🌱 Method:", p["method"])
            st.write("📏 Spacing:", p["spacing"])
            st.write("🌞 Sun:", p["sun"])
            st.write("💧 Water:", p["water"])
            st.write("🌿 Soil:", p["soil"])

            st.write("⏳ Harvest:", p["harvest_days"], "days")
            st.write("📦 Yield:", p["yield"])
            st.write("🥫 Storage:", p["storage"])

            st.write("🌿 Care:", p["care"])

            st.write("🤝 Companions:", ", ".join(p["companions"]) if p["companions"] else "None")
            st.write("🚫 Avoid:", ", ".join(p["avoid"]) if p["avoid"] else "None")

            if p["cultivars"]:
                with st.expander("Cultivars"):
                    for c in p["cultivars"]:
                        st.write(f"{c['name']} — {c['description']}")

            if "granny_fanny" in p:
                st.markdown(f"💬 *Granny Fanny says:* {p['granny_fanny']}")

            st.divider()
