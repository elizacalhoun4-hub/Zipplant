# ZipPlant Full App (Stable Version)

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

def next_good_day(weather):
    for i in range(len(weather["time"])):
        t = weather["temperature_2m_min"][i]
        r = weather["precipitation_probability_max"][i]
        if t > 50 and r < 40:
            return format_date(weather["time"][i])
    return "No good day soon"

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
                st.session_state.weather["temperature_2m_min"][i],
                "F | Rain",
                st.session_state.weather["precipitation_probability_max"][i],
                "%"
            )

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
            st.success("Next planting: " + next_good_day(st.session_state.weather))

        st.write("Spacing:", p["spacing"])
        st.write("Depth:", p["depth"])
        st.write("Sun:", p["sun"])
        st.write("Water:", p["water"])
        st.write("Harvest:", p["harvest_days"])
        st.write("Yield:", p["yield"])

        st.write("Companions:", ", ".join(p.get("companions", [])))
        st.write("Avoid:", ", ".join(p.get("avoid", [])))

        if p.get("granny_fanny"):
            st.write("Granny Fanny:", p["granny_fanny"])

        st.divider()
