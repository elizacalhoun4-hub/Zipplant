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
    return ["Plant today", "Wait 1 day"] + [f"Wait {i} days" for i in range(2,10)][i:i+1]

# ---------- CLEAN DATA ----------
def clean_plants(plants):
    unique = {}

    for p in plants:
        base = p["name"].split(" Variant")[0]

        if base not in unique:
            new_p = p.copy()
            new_p["name"] = base
            new_p["cultivars"] = []
            unique[base] = new_p

        if p.get("cultivars"):
            for c in p["cultivars"]:
                cname = c["name"].split(" ")[0]

                if cname not in [x["name"] for x in unique[base]["cultivars"]]:
                    unique[base]["cultivars"].append({
                        "name": cname,
                        "description": c["description"]
                    })

    return list(unique.values())

plants = clean_plants(plants)

# ---------- GARDEN INTELLIGENCE ----------
def garden_info(name):
    name = name.lower()

    if "tomato" in name:
        return ("2–4 per person","4–6","8–12","Canning, freeze, sauce","Fresh, pasta, sauce")
    if "lettuce" in name:
        return ("6–10 per person","10–15","20–30","Fridge short-term","Salads")
    if "carrot" in name:
        return ("20–30","40–60","80–120","Root cellar, freeze","Roasting, soups")

    return ("Varies","Varies","Varies","Depends","General use")

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("ZipPlant Calendar 🌱")
tabs = st.tabs(["Location","Build","Garden"])

# ---------- LOCATION ----------
with tabs[0]:
    zip = st.text_input("ZIP Code")

    if st.button("Get Forecast"):
        lat, lon = geocode(zip)
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
    cats = sorted(set(p["category"] for p in plants))
    selected = st.selectbox("Filter", ["All"] + cats)

    for i,p in enumerate(plants):
        if selected!="All" and p["category"]!=selected:
            continue

        col1,col2 = st.columns([2,1])

        with col1:
            st.subheader(p["name"])
            st.caption(p["category"])
            st.write("Depth:", p["depth"])
            st.write("Care:", p["care"])

            if p["cultivars"]:
                with st.expander("Cultivars"):
                    for c in p["cultivars"]:
                        st.write(f"{c['name']}: {c['description']}")

        with col2:
            if st.button("Add", key=str(i)):
                st.session_state.garden.append(p)

# ---------- GARDEN ----------
with tabs[2]:
    for p in st.session_state.garden:
        st.subheader(p["name"])

        info = garden_info(p["name"])
        st.write("👤 Per Person:", info[0])
        st.write("👨‍👩‍👧 Family 2:", info[1])
        st.write("👨‍👩‍👧‍👦 Family 4:", info[2])
        st.write("🥫 Storage:", info[3])
        st.write("🍳 Use:", info[4])

        if p["cultivars"]:
            st.write("Cultivars:")
            for c in p["cultivars"]:
                st.write(f"- {c['name']}")

        st.divider()
