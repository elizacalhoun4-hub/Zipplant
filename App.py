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

# ---------- PLANTING LOGIC ----------
def planting_score(temp, rain):
    if temp < 36:
        return "red", "Too cold (frost risk)"
    if rain > 70:
        return "red", "Heavy rain"
    if temp < 50 or rain > 40:
        return "yellow", "Caution"
    return "green", "Good planting day"

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
    best_index = 0
    best_score = -999

    for i, d in enumerate(weather[:7]):
        s = score_day(d["temp"], d["rain"])
        if s > best_score:
            best_score = s
            best_index = i

    return best_index

def wait_message(best_index):
    if best_index == 0:
        return "🌿 Plant today — conditions are ideal."
    elif best_index == 1:
        return "🌿 Wait 1 day — tomorrow is better."
    else:
        return f"🌿 Wait {best_index} days — better conditions ahead."

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

tabs = st.tabs(["📍 Location","🌿 Build","🌼 Garden","🧠 Tips"])

# ---------- LOCATION ----------
with tabs[0]:
    zip = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zip)
        if lat:
            st.session_state.weather = get_weather(lat, lon)
            st.session_state.frost = estimate_frost(st.session_state.weather)

    if "weather" in st.session_state:
        st.subheader("Next 7 Days — Planting Outlook")

        best_index = find_best_day(st.session_state.weather)

        for i, d in enumerate(st.session_state.weather[:7]):
            date = datetime.datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a %b %d")

            color, reason = planting_score(d["temp"], d["rain"])
            highlight = " ⭐ BEST DAY" if i == best_index else ""

            st.markdown(
                f"<div class='day-card {color}'>"
                f"{date}{highlight}<br>"
                f"{d['temp']}°F | 🌧 {d['rain']}%<br>"
                f"{reason}"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("### 🌱 Planting Recommendation")
        st.success(wait_message(best_index))

# ---------- BUILD ----------
with tabs[1]:
    category = st.selectbox("Category", ["Vegetables","Flowers"])

    if category == "Vegetables":
        sub = st.selectbox("Type", ["fruit","leafy","root"])
        filtered = [p for p in plants if p["type"] == sub]
    else:
        filtered = [p for p in plants if p["type"] == "flower"]

    for i, p in enumerate(filtered):
        col1, col2 = st.columns([3,1])

        col1.write(f"**{p['name']}**")
        col1.write(p["tip"])

        if col2.button("Add", key=f"{p['name']}_{i}"):
            if p not in st.session_state.garden:
                st.session_state.garden.append(p)

        st.divider()

# ---------- GARDEN ----------
with tabs[2]:
    if st.session_state.garden:
        for p in st.session_state.garden:
            st.markdown(f"### {p['name']}")

            if "frost" in st.session_state:
                plant_date = st.session_state.frost + datetime.timedelta(weeks=2)
                harvest = plant_date + datetime.timedelta(days=p["harvest"])

                st.write(f"🌿 Plant: {plant_date}")
                st.write(f"🍅 Harvest: {harvest}")

            st.write(f"💡 {p['tip']}")
            st.divider()
    else:
        st.info("Add plants to your garden")

# ---------- TIPS ----------
with tabs[3]:
    if "weather" in st.session_state:
        best_index = find_best_day(st.session_state.weather)
        st.success(wait_message(best_index))
    else:
        st.info("Enter location first")
