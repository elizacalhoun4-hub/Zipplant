import streamlit as st
import requests
import datetime
from plants_data import plants

st.set_page_config(page_title="ZipPlant 🌱", layout="centered")

# ---------- CLEAN DATA ----------
def clean_names(plants):
    for p in plants:
        # Remove trailing numbers like "Tomato 1"
        p["name"] = p["name"].split(" ")[0]
    return plants

plants = clean_names(plants)

# ---------- TYPE OPTIONS ----------
TYPE_OPTIONS = {
    "tomato": ["Slicing", "Paste", "Cherry"],
    "pepper": ["Bell", "Hot", "Sweet", "Wax"],
    "lettuce": ["Romaine", "Leaf", "Butterhead"],
    "basil": ["Genovese", "Thai", "Lemon"]
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
        return "red","Too cold"
    if rain > 70:
        return "red","Heavy rain"
    if temp < 50 or rain > 40:
        return "yellow","Caution"
    return "green","Good"

def best_day(weather):
    scores = [d["temp"] - d["rain"] for d in weather[:7]]
    return scores.index(max(scores))

# ---------- GARDEN INFO ----------
def garden_info(name):
    n = name.lower()

    if "tomato" in n:
        return {
            "planting":"2–4 per person",
            "family2":"4–6",
            "family4":"8–12",
            "storage":"Can, freeze, dry",
            "care":"Stake, prune, deep water",
            "use":"Fresh, sauces"
        }

    if "pepper" in n:
        return {
            "planting":"1–2 per person",
            "family2":"2–4",
            "family4":"6–8",
            "storage":"Freeze, pickle",
            "care":"Warm soil",
            "use":"Cooking, spice"
        }

    return {
        "planting":"Varies",
        "family2":"Varies",
        "family4":"Varies",
        "storage":"Mixed",
        "care":"General",
        "use":"General"
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

    if "weather" in st.session_state:
        best = best_day(st.session_state.weather)

        for i,d in enumerate(st.session_state.weather[:7]):
            color, reason = planting_score(d["temp"], d["rain"])
            star = "⭐ BEST" if i == best else ""

            st.markdown(
                f"{d['date']} {star} — {d['temp']}F / Rain {d['rain']}% ({reason})"
            )

# ---------- BUILD ----------
with tabs[1]:
    seen = set()

    for i,p in enumerate(plants):
        name = p["name"]

        if name in seen:
            continue
        seen.add(name)

        st.subheader(name)

        # Type selector
        plant_type = None
        for key in TYPE_OPTIONS:
            if key in name.lower():
                plant_type = st.selectbox("Type", TYPE_OPTIONS[key], key=f"{name}_{i}")

        entry = f"{name} - {plant_type}" if plant_type else name

        if entry in [g["name"] for g in st.session_state.garden]:
            st.success("Added")
        else:
            if st.button("Add", key=i):
                st.session_state.garden.append({
                    "name": entry,
                    "base": name,
                    "type": plant_type,
                    "cultivars": p.get("cultivars", [])
                })

# ---------- GARDEN ----------
with tabs[2]:
    if "weather" not in st.session_state:
        st.info("Enter ZIP first")
    else:
        for p in st.session_state.garden:
            st.subheader(p["name"])

            info = garden_info(p["name"])

            st.write("Per Person:", info["planting"])
            st.write("Family 2:", info["family2"])
            st.write("Family 4:", info["family4"])
            st.write("Storage:", info["storage"])
            st.write("Care:", info["care"])
            st.write("Use:", info["use"])

            # Cultivars restored
            if p.get("cultivars"):
                with st.expander("Cultivars"):
                    for c in p["cultivars"][:5]:
                        st.write(f"{c['name']} - {c['description']}")

            st.divider()
