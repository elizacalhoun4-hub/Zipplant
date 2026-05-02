import streamlit as st
import requests
import datetime

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

.plant-card {
    background: white;
    padding: 12px;
    border-radius: 16px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

h1, h2, h3 { color: #2f5d3a; }
</style>
""", unsafe_allow_html=True)

# ---------- PLANTS ----------
plants = [
{"name":"Bell Pepper","type":"fruit","harvest":75,"tip":"Needs warm nights"},
{"name":"Jalapeño","type":"fruit","harvest":70,"tip":"Loves heat"},
{"name":"Cherry Tomato","type":"fruit","harvest":65,"tip":"Fast grower"},
{"name":"Roma Tomato","type":"fruit","harvest":75,"tip":"Great for cooking"},
{"name":"Cucumber","type":"fruit","harvest":55,"tip":"Needs steady water"},
{"name":"Zucchini","type":"fruit","harvest":50,"tip":"Very productive"},

{"name":"Lettuce","type":"leafy","harvest":30,"tip":"Cool weather crop"},
{"name":"Spinach","type":"leafy","harvest":35,"tip":"Spring favorite"},
{"name":"Kale","type":"leafy","harvest":55,"tip":"Cold hardy"},

{"name":"Carrot","type":"root","harvest":70,"tip":"Direct sow"},
{"name":"Radish","type":"root","harvest":30,"tip":"Very fast"},
{"name":"Beet","type":"root","harvest":60,"tip":"Dual purpose"},

{"name":"Zinnia","type":"flower","harvest":60,"tip":"Heat loving"},
{"name":"Marigold","type":"flower","harvest":50,"tip":"Pest control"},
{"name":"Sunflower","type":"flower","harvest":80,"tip":"Direct sow"},
{"name":"Cosmos","type":"flower","harvest":65,"tip":"Low care"},
]

# ---------- FUNCTIONS ----------
def geocode(zip):
    r = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip}").json()
    if "results" in r:
        return r["results"][0]["latitude"], r["results"][0]["longitude"]
    return None, None

def get_weather(lat, lon):
    r = requests.get(
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_min,precipitation_probability_max"
        f"&temperature_unit=fahrenheit"
        f"&timezone=auto"
    ).json()

    days = r["daily"]["time"]
    temps = r["daily"]["temperature_2m_min"]
    rain = r["daily"]["precipitation_probability_max"]

    data = []
    for i in range(len(days)):
        data.append({
            "date": days[i],
            "temp": round(temps[i]),
            "rain": rain[i]
        })
    return data

@st.cache_data(show_spinner=False)
def get_plant_image(name):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}"
        r = requests.get(url, timeout=5).json()
        if "thumbnail" in r:
            return r["thumbnail"]["source"]
    except:
        pass
    return None

def planting_score(temp, rain):
    if temp < 36: return "red", "Too cold"
    if rain > 70: return "red", "Heavy rain"
    if temp < 50 or rain > 40: return "yellow", "Caution"
    return "green", "Good day"

def score_day(temp, rain):
    score = 0
    if temp >= 60: score += 3
    elif temp >= 50: score += 2
    elif temp >= 40: score += 1
    else: score -= 3

    if rain < 20: score += 2
    elif rain < 50: score += 1
    else: score -= 2

    return score

def find_best_day(weather):
    best_i = 0
    best_score = -999
    for i, d in enumerate(weather[:7]):
        s = score_day(d["temp"], d["rain"])
        if s > best_score:
            best_score = s
            best_i = i
    return best_i

def wait_message(i):
    if i == 0: return "🌿 Plant today"
    if i == 1: return "🌿 Wait 1 day"
    return f"🌿 Wait {i} days"

def estimate_frost(weather):
    today = datetime.date.today()
    for i, d in enumerate(weather):
        if d["temp"] > 36:
            return today + datetime.timedelta(days=i)
    return today

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("🌱 ZipPlant Calendar")

tabs = st.tabs(["📍","🌿","🌼","🧠"])

# ---------- LOCATION ----------
with tabs[0]:
    zip = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zip)
        if lat:
            st.session_state.weather = get_weather(lat, lon)
            st.session_state.frost = estimate_frost(st.session_state.weather)

    if "weather" in st.session_state:
        best = find_best_day(st.session_state.weather)

        for i, d in enumerate(st.session_state.weather[:7]):
            date = datetime.datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a %b %d")
            color, reason = planting_score(d["temp"], d["rain"])
            star = " ⭐ BEST" if i == best else ""

            st.markdown(
                f"<div class='day-card {color}'>"
                f"{date}{star}<br>{d['temp']}°F | 🌧 {d['rain']}%<br>{reason}"
                f"</div>",
                unsafe_allow_html=True
            )

        st.success(wait_message(best))

# ---------- BUILD ----------
with tabs[1]:
    st.caption(f"{len(st.session_state.garden)} plants selected")

    category = st.selectbox("Category", ["Vegetables","Flowers"])

    if category == "Vegetables":
        sub = st.selectbox("Type", ["fruit","leafy","root"])
        filtered = [p for p in plants if p["type"] == sub]
    else:
        filtered = [p for p in plants if p["type"] == "flower"]

    for i, p in enumerate(filtered):
        col1, col2 = st.columns([2,1])

        with col1:
            st.markdown("<div class='plant-card'>", unsafe_allow_html=True)

            img = get_plant_image(p["name"])
            if img:
                st.image(img, use_container_width=True)
            else:
                emoji = "🌸" if p["type"] == "flower" else "🌱"
                st.markdown(f"<div style='font-size:40px'>{emoji}</div>", unsafe_allow_html=True)

            st.markdown(f"**{p['name']}**")
            st.caption(f"Harvest ~{p['harvest']} days")
            st.write(p["tip"])

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            if p in st.session_state.garden:
                st.success("✓ Added")
            else:
                if st.button("Add", key=f"{p['name']}_{i}"):
                    st.session_state.garden.append(p)
                    st.toast(f"{p['name']} added 🌿")

# ---------- GARDEN ----------
with tabs[2]:
    if st.session_state.garden:
        for p in st.session_state.garden:
            st.markdown(f"### {p['name']}")

            img = get_plant_image(p["name"])
            if img:
                st.image(img, width=200)

            if "frost" in st.session_state:
                plant = st.session_state.frost + datetime.timedelta(weeks=2)
                harvest = plant + datetime.timedelta(days=p["harvest"])

                st.write(f"🌿 Plant: {plant}")
                st.write(f"🍅 Harvest: {harvest}")

            st.write(f"💡 {p['tip']}")
            st.divider()
    else:
        st.info("Add plants first 🌱")

# ---------- TIPS ----------
with tabs[3]:
    if "weather" in st.session_state:
        best = find_best_day(st.session_state.weather)
        st.success(wait_message(best))
    else:
        st.info("Enter location")
