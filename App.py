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
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

h1, h2, h3 { color: #2f5d3a; }
</style>
""", unsafe_allow_html=True)

# ---------- PLANTS ----------
plants = [
{
"name":"Bell Pepper",
"type":"fruit",
"harvest":75,
"tip":"Needs warm nights",
"depth":"1/4 inch",
"companions":["Tomato","Basil","Onion"],
"avoid":["Beans","Cabbage"],
"water":"Keep soil evenly moist (2-3x per week)",
"sun":"Full sun (6-8 hrs)",
"temp":"70-85F",
"care":"Stake plants early; avoid overwatering roots"
},
{
"name":"Cherry Tomato",
"type":"fruit",
"harvest":65,
"tip":"Fast grower",
"depth":"1/4 inch / deep transplant",
"companions":["Basil","Marigold"],
"avoid":["Corn","Potato"],
"water":"Deep watering 2-3x per week",
"sun":"Full sun",
"temp":"65-85F",
"care":"Prune suckers; support with cage"
},
{
"name":"Lettuce",
"type":"leafy",
"harvest":30,
"tip":"Cool weather crop",
"depth":"1/4 inch",
"companions":["Carrot","Radish"],
"avoid":[],
"water":"Light watering daily or every other day",
"sun":"Partial sun",
"temp":"45-70F",
"care":"Harvest outer leaves early"
},
{
"name":"Carrot",
"type":"root",
"harvest":70,
"tip":"Direct sow",
"depth":"1/4 inch",
"companions":["Lettuce","Onion"],
"avoid":["Dill"],
"water":"Keep soil moist during germination",
"sun":"Full sun",
"temp":"55-75F",
"care":"Thin seedlings early"
},
{
"name":"Marigold",
"type":"flower",
"harvest":50,
"tip":"Pest control powerhouse",
"depth":"1/4 inch",
"companions":["Tomato","Pepper"],
"avoid":[],
"water":"Water when soil dries",
"sun":"Full sun",
"temp":"60-80F",
"care":"Deadhead to keep blooming"
}
]

# ---------- IMAGE ----------
@st.cache_data(show_spinner=False)
def get_plant_image(name):
    name_map = {
        "Bell Pepper":"Bell_pepper",
        "Cherry Tomato":"Cherry_tomato",
        "Marigold":"Tagetes"
    }
    search = name_map.get(name, name).replace(" ", "_")
    try:
        r = requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/" + search, timeout=5).json()
        if "thumbnail" in r:
            return r["thumbnail"]["source"]
    except:
        pass
    return None

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
    return "Wait " + str(i) + " days"

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("ZipPlant Calendar")

tabs = st.tabs(["Location","Build","Garden","Tips"])

# ---------- LOCATION ----------
with tabs[0]:
    zipcode = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zipcode)
        if lat:
            st.session_state.weather = get_weather(lat, lon)

    if "weather" in st.session_state:
        best = best_day(st.session_state.weather)

        for i, d in enumerate(st.session_state.weather[:7]):
            date = datetime.datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a %b %d")
            color, reason = planting_score(d["temp"], d["rain"])
            star = " BEST" if i == best else ""

            st.markdown(
                "<div class='day-card " + color + "'>" +
                date + star + "<br>" +
                str(d["temp"]) + "F | Rain " + str(d["rain"]) + "%<br>" +
                reason +
                "</div>",
                unsafe_allow_html=True
            )

        st.success(wait_msg(best))

# ---------- BUILD ----------
with tabs[1]:
    for i, p in enumerate(plants):
        col1, col2 = st.columns([2,1])

        with col1:
            img = get_plant_image(p["name"])
            if img:
                st.image(img, use_container_width=True)

            st.write(p["name"])
            st.write("Depth:", p["depth"])
            st.write("Tip:", p["tip"])

            st.write("Companion Plants:", ", ".join(p["companions"]) if p["companions"] else "None")
            st.write("Plants to Avoid:", ", ".join(p["avoid"]) if p["avoid"] else "None")

        with col2:
            if p in st.session_state.garden:
                st.success("Added")
            else:
                if st.button("Add", key=str(i)):
                    st.session_state.garden.append(p)
                    st.toast(p["name"] + " added")

# ---------- GARDEN ----------
with tabs[2]:
    if st.session_state.garden:
        for p in st.session_state.garden:
            st.subheader(p["name"])

            img = get_plant_image(p["name"])
            if img:
                st.image(img, width=200)

            st.write("Depth:", p["depth"])
            st.write("Water:", p["water"])
            st.write("Sun:", p["sun"])
            st.write("Temp:", p["temp"])
            st.write("Care:", p["care"])

            st.write("Companion Plants:", ", ".join(p["companions"]) if p["companions"] else "None")
            st.write("Plants to Avoid:", ", ".join(p["avoid"]) if p["avoid"] else "None")

            st.divider()
    else:
        st.info("Add plants first")

# ---------- TIPS ----------
with tabs[3]:
    if "weather" in st.session_state:
        best = best_day(st.session_state.weather)
        st.success(wait_msg(best))
    else:
        st.info("Enter location first")
