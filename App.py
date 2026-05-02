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

# ---------- PLANT DATA ----------
plants = [
{"name":"Bell Pepper","type":"fruit","harvest":75,"tip":"Needs warm nights","depth":"¼ inch","companions":["Tomato","Basil","Onion"],"avoid":["Beans","Cabbage"]},
{"name":"Jalapeño","type":"fruit","harvest":70,"tip":"Loves heat","depth":"¼ inch","companions":["Tomato","Carrot"],"avoid":["Beans"]},

{"name":"Cherry Tomato","type":"fruit","harvest":65,"tip":"Fast grower","depth":"¼ inch / deep transplant","companions":["Basil","Marigold","Carrot"],"avoid":["Corn","Potato"]},
{"name":"Roma Tomato","type":"fruit","harvest":75,"tip":"Great for sauces","depth":"¼ inch / deep transplant","companions":["Basil","Onion"],"avoid":["Corn"]},

{"name":"Cucumber","type":"fruit","harvest":55,"tip":"Needs steady water","depth":"1 inch","companions":["Beans","Radish"],"avoid":["Potato"]},

{"name":"Lettuce","type":"leafy","harvest":30,"tip":"Cool weather crop","depth":"¼ inch","companions":["Carrot","Radish"],"avoid":[]},
{"name":"Spinach","type":"leafy","harvest":35,"tip":"Spring favorite","depth":"½ inch","companions":["Strawberry"],"avoid":[]},

{"name":"Carrot","type":"root","harvest":70,"tip":"Direct sow","depth":"¼ inch","companions":["Lettuce","Onion"],"avoid":["Dill"]},
{"name":"Radish","type":"root","harvest":30,"tip":"Very fast","depth":"½ inch","companions":["Cucumber","Carrot"],"avoid":["Hyssop"]},

{"name":"Marigold","type":"flower","harvest":50,"tip":"Pest control powerhouse","depth":"¼ inch","companions":["Tomato","Pepper"],"avoid":[]},
{"name":"Sunflower","type":"flower","harvest":80,"tip":"Direct sow","depth":"1 inch","companions":["Corn"],"avoid":["Potato"]},
]

# ---------- IMAGE ----------
@st.cache_data(show_spinner=False)
def get_plant_image(name):
    name_map = {
        "Bell Pepper":"Bell_pepper",
        "Roma Tomato":"Plum_tomato",
        "Cherry Tomato":"Cherry_tomato",
        "Beet":"Beetroot",
        "Marigold":"Tagetes",
        "Cosmos":"Cosmos_(plant)"
    }
    search = name_map.get(name, name).replace(" ", "_")
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{search}", timeout=5).json()
        if "thumbnail" in r:
            return r["thumbnail"]["source"]
    except:
        pass
    return None

# ---------- WEATHER ----------
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
    if temp < 36: return "red","Too cold"
    if rain > 70: return "red","Heavy rain"
    if temp < 50 or rain > 40: return "yellow","Caution"
    return "green","Good day"

def score_day(temp, rain):
    return temp - rain

def best_day(weather):
    scores = [score_day(d["temp"], d["rain"]) for d in weather[:7]]
    return scores.index(max(scores))

def wait_msg(i):
    if i==0: return "🌿 Plant today"
    if i==1: return "🌿 Wait 1 day"
    return f"🌿 Wait {i} days"

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

    if "weather" in st.session_state:
        best = best_day(st.session_state.weather)

        for i,d in enumerate(st.session_state.weather[:7]):
            date = datetime.datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a %b %d")
            color, reason = planting_score(d["temp"], d["rain"])
            star = " ⭐ BEST" if i==best else ""

            st.markdown(
                f"<div class='day-card {color}'>"
                f"{date}{star}<br>{d['temp']}°F | 🌧 {d['rain']}%<br>{reason}"
                f"</div>", unsafe_allow_html=True
            )

        st.success(wait_msg(best))

# ---------- BUILD ----------
with tabs[1]:
    st.caption(f"{len(st.session_state.garden)} plants selected")

    category = st.selectbox("Category",["Vegetables","Flowers"])

    if category=="Vegetables":
        sub = st.selectbox("Type",["fruit","leafy","root"])
        filtered=[p for p in plants if p["type"]==sub]
    else:
        filtered=[p for p in plants if p["type"]=="flower"]

    for i,p in enumerate(filtered):
        col1,col2=st.columns([2,1])

        with col1:
            st.markdown("<div class='plant-card'>",unsafe_allow_html=True)

            img=get_plant_image(p["name"])
            if img:
                st.image(img,use_container_width=True)
            else:
                st.markdown("🌿",unsafe_allow_html=True)

            st.markdown(f"**{p['name']}**")
            st.caption(f"Harvest ~{p['harvest']} days")
            st.write(f"🌾 Depth: {p['depth']}")
            st.write(f"💡 {p['tip']}")

            if p["companions"]:
                st.write(f"🤝 {', '.join(p['companions'])}")
            if p["avoid"]:
                st.write(f"❌ Avoid: {', '.join(p['avoid'])}")

            st.markdown("</div>",unsafe_allow_html=True)

        with col2:
            if p in st.session_state.garden:
                st.success("✓ Added")
            else:
                if st.button("Add",key=f"{p['name']}_{i}"):
                    st.session_state.garden.append(p)
                    st.toast(f"{p['name']} added 🌿")

# ---------- GARDEN ----------
with tabs[2]:
    if st.session_state.garden:
        for p in st.session_state.garden:
            st.markdown(f"### {p['name']}")

            img=get_plant_image(p["name"])
            if img:
                st.image(img,width=200)

            st.write(f"🌾 Depth: {p['depth']}")
            st.write(f"🤝 {', '.join(p['companions'])}")
            if p["avoid"]:
                st.write(f"❌ Avoid: {', '.join(p['avoid'])}")

            st.divider()
    else:
        st.info("Add plants first 🌱")

# ---------- TIPS ----------
with tabs[3]:
    if "weather" in st.session_state:
        best = best_day(st.session_state.weather)
        st.success(wait_msg(best))
    else:
        st.info("Enter location")
