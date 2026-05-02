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
    "parsley": ["Flat Leaf", "Curly"],
    "carrot": []
}

# ---------- PLANT INTELLIGENCE ----------
def plant_profile(name):
    n = name.lower()

    if "tomato" in n:
        return {
            "category": "Fruit",
            "group": "Vegetable",
            "planting": "2–4 per person",
            "family2": "4–6 plants",
            "family4": "8–12 plants",
            "method": "Start indoors, transplant",
            "harvest": "60–85 days",
            "storage": "Can, freeze, dry",
            "care": "Stake, prune suckers, deep watering"
        }

    if "carrot" in n:
        return {
            "category": "Root",
            "group": "Vegetable",
            "planting": "20–30 per person",
            "family2": "40–60",
            "family4": "80–120",
            "method": "Direct sow seeds",
            "harvest": "60–75 days",
            "storage": "Root cellar, fridge",
            "care": "Loose soil, thin early"
        }

    if "lettuce" in n:
        return {
            "category": "Leafy",
            "group": "Vegetable",
            "planting": "6–10 per person",
            "family2": "10–15",
            "family4": "20–30",
            "method": "Direct sow or transplant",
            "harvest": "30–50 days",
            "storage": "Refrigerate short-term",
            "care": "Cool weather, frequent harvest"
        }

    if "basil" in n:
        return {
            "category": "Leafy",
            "group": "Herb",
            "planting": "1–2 per person",
            "family2": "2–3",
            "family4": "4–6",
            "method": "Start indoors or direct sow",
            "harvest": "30–60 days",
            "storage": "Dry or freeze pesto",
            "care": "Pinch often, avoid flowering"
        }

    if "parsley" in n:
        return {
            "category": "Leafy",
            "group": "Herb",
            "planting": "2–4 per person",
            "family2": "4–6",
            "family4": "8–12",
            "method": "Direct sow or transplant",
            "harvest": "70–90 days",
            "storage": "Refrigerate, dry",
            "care": "Slow germination, keep moist"
        }

    if "pepper" in n:
        return {
            "category": "Fruit",
            "group": "Vegetable",
            "planting": "1–2 per person",
            "family2": "2–4",
            "family4": "6–8",
            "method": "Start indoors, transplant",
            "harvest": "60–90 days",
            "storage": "Freeze, pickle",
            "care": "Warm soil, consistent watering"
        }

    return {
        "category": "General",
        "group": "Vegetable",
        "planting": "Varies",
        "family2": "Varies",
        "family4": "Varies",
        "method": "Seeds or starts",
        "harvest": "Varies",
        "storage": "Mixed",
        "care": "General care"
    }

# ---------- WEATHER ----------
def get_weather(zipcode):
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zipcode}").json()
    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit"
    r = requests.get(url).json()

    data = []
    for i in range(len(r["daily"]["time"])):
        data.append({
            "date": r["daily"]["time"][i],
            "temp": round(r["daily"]["temperature_2m_min"][i]),
            "rain": r["daily"]["precipitation_probability_max"][i]
        })
    return data

def planting_score(temp, rain):
    if temp < 36:
        return "Too cold"
    if rain > 70:
        return "Heavy rain"
    if temp < 50 or rain > 40:
        return "Caution"
    return "Good"

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

    if "weather" in st.session_state:
        for d in st.session_state.weather[:7]:
            st.write(f"{d['date']} — {d['temp']}F / Rain {d['rain']}% ({planting_score(d['temp'], d['rain'])})")

# ---------- BUILD ----------
with tabs[1]:
    groups = ["All", "Vegetable", "Herb"]
    selected_group = st.selectbox("Filter by Group", groups)

    categories = ["All", "Root", "Leafy", "Fruit"]
    selected_cat = st.selectbox("Filter by Type", categories)

    for i,p in enumerate(plants):
        profile = plant_profile(p["name"])

        if selected_group != "All" and profile["group"] != selected_group:
            continue
        if selected_cat != "All" and profile["category"] != selected_cat:
            continue

        st.subheader(p["name"])

        key = p["name"].lower()
        plant_type = None

        for k in TYPE_OPTIONS:
            if k in key and TYPE_OPTIONS[k]:
                plant_type = st.selectbox("Choose type", TYPE_OPTIONS[k], key=f"type_{i}")

        entry = f"{p['name']} - {plant_type}" if plant_type else p["name"]

        if entry in [g["name"] for g in st.session_state.garden]:
            st.success("Added")
        else:
            if st.button("Add", key=i):
                st.session_state.garden.append({
                    "name": entry,
                    "base": p["name"],
                    "type": plant_type,
                    "cultivars": p.get("cultivars", [])
                })

# ---------- GARDEN ----------
with tabs[2]:
    if "weather" not in st.session_state:
        st.info("Enter ZIP first")
    else:
        for p in st.session_state.garden:
            profile = plant_profile(p["name"])

            st.subheader(p["name"])

            st.write("Category:", profile["category"])
            st.write("Group:", profile["group"])

            st.write("Per Person:", profile["planting"])
            st.write("Family of 2:", profile["family2"])
            st.write("Family of 4:", profile["family4"])

            st.write("Planting Method:", profile["method"])
            st.write("Harvest Time:", profile["harvest"])

            st.write("Storage:", profile["storage"])
            st.write("Care:", profile["care"])

            if p.get("cultivars"):
                with st.expander("Cultivars"):
                    for c in p["cultivars"]:
                        st.write(f"{c['name']} - {c['description']}")

            st.divider()
