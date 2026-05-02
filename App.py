import streamlit as st
import requests
import datetime
from plants_data import plants as base_plants

st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# ---------- TYPE MAP ----------
TYPE_MAP = {
    "tomato": [("Slicing","Indeterminate"),("Paste","Determinate"),("Cherry","Indeterminate"),("Heirloom","Indeterminate")],
    "pepper": [("Bell",None),("Hot",None),("Sweet",None),("Wax",None)],
    "lettuce": [("Romaine",None),("Butterhead",None),("Leaf",None)],
    "basil": [("Genovese",None),("Thai",None),("Lemon",None),("Purple",None)],
    "parsley": [("Flat Leaf",None),("Curly",None)]
}

def expand_plants(plants):
    expanded = []
    for p in plants:
        name = p["name"].lower()
        matched = False

        for key in TYPE_MAP:
            if key in name:
                matched = True
                for subtype, growth in TYPE_MAP[key]:
                    new_p = p.copy()
                    new_p["name"] = f"{p['name']} — {subtype}"
                    new_p["subtype"] = subtype
                    if growth:
                        new_p["growth"] = growth
                    expanded.append(new_p)
                break

        if not matched:
            expanded.append(p)

    return expanded

plants = expand_plants(base_plants)

# ---------- WEATHER ----------
def geocode(zipcode):
    r = requests.get("https://geocoding-api.open-meteo.com/v1/search?name=" + zipcode).json()
    if "results" in r:
        return r["results"][0]["latitude"], r["results"][0]["longitude"]
    return None, None

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit&timezone=auto"
    r = requests.get(url).json()

    data = []
    for i in range(len(r["daily"]["time"])):
        data.append({
            "date": r["daily"]["time"][i],
            "temp": round(r["daily"]["temperature_2m_min"][i]),
            "rain": r["daily"]["precipitation_probability_max"][i]
        })
    return data

def plant_timing(p, weather):
    for i, d in enumerate(weather[:7]):
        temp = d["temp"]

        if "lettuce" in p["name"].lower() and temp > 45:
            return i

        if "tomato" in p["name"].lower() and temp > 60:
            return i

        if "pepper" in p["name"].lower() and temp > 65:
            return i

    return 0

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("ZipPlant 🌱")
tabs = st.tabs(["Location","Build","Garden"])

# ---------- LOCATION ----------
with tabs[0]:
    zipcode = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zipcode)
        if lat:
            st.session_state.weather = get_weather(lat, lon)

# ---------- BUILD ----------
with tabs[1]:
    for i,p in enumerate(plants):

        st.subheader(p["name"])

        if p.get("subtype"):
            st.write("Type:", p["subtype"])

        if p.get("growth"):
            st.write("Growth:", p["growth"])

        if p["name"] in [g["name"] for g in st.session_state.garden]:
            st.success("Added ✓")
        else:
            if st.button("Add", key=str(i)):
                st.session_state.garden.append(p)

# ---------- GARDEN ----------
with tabs[2]:
    if "weather" not in st.session_state:
        st.info("Enter ZIP first")
    else:
        for p in st.session_state.garden:
            st.subheader(p["name"])

            day = plant_timing(p, st.session_state.weather)

            if day == 0:
                st.success("Plant today")
            else:
                st.warning(f"Wait {day} days")

            if p.get("subtype"):
                st.write("🌱 Type:", p["subtype"])

            if p.get("growth"):
                st.write("🌿 Growth:", p["growth"])

            st.divider()
