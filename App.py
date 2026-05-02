import streamlit as st
import requests
import datetime

st.set_page_config(page_title="ZipPlant", layout="centered")

# =========================
# SAFE STATE INIT
# =========================
if "garden" not in st.session_state:
    st.session_state.garden = []

if "weather" not in st.session_state:
    st.session_state.weather = None

# =========================
# DATA
# =========================
plants = [
    {
        "name": "Cherry Tomato",
        "harvest": 65,
        "depth": "1/4 inch",
        "companions": ["Basil", "Marigold"],
        "avoid": ["Corn"],
        "water": "Deep watering",
        "sun": "Full sun",
        "temp": "65-85F",
        "care": "Prune and cage"
    },
    {
        "name": "Carrot",
        "harvest": 70,
        "depth": "1/4 inch",
        "companions": ["Lettuce"],
        "avoid": ["Dill"],
        "water": "Keep moist",
        "sun": "Full sun",
        "temp": "55-75F",
        "care": "Thin seedlings"
    }
]

# =========================
# WEATHER FUNCTIONS (SAFE)
# =========================
def geocode(zipcode):
    try:
        r = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={zipcode}",
            timeout=5
        ).json()

        if "results" in r:
            return r["results"][0]["latitude"], r["results"][0]["longitude"]
    except:
        pass

    return None, None


def get_weather(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_min,precipitation_probability_max"
            f"&temperature_unit=fahrenheit"
            f"&timezone=auto"
        )

        r = requests.get(url, timeout=5).json()

        if "daily" not in r:
            return None

        data = []
        for i in range(len(r["daily"]["time"])):
            data.append({
                "date": r["daily"]["time"][i],
                "temp": round(r["daily"]["temperature_2m_min"][i]),
                "rain": r["daily"]["precipitation_probability_max"][i]
            })

        return data

    except:
        return None


# =========================
# UI START
# =========================
st.title("🌱 ZipPlant")

tabs = st.tabs(["Location", "Build", "Garden", "Tips"])

# =========================
# LOCATION TAB
# =========================
with tabs[0]:

    zip_code = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zip_code)

        if lat is None:
            st.error("Could not find location")
        else:
            weather = get_weather(lat, lon)

            if weather:
                st.session_state.weather = weather
            else:
                st.error("Weather failed to load")

    # SAFE WEATHER DISPLAY
    if st.session_state.weather:

        st.subheader("Next 7 Days")

        for d in st.session_state.weather[:7]:
            date = datetime.datetime.strptime(d["date"], "%Y-%m-%d")
            st.write(
                f"{date.strftime('%b %d')} — "
                f"{d['temp']}F | Rain {d['rain']}%"
            )

# =========================
# BUILD TAB
# =========================
with tabs[1]:

    for i, p in enumerate(plants):

        col1, col2 = st.columns([3, 1])

        col1.write(p["name"])
        col1.write(f"Depth: {p.get('depth', '')}")

        if col2.button("Add", key=f"add_{i}"):
            if p not in st.session_state.garden:
                st.session_state.garden.append(p)

# =========================
# GARDEN TAB
# =========================
with tabs[2]:

    if not st.session_state.garden:
        st.info("No plants added yet")
    else:
        for p in st.session_state.garden:

            st.subheader(p["name"])

            st.write(f"Depth: {p.get('depth','')}")
            st.write(f"Water: {p.get('water','')}")
            st.write(f"Sun: {p.get('sun','')}")
            st.write(f"Care: {p.get('care','')}")

            st.write(
                "Companion Plants: " +
                (", ".join(p.get("companions", [])) or "None")
            )

            st.write(
                "Avoid: " +
                (", ".join(p.get("avoid", [])) or "None")
            )

            st.divider()

# =========================
# TIPS TAB
# =========================
with tabs[3]:

    if st.session_state.weather:
        st.success("Weather loaded successfully")
    else:
        st.info("Enter location first")
