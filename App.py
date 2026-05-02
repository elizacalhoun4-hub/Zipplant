import streamlit as st
import requests
import datetime
from plants_data import plants

st.set_page_config(page_title="ZipPlant", layout="centered")

# ---------- TYPE OPTIONS ----------
TYPE_OPTIONS = {
    "tomato": ["Slicing", "Paste", "Cherry"],
    "pepper": ["Bell", "Hot", "Sweet", "Wax"],
    "lettuce": ["Romaine", "Leaf", "Butterhead"],
    "basil": ["Genovese", "Thai", "Lemon"],
    "parsley": ["Flat Leaf", "Curly"]
}

# ---------- WEATHER ----------
def geocode(zipcode):
    r = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zipcode}").json()
    return r["results"][0]["latitude"], r["results"][0]["longitude"]

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min&temperature_unit=fahrenheit"
    r = requests.get(url).json()
    return r["daily"]["temperature_2m_min"]

def planting_day(name, temps):
    n = name.lower()

    for i, t in enumerate(temps[:7]):
        if "lettuce" in n and t > 45:
            return i
        if "tomato" in n and t > 60:
            return i
        if "pepper" in n and t > 65:
            return i

    return 0

# ---------- GARDEN INFO ----------
def garden_info(name):
    n = name.lower()

    if "tomato" in n:
        return ("2-4 per person","4-6","8-12","Can, freeze, dry","Stake and prune")
    if "pepper" in n:
        return ("1-2 per person","2-4","6-8","Freeze, pickle","Warm soil")
    if "lettuce" in n:
        return ("6-10 per person","10-15","20-30","Refrigerate","Cool weather")

    return ("Varies","Varies","Varies","Mixed storage","General care")

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("ZipPlant")
tabs = st.tabs(["Location","Build","Garden"])

# ---------- LOCATION ----------
with tabs[0]:
    zipcode = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zipcode)
        st.session_state.weather = get_weather(lat, lon)

    if "weather" in st.session_state:
        st.write("7 Day Forecast (F):")
        st.write(st.session_state.weather[:7])

# ---------- BUILD ----------
with tabs[1]:
    for i, p in enumerate(plants):

        st.subheader(p["name"])

        key = p["name"].lower()
        plant_type = None

        for k in TYPE_OPTIONS:
            if k in key:
                plant_type = st.selectbox(
                    "Choose type",
                    TYPE_OPTIONS[k],
                    key=f"type_{i}"
                )

        entry_name = f"{p['name']} - {plant_type}" if plant_type else p["name"]

        if entry_name in [g["name"] for g in st.session_state.garden]:
            st.success("Added")
        else:
            if st.button("Add", key=i):
                st.session_state.garden.append({
                    "name": entry_name,
                    "base": p["name"],
                    "type": plant_type
                })

# ---------- GARDEN ----------
with tabs[2]:

    if "weather" not in st.session_state:
        st.info("Enter ZIP first")
    else:
        for p in st.session_state.garden:

            st.subheader(p["name"])

            day = planting_day(p["name"], st.session_state.weather)

            if day == 0:
                st.success("Plant today")
            else:
                st.warning(f"Wait {day} days")

            info = garden_info(p["name"])

            st.write("Per Person:", info[0])
            st.write("Family of 2:", info[1])
            st.write("Family of 4:", info[2])

            st.write("Storage:", info[3])
            st.write("Care:", info[4])

            st.divider()
