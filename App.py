import streamlit as st
import requests
import datetime

st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
.block-container { padding-top: 1rem; }

/* Calendar grid */
.calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 6px;
}

.day-box {
    padding: 10px;
    border-radius: 10px;
    text-align: center;
    font-size: 12px;
    color: white;
}

.green { background-color: #4CAF50; }
.yellow { background-color: #f4b400; }
.red { background-color: #d93025; }

.header-day {
    text-align: center;
    font-weight: bold;
    font-size: 12px;
    color: #2f5d3a;
}

h1, h2, h3 { color: #2f5d3a; }
</style>
""", unsafe_allow_html=True)

# ---------- PLANTS ----------
plants = [
{"name":"Cherry Tomato","type":"fruit","harvest":65,"depth":"1/4 inch",
"companions":["Basil","Marigold"],"avoid":["Corn"],
"water":"Deep watering","sun":"Full sun","temp":"65-85F",
"care":"Prune suckers",
"yield_lbs":10,"meals":8,
"recipes":["Tomato salad","Pasta sauce","Tomato soup"]},

{"name":"Carrot","type":"root","harvest":70,"depth":"1/4 inch",
"companions":["Lettuce"],"avoid":["Dill"],
"water":"Keep moist","sun":"Full sun","temp":"55-75F",
"care":"Thin seedlings",
"yield_lbs":1,"meals":3,
"recipes":["Roasted carrots","Carrot soup","Honey carrots"]},

{"name":"Marigold","type":"flower","harvest":50,"depth":"1/4 inch",
"companions":["Tomato"],"avoid":[],
"water":"Light watering","sun":"Full sun","temp":"60-80F",
"care":"Deadhead flowers",
"yield_lbs":0,"meals":0,
"recipes":[]}
]

# ---------- WEATHER ----------
def geocode(zipcode):
    r = requests.get("https://geocoding-api.open-meteo.com/v1/search?name=" + zipcode).json()
    if "results" in r:
        return r["results"][0]["latitude"], r["results"][0]["longitude"]
    return None, None

def get_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=" + str(lat) +
        "&longitude=" + str(lon) +
        "&daily=temperature_2m_min,precipitation_probability_max"
        "&temperature_unit=fahrenheit"
        "&timezone=auto"
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
def planting_color(temp, rain):
    if temp < 36:
        return "red", "Cold"
    if rain > 70:
        return "red", "Rain"
    if temp < 50 or rain > 40:
        return "yellow", "Caution"
    return "green", "Good"

def best_day(weather):
    scores = [d["temp"] - d["rain"] for d in weather[:30]]
    return scores.index(max(scores))

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("🌱 ZipPlant Calendar")

tabs = st.tabs(["📍 Location","🌿 Build","🌼 Garden","📅 Calendar","🧠 Tips"])

# ---------- LOCATION ----------
with tabs[0]:
    zipcode = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zipcode)
        if lat:
            st.session_state.weather = get_weather(lat, lon)

# ---------- BUILD ----------
with tabs[1]:
    for i, p in enumerate(plants):
        col1, col2 = st.columns([2,1])

        col1.write(p["name"])
        col1.write("Depth:", p["depth"])

        if col2.button("Add", key=str(i)):
            if p not in st.session_state.garden:
                st.session_state.garden.append(p)

# ---------- GARDEN ----------
with tabs[2]:
    if st.session_state.garden:
        total_lbs = sum(p["yield_lbs"] for p in st.session_state.garden)
        total_meals = sum(p["meals"] for p in st.session_state.garden)

        st.write("🌿 Estimated Yield:", total_lbs, "lbs")
        st.write("🍽 Meals:", total_meals)

        for p in st.session_state.garden:
            st.subheader(p["name"])

            st.write("🌾 Depth:", p["depth"])
            st.write("🌿 Companion Plants:", ", ".join(p["companions"]) if p["companions"] else "None")
            st.write("🚫 Plants to Avoid:", ", ".join(p["avoid"]) if p["avoid"] else "None")

            st.write("💧 Water:", p["water"])
            st.write("☀️ Sun:", p["sun"])
            st.write("🌡 Temp:", p["temp"])
            st.write("✂️ Care:", p["care"])

            if p["recipes"]:
                st.write("🍽 Recipes:")
                for r in p["recipes"]:
                    st.write("-", r)

            st.divider()

# ---------- CALENDAR ----------
with tabs[3]:

    st.header("📅 Monthly Garden Calendar")

    if "weather" in st.session_state:

        weather = st.session_state.weather
        best = best_day(weather)

        # Day headers
        days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
        cols = st.columns(7)
        for i, d in enumerate(days):
            cols[i].markdown(f"<div class='header-day'>{d}</div>", unsafe_allow_html=True)

        # Calendar grid
        cols = st.columns(7)

        for i, d in enumerate(weather[:28]):
            date = datetime.datetime.strptime(d["date"], "%Y-%m-%d")
            color, label = planting_color(d["temp"], d["rain"])
            star = "⭐" if i == best else ""

            cols[i % 7].markdown(
                f"<div class='day-box {color}'>"
                f"{date.day}<br>{star}<br>{d['temp']}F"
                f"</div>",
                unsafe_allow_html=True
            )

        st.divider()

        # Summary
        good_days = sum(1 for d in weather if planting_color(d["temp"], d["rain"])[0] == "green")
        st.success(f"🌿 {good_days} good planting days this month")

        # Garden advice
        if st.session_state.garden:
            st.subheader("🌿 Your Garden This Month")

            for p in st.session_state.garden:
                st.write(f"{p['name']} → Plant in {best} days")

    else:
        st.info("Enter location first")

# ---------- TIPS ----------
with tabs[4]:
    if "weather" in st.session_state:
        best = best_day(st.session_state.weather)
        st.success(f"Best planting day in {best} days")
    else:
        st.info("Enter location")
