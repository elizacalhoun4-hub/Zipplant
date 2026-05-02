import streamlit as st
import requests
from plants_data import plants

st.set_page_config(page_title="ZipPlant", layout="centered")

# ---------- PLANT INTELLIGENCE ----------
def plant_profile(name):
    n = name.lower()

    if "tomato" in n:
        return {
            "category": "Fruit",
            "group": "Vegetable",
            "method": "Start seeds indoors 6–8 weeks before last frost. Transplant after frost.",
            "planting_steps": [
                "Dig deep hole (bury stem)",
                "Space 18–24 inches apart",
                "Add compost to hole",
                "Water thoroughly after planting"
            ],
            "care": [
                "Water deeply 2–3x per week",
                "Stake or cage early",
                "Prune suckers for airflow"
            ],
            "harvest": "Pick when fully colored and slightly soft",
            "yield": "10–20 lbs per plant (varies by type)",
            "storage": "Can, freeze, or use fresh"
        }

    if "lettuce" in n:
        return {
            "category": "Leafy",
            "group": "Vegetable",
            "method": "Direct sow seeds in cool weather",
            "planting_steps": [
                "Scatter seeds lightly",
                "Cover with thin soil layer",
                "Keep soil moist"
            ],
            "care": [
                "Water frequently (light watering)",
                "Provide partial shade in heat"
            ],
            "harvest": "Cut outer leaves early or harvest whole head",
            "yield": "1 head per plant",
            "storage": "Refrigerate short-term"
        }

    return {
        "category": "General",
        "group": "Vegetable",
        "method": "Seeds or starts",
        "planting_steps": ["Standard planting"],
        "care": ["General care"],
        "harvest": "Varies",
        "yield": "Varies",
        "storage": "Mixed"
    }

# ---------- WEATHER ----------
def get_weather(zipcode):
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zipcode}").json()
    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min&temperature_unit=fahrenheit"
    r = requests.get(url).json()
    return r["daily"]["temperature_2m_min"]

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("ZipPlant")
tabs = st.tabs(["Location","Build","Garden"])

# ---------- LOCATION ----------
with tabs[0]:
    zip = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        st.session_state.weather = get_weather(zip)

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
        profile = plant_profile(p["name"])

        st.subheader(p["name"])

        st.write("🌱 HOW TO PLANT:")
        st.write(profile["method"])

        for step in profile["planting_steps"]:
            st.write("•", step)

        st.write("🌿 CARE:")
        for c in profile["care"]:
            st.write("•", c)

        st.write("🌾 HARVEST:")
        st.write(profile["harvest"])

        st.write("📦 YIELD:")
        st.write(profile["yield"])

        st.write("🥫 STORAGE:")
        st.write(profile["storage"])

        st.divider()
