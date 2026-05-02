import streamlit as st
import requests
import datetime

st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
.block-container { padding-top: 1rem; }

.day-card {
    padding: 10px;
    border-radius: 10px;
    margin: 4px;
    text-align: center;
    color: white;
    font-size: 12px;
}

.green { background-color: #4CAF50; }
.yellow { background-color: #f4b400; }
.red { background-color: #d93025; }

h1, h2, h3 { color: #2f5d3a; }
</style>
""", unsafe_allow_html=True)

# ---------- DATA ----------
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

# ---------- WEATHER ----------
def geocode(zipcode):
    r = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zipcode}").json()
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

# ---------- LOGIC ----------
def planting_color(temp, rain):
    if temp < 36:
        return "red"
    if rain > 70:
        return "red"
    if temp < 50 or rain > 40:
        return "yellow"
    return "green"

def best_day(weather):
    scores = [d["temp"] - d["rain"] for d in weather[:30]]
    return scores.index(max(scores))

def estimate_dates(weather, harvest_days):
    today = datetime.date.today()
    for i, d in enumerate(weather):
        if d["temp"] > 40:
            plant = today + datetime.timedelta(days=i)
            harvest = plant + datetime.timedelta(days=harvest_days)
            return plant, harvest
    return today, today + datetime.timedelta(days=harvest_days)

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("🌱 ZipPlant Calendar")

tabs = st.tabs(["📍 Location","🌿 Build","🌼 Garden","📅 Calendar"])

# ---------- LOCATION ----------
with tabs[0]:
    zip_code = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zip_code)
        if lat:
            st.session_state.weather = get_weather(lat, lon)

# ---------- BUILD ----------
with tabs[1]:
    for i, p in enumerate(plants):
        col1, col2 = st.columns([3,1])

        col1.write(p["name"])
        col1.write(f"Depth: {p.get('depth','')}")

        if col2.button("Add", key=f"add{i}"):
            if p not in st.session_state.garden:
                st.session_state.garden.append(p)

# ---------- GARDEN ----------
with tabs[2]:
    if st.session_state.garden:

        total_lbs = sum(p.get("yield_lbs",0) for p in st.session_state.garden)
        total_meals = sum(p.get("meals",0) for p in st.session_state.garden)

        st.subheader("🌿 Garden Output")
        st.write(f"Estimated Yield: {total_lbs} lbs")
        st.write(f"Meals Supported: {total_meals}")

        for p in st.session_state.garden:

            st.subheader(p["name"])

            if "weather" in st.session_state:
                plant, harvest = estimate_dates(st.session_state.weather, p["harvest"])
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

# ---------- CALENDAR ----------
with tabs[3]:
    if "weather" in st.session_state:

        weather = st.session_state.weather
        best = best_day(weather)

        st.subheader("📅 Monthly View")

        for row in range(4):
            cols = st.columns(7)
            for col in range(7):
                i = row*7 + col
                if i >= len(weather):
                    continue

                d = weather[i]
                date = datetime.datetime.strptime(d["date"], "%Y-%m-%d")
                color = planting_color(d["temp"], d["rain"])
                star = "⭐" if i == best else ""

                cols[col].markdown(
                    f"<div class='day-card {color}'>"
                    f"{date.day}<br>{star}<br>{d['temp']}F"
                    f"</div>",
                    unsafe_allow_html=True
                )

    else:
        st.info("Enter location first")
