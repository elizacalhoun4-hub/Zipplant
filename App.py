import streamlit as st
import requests
import datetime

st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# ---------- CLEAN STYLE ----------
st.markdown("""
<style>
.block-container { padding-top: 1rem; }
h1, h2, h3 { color: #2f5d3a; }
</style>
""", unsafe_allow_html=True)

# ---------- REAL PLANT DATA ----------
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

def weather(lat, lon):
    r = requests.get(
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_min"
        f"&temperature_unit=fahrenheit"
        f"&timezone=auto"
    ).json()
    return [round(t) for t in r["daily"]["temperature_2m_min"][:7]]

def frost(temps):
    today = datetime.date.today()
    for i,t in enumerate(temps):
        if t > 36:
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

    if st.button("Get Weather"):
        lat, lon = geocode(zip)
        if lat:
            st.session_state.temps = weather(lat, lon)
            st.session_state.frost = frost(st.session_state.temps)

    if "temps" in st.session_state:
        st.subheader("Next 7 Nights")
        for t in st.session_state.temps:
            st.write(f"{t}°F")

# ---------- BUILD ----------
with tabs[1]:
    st.subheader("Choose your plants")

    category = st.selectbox("Category", ["Vegetables","Flowers"])

    if category == "Vegetables":
        sub = st.selectbox("Type", ["fruit","leafy","root"])
        filtered = [p for p in plants if p["type"] == sub]
    else:
        filtered = [p for p in plants if p["type"] == "flower"]

    for i, p in enumerate(filtered):
        col1, col2 = st.columns([3,1])

        col1.write(f"**{p['name']}**")
        col1.write(f"Harvest ~{p['harvest']} days")
        col1.write(p["tip"])

        # ✅ FIXED UNIQUE KEYS
        if col2.button("Add", key=f"add_{p['name']}_{i}"):
            if p not in st.session_state.garden:
                st.session_state.garden.append(p)

        st.divider()

# ---------- GARDEN ----------
with tabs[2]:
    st.subheader("Your Garden")

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
        st.info("Add some plants")

# ---------- TIPS ----------
with tabs[3]:
    if "temps" in st.session_state:
        if min(st.session_state.temps) < 35:
            st.warning("Cold nights ahead — wait to plant")
        else:
            st.success("Conditions look good 🌿")
    else:
        st.info("Enter location first")
