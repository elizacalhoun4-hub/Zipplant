import streamlit as st
import requests
import datetime
from plants_data import plants

st.set_page_config(page_title="ZipPlant", layout="centered")

# ---------- THEME ----------
st.markdown("""
<style>
.stApp { background-color: #0b0f14; color: #e6edf3; }
h1,h2,h3 { color:#9be28f; }
button { background:#1f6f4a !important; color:white !important; }
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

def format_date(date_str):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%B %d, %Y")

def planting_score(temp, rain):
    if temp < 45: return -100
    return temp - rain

def best_day(weather):
    scores = []
    for i in range(7):
        t = weather["temperature_2m_min"][i]
        r = weather["precipitation_probability_max"][i]
        scores.append(planting_score(t, r))

    best_index = scores.index(max(scores))
    return format_date(weather["time"][best_index])

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

st.title("ZipPlant 🌱")
tabs = st.tabs(["Location","Build","Garden"])

# ---------- LOCATION ----------
with tabs[0]:
    zip = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        st.session_state.weather = get_weather(zip)

    if "weather" in st.session_state:
        for i in range(7):
            st.write(
                format_date(st.session_state.weather["time"][i]),
                f"{st.session_state.weather['temperature_2m_min'][i]}°F",
                f"Rain {st.session_state.weather['precipitation_probability_max'][i]}%"
            )

        st.success(f"Best planting day: {best_day(st.session_state.weather)}")

# ---------- BUILD ----------
with tabs[1]:
    for i,p in enumerate(plants):
        st.subheader(p["name"])

        if p["name"] in [g["name"] for g in st.session_state.garden]:
            st.success("Added")
        else:
            if st.button("Add", key=i):
                st.session_state.garden.append(p)

# ---------- GARDEN ----------
with tabs[2]:
    for p in st.session_state.garden:
        st.subheader(p["name"])

        if "weather" in st.session_state:
            st.success(f"Plant on: {best_day(st.session_state.weather)}")

        st.write("Spacing:", p["spacing"])
        st.write("Depth:", p["depth"])
        st.write("Sun:", p["sun"])
        st.write("Water:", p["water"])
        st.write("Harvest:", p["harvest_days"])
        st.write("Yield:", p["yield"])

        st.write("Companions:", ", ".join(p["companions"]))
        st.write("Avoid:", ", ".join(p["avoid"]))

        st.write("Care:", p["care"])
        st.write("Harvest Method:", p["harvest_notes"])

        st.divider()