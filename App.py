import streamlit as st
import requests
from plants_data import plants as base_plants

st.set_page_config(page_title="ZipPlant 🌱", layout="centered")

# ---------- TYPE EXPANSION ----------
TYPE_MAP = {
    "tomato": [("Slicing","Indeterminate"),("Paste","Determinate"),("Cherry","Indeterminate")],
    "pepper": [("Bell",None),("Hot",None),("Sweet",None),("Wax",None)],
    "lettuce": [("Romaine",None),("Leaf",None),("Butterhead",None)],
    "basil": [("Genovese",None),("Thai",None),("Lemon",None)],
    "parsley": [("Flat Leaf",None),("Curly",None)]
}

def expand(plants):
    out = []
    for p in plants:
        name = p["name"].lower()
        matched = False

        for key in TYPE_MAP:
            if key in name:
                matched = True
                for subtype, growth in TYPE_MAP[key]:
                    new = p.copy()
                    new["name"] = f"{p['name']} — {subtype}"
                    new["subtype"] = subtype
                    if growth:
                        new["growth"] = growth
                    out.append(new)
                break

        if not matched:
            out.append(p)

    return out

plants = expand(base_plants)

# ---------- GARDEN INTELLIGENCE ----------
def garden_info(name):
    n = name.lower()

    if "tomato" in n:
        return {
            "planting": "2–4 plants per person",
            "family2": "4–6 plants",
            "family4": "8–12 plants",
            "storage": "Can (sauce), freeze, sun-dry, dehydrate",
            "care": "Stake or cage, prune suckers, deep water",
            "use": "Fresh eating, sauces, paste"
        }

    if "pepper" in n:
        return {
            "planting": "1–2 plants per person",
            "family2": "2–4 plants",
            "family4": "6–8 plants",
            "storage": "Freeze, pickle, dry",
            "care": "Warm soil, consistent watering",
            "use": "Cooking, fresh, spice"
        }

    if "lettuce" in n:
        return {
            "planting": "6–10 plants per person",
            "family2": "10–15 plants",
            "family4": "20–30 plants",
            "storage": "Refrigerate short-term",
            "care": "Cool weather, frequent harvest",
            "use": "Salads, wraps"
        }

    if "basil" in n:
        return {
            "planting": "1–2 plants per person",
            "family2": "2–3 plants",
            "family4": "4–6 plants",
            "storage": "Dry or freeze pesto",
            "care": "Pinch regularly, avoid flowering",
            "use": "Pesto, seasoning"
        }

    return {
        "planting": "Varies",
        "family2": "Varies",
        "family4": "Varies",
        "storage": "Refrigerate, freeze, or dry",
        "care": "General garden care",
        "use": "General use"
    }

# ---------- WEATHER ----------
def get_weather(zipcode):
    r = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zipcode}").json()
    lat, lon = r["results"][0]["latitude"], r["results"][0]["longitude"]

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min&temperature_unit=fahrenheit"
    r = requests.get(url).json()

    return r["daily"]["temperature_2m_min"]

def planting_day(p, temps):
    for i, t in enumerate(temps[:7]):
        n = p["name"].lower()

        if "lettuce" in n and t > 45:
            return i
        if "tomato" in n and t > 60:
            return i
        if "pepper" in n and t > 65:
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
    zip = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        st.session_state.weather = get_weather(zip)

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
            if st.button("Add", key=i):
                st.session_state.garden.append(p)

# ---------- GARDEN ----------
with tabs[2]:
    if "weather" not in st.session_state:
        st.info("Enter ZIP first")
    else:
        for p in st.session_state.garden:

            st.subheader(p["name"])

            day = planting_day(p, st.session_state.weather)

            if day == 0:
                st.success("Plant today")
            else:
                st.warning(f"Wait {day} days")

            info = garden_info(p["name"])

            st.write("👤 Per Person:", info["planting"])
            st.write("👨‍👩‍👧 Family 2:", info["family2"])
            st.write("👨‍👩‍👧‍👦 Family 4:", info["family4"])

            st.write("🥫 Storage:", info["storage"])
            st.write("🌿 Care:", info["care"])
            st.write("🍳 Use:", info["use"])

            st.divider()
