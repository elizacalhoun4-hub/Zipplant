# =========================================
# ZIPPLANT CALENDAR — STABLE BASE VERSION
# =========================================

import streamlit as st
import requests
import datetime

st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# =========================================
# STYLE
# =========================================
st.markdown("""
<style>
.block-container { padding-top: 1rem; }

.day-card {
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
    color: white;
    font-weight: 500;
}

.green { background-color: #4CAF50; }
.yellow { background-color: #f4b400; }
.red { background-color: #d93025; }

h1, h2, h3 { color: #2f5d3a; }
</style>
""", unsafe_allow_html=True)

# =========================================
# PLANT DATA (SAFE BASE)
# =========================================
plants = [
{
"name":"Cherry Tomato",
"type":"fruit",
"harvest":65,
"depth":"1/4 inch",
"companions":["Basil","Marigold"],
"avoid":["Corn"],
"water":"Deep watering 2-3x/week",
"sun":"Full sun",
"temp":"65-85F",
"care":"Prune and cage",
"yield_lbs":10,
"meals":8,
"recipes":["Tomato salad","Pasta sauce","Tomato soup"]
},
{
"name":"Carrot",
"type":"root",
"harvest":70,
"depth":"1/4 inch",
"companions":["Lettuce"],
"avoid":["Dill"],
"water":"Keep soil moist",
"sun":"Full sun",
"temp":"55-75F",
"care":"Thin seedlings",
"yield_lbs":1,
"meals":3,
"recipes":["Roasted carrots","Carrot soup","Glazed carrots"]
}
]

# =========================================
# WEATHER FUNCTIONS
# =========================================
def geocode(zipcode):
    r = requests.get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={zipcode}"
    ).json()

    if "results" in r:
        return r["results"][0]["latitude"], r["results"][0]["longitude"]

    return None, None


def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_min,precipitation_probability_max"
        f"&temperature_unit=fahrenheit"
        f"&timezone=auto"
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


# =========================================
# LOGIC FUNCTIONS
# =========================================
def planting_color(temp, rain):
    if temp < 36:
        return "red", "Too Cold"
    if rain > 70:
        return "red", "Heavy Rain"
    if temp < 50 or rain > 40:
        return "yellow", "Caution"
    return "green", "Good"


def best_day(weather):
    scores = [d["temp"] - d["rain"] for d in weather[:7]]
    return scores.index(max(scores))


def estimate_dates(weather, harvest_days):
    today = datetime.date.today()

    for i, d in enumerate(weather):
        if d["temp"] > 40:
            plant = today + datetime.timedelta(days=i)
            harvest = plant + datetime.timedelta(days=harvest_days)
            return plant, harvest

    return today, today + datetime.timedelta(days=harvest_days)


# =========================================
# SESSION STATE
# =========================================
if "garden" not in st.session_state:
    st.session_state.garden = []

# =========================================
# UI TABS
# =========================================
tabs = st.tabs(["📍 Location","🌿 Build","🌼 Garden","🧠 Tips"])

# =========================================
# LOCATION TAB
# =========================================
with tabs[0]:

    zip_code = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zip_code)

        if lat:
            st.session_state.weather = get_weather(lat, lon)

    # ---------- WEATHER DISPLAY ----------
    if "weather" in st.session_state:

        best = best_day(st.session_state.weather)

        for i, d in enumerate(st.session_state.weather[:7]):

            date = datetime.datetime.strptime(
                d["date"], "%Y-%m-%d"
            ).strftime("%a %b %d")

            color, reason = planting_color(d["temp"], d["rain"])
            star = " ⭐ BEST" if i == best else ""

            st.markdown(
                f"<div class='day-card {color}'>"
                f"{date}{star}<br>"
                f"{d['temp']}F | Rain {d['rain']}%<br>"
                f"{reason}"
                f"</div>",
                unsafe_allow_html=True
            )

# =========================================
# BUILD TAB
# =========================================
with tabs[1]:

    for i, p in enumerate(plants):

        col1, col2 = st.columns([3,1])

        col1.write(p["name"])
        col1.write(f"Depth: {p.get('depth','')}")

        if col2.button("Add", key=f"add_{i}"):
            if p not in st.session_state.garden:
                st.session_state.garden.append(p)

# =========================================
# GARDEN TAB
# =========================================
with tabs[2]:

    if st.session_state.garden:

        total_lbs = sum(p.get("yield_lbs", 0) for p in st.session_state.garden)
        total_meals = sum(p.get("meals", 0) for p in st.session_state.garden)

        st.subheader("🌿 Garden Output")
        st.write(f"Estimated Yield: {total_lbs} lbs")
        st.write(f"Meals Supported: {total_meals}")

        for p in st.session_state.garden:

            st.subheader(p["name"])

            if "weather" in st.session_state:
                plant, harvest = estimate_dates(
                    st.session_state.weather,
                    p["harvest"]
                )

                st.write(f"🌿 Plant On: {plant}")
                st.write(f"🍅 Harvest Around: {harvest}")

            st.write(f"🌾 Depth: {p.get('depth','')}")
            st.write(f"🌿 Companion Plants: {', '.join(p.get('companions',[])) or 'None'}")
            st.write(f"🚫 Plants to Avoid: {', '.join(p.get('avoid',[])) or 'None'}")

            st.markdown("### 🌿 Care Guide")
            st.write(f"💧 Water: {p.get('water','')}")
            st.write(f"☀️ Sun: {p.get('sun','')}")
            st.write(f"🌡 Temp: {p.get('temp','')}")
            st.write(f"✂️ Care: {p.get('care','')}")

            st.markdown("### 🌱 Food Output")
            st.write(f"Yield: {p.get('yield_lbs',0)} lbs")
            st.write(f"Meals: {p.get('meals',0)}")

            if p.get("recipes"):
                st.markdown("### 🍽 Recipes")
                for r in p["recipes"]:
                    st.write(f"- {r}")

            st.divider()

    else:
        st.info("Add plants first 🌱")

# =========================================
# TIPS TAB
# =========================================
with tabs[3]:

    if "weather" in st.session_state:
        best = best_day(st.session_state.weather)
        st.success(f"Best planting day in {best} days")
    else:
        st.info("Enter location first")
