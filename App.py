import streamlit as st
import requests
import datetime
from plants_data import plants

st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
.block-container { padding-top: 1rem; }
.day-card {
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 10px;
    color: white;
    font-weight: 500;
}
.green { background-color: #4CAF50; }
.yellow { background-color: #f4b400; }
.red { background-color: #d93025; }
h1, h2, h3 { color: #2f5d3a; }
</style>
""", unsafe_allow_html=True)

# ---------- IMAGE ----------
@st.cache_data(show_spinner=False)
def get_plant_image(name):
    try:
        search = name.replace(" ", "_")
        r = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + search,
            timeout=5
        ).json()
        if "thumbnail" in r:
            return r["thumbnail"]["source"]
    except:
        pass
    return None

# ---------- WEATHER ----------
def geocode(zipcode):
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search?name=" + zipcode
    ).json()
    if "results" in r:
        return r["results"][0]["latitude"], r["results"][0]["longitude"]
    return None, None

def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_min,precipitation_probability_max"
        "&temperature_unit=fahrenheit&timezone=auto"
    )
    r = requests.get(url).json()

    data = []
    for i in range(len(r["daily"]["time"])):
        data.append({
            "date": r["daily"]["time"][i],
            "temp": round(r["daily"]["temperature_2m_min"][i]),
            "rain": r["daily"]["precipitation_probability_max"][i]
        })
    return data

# ---------- LOGIC ----------
def planting_score(temp, rain):
    if temp < 36:
        return "red", "Too cold"
    if rain > 70:
        return "red", "Heavy rain"
    if temp < 50 or rain > 40:
        return "yellow", "Caution"
    return "green", "Good day"

def best_day(weather):
    scores = [d["temp"] - d["rain"] for d in weather[:7]]
    return scores.index(max(scores))

def wait_msg(i):
    if i == 0:
        return "Plant today"
    if i == 1:
        return "Wait 1 day"
    return f"Wait {i} days"

# ---------- GARDEN INTELLIGENCE ----------
def plant_details(name):
    n = name.lower()

    if "tomato" in n:
        return {
            "type": "Paste / Slicing / Cherry / Heirloom",
            "planting": "2–4 per person",
            "family2": "4–6 plants",
            "family4": "8–12 plants",
            "storage": "Can, freeze, dehydrate, sun-dry",
            "use": "Fresh eating, sauces, roasting",
        }

    if "pepper" in n:
        return {
            "type": "Bell / Hot / Sweet / Wax",
            "planting": "1–2 per person",
            "family2": "2–4 plants",
            "family4": "6–8 plants",
            "storage": "Freeze, dry, pickle",
            "use": "Fresh, cooking, sauces, spice",
        }

    if "lettuce" in n:
        return {
            "type": "Leaf / Romaine / Butterhead",
            "planting": "6–10 per person",
            "family2": "10–15 plants",
            "family4": "20–30 plants",
            "storage": "Refrigerate short-term",
            "use": "Salads, wraps",
        }

    return {
        "type": "General",
        "planting": "Varies",
        "family2": "Varies",
        "family4": "Varies",
        "storage": "Refrigerate, freeze, or dry",
        "use": "General kitchen use",
    }

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("ZipPlant Calendar 🌱")
tabs = st.tabs(["Location","Build","Garden"])

# ---------- LOCATION ----------
with tabs[0]:
    zipcode = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zipcode)
        if lat:
            st.session_state.weather = get_weather(lat, lon)

    if "weather" in st.session_state:
        best = best_day(st.session_state.weather)

        for i,d in enumerate(st.session_state.weather[:7]):
            date = datetime.datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a %b %d")
            color, reason = planting_score(d["temp"], d["rain"])
            star = " ⭐ BEST" if i == best else ""

            st.markdown(
                f"<div class='day-card {color}'>{date}{star}<br>{d['temp']}F | Rain {d['rain']}%<br>{reason}</div>",
                unsafe_allow_html=True
            )

# ---------- BUILD ----------
with tabs[1]:
    categories = sorted(set(p["category"] for p in plants))
    selected = st.selectbox("Filter", ["All"] + categories)

    for i,p in enumerate(plants):
        if selected!="All" and p["category"]!=selected:
            continue

        col1,col2 = st.columns([2,1])

        with col1:
            st.subheader(p["name"])
            st.caption(p["category"])

            details = plant_details(p["name"])
            st.write("Type:", details["type"])
            st.write("Care:", p["care"])

            if p.get("cultivars"):
                with st.expander("Cultivars"):
                    for c in p["cultivars"]:
                        st.write(f"{c['name']}: {c['description']}")

        with col2:
            if p["name"] in [g["name"] for g in st.session_state.garden]:
                st.success("Added ✓")
            else:
                if st.button("Add", key=str(i)):
                    st.session_state.garden.append(p)
                    st.toast(p["name"] + " added")

# ---------- GARDEN ----------
with tabs[2]:
    if st.session_state.garden:
        for p in st.session_state.garden:
            st.subheader(p["name"])

            details = plant_details(p["name"])

            st.write("🌱 Type:", details["type"])
            st.write("👤 Per Person:", details["planting"])
            st.write("👨‍👩‍👧 Family 2:", details["family2"])
            st.write("👨‍👩‍👧‍👦 Family 4:", details["family4"])
            st.write("🥫 Storage:", details["storage"])
            st.write("🍳 Use:", details["use"])

            if p.get("cultivars"):
                st.write("🌿 Cultivars:")
                for c in p["cultivars"]:
                    st.write(f"- {c['name']}: {c['description']}")

            st.divider()
    else:
        st.info("Add plants from the Build tab 🌿")
