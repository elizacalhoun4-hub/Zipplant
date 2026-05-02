import streamlit as st
import requests
import datetime

st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
.block-container { padding-top: 1rem; }

.card {
    background: white;
    padding: 16px;
    border-radius: 18px;
    margin-bottom: 12px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}

.category-title {
    font-size: 20px;
    margin-top: 10px;
    margin-bottom: 5px;
}

.stButton>button {
    border-radius: 14px;
    padding: 10px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ---------- REAL PLANTS ----------
plants = [
# Vegetables - Fruit
{"name":"Bell Pepper","type":"fruit","category":"vegetable","harvest":75,"tip":"Needs warm nights"},
{"name":"Jalapeño Pepper","type":"fruit","category":"vegetable","harvest":70,"tip":"Loves heat"},
{"name":"Cherry Tomato","type":"fruit","category":"vegetable","harvest":65,"tip":"Fast producer"},
{"name":"Roma Tomato","type":"fruit","category":"vegetable","harvest":75,"tip":"Great for sauces"},
{"name":"Cucumber","type":"fruit","category":"vegetable","harvest":55,"tip":"Needs consistent water"},
{"name":"Zucchini","type":"fruit","category":"vegetable","harvest":50,"tip":"Produces quickly"},

# Vegetables - Leafy
{"name":"Romaine Lettuce","type":"leafy","category":"vegetable","harvest":30,"tip":"Cool weather crop"},
{"name":"Spinach","type":"leafy","category":"vegetable","harvest":35,"tip":"Grows fast in spring"},
{"name":"Kale","type":"leafy","category":"vegetable","harvest":55,"tip":"Cold hardy"},

# Vegetables - Root
{"name":"Carrot","type":"root","category":"vegetable","harvest":70,"tip":"Direct sow only"},
{"name":"Radish","type":"root","category":"vegetable","harvest":30,"tip":"Very fast crop"},
{"name":"Beet","type":"root","category":"vegetable","harvest":60,"tip":"Edible greens too"},

# Flowers
{"name":"Zinnia","type":"flower","category":"flower","harvest":60,"tip":"Loves heat"},
{"name":"Marigold","type":"flower","category":"flower","harvest":50,"tip":"Repels pests"},
{"name":"Sunflower","type":"flower","category":"flower","harvest":80,"tip":"Direct sow"},
{"name":"Cosmos","type":"flower","category":"flower","harvest":65,"tip":"Low maintenance"},
{"name":"Lavender","type":"flower","category":"flower","harvest":90,"tip":"Needs sun + drainage"},
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

def harvest_window(outdoor, days):
    return outdoor + datetime.timedelta(days=days)

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("🌱 ZipPlant Calendar")

tabs = st.tabs(["📍 Location","🌿 Build Garden","🌼 My Garden","🧠 Advice"])

# ---------- LOCATION ----------
with tabs[0]:
    st.subheader("Where are you planting?")

    zip = st.text_input("ZIP Code")

    if st.button("Get Weather"):
        lat, lon = geocode(zip)
        if lat:
            temps = weather(lat, lon)
            st.session_state.temps = temps
            st.session_state.frost = frost(temps)

    if "temps" in st.session_state:
        for t in st.session_state.temps:
            st.markdown(f"<div class='card'>🌙 {t}°F</div>", unsafe_allow_html=True)

# ---------- BUILD ----------
with tabs[1]:
    st.subheader("Choose what you want to grow")

    category = st.radio("Category", ["Vegetables","Flowers"], horizontal=True)

    if category == "Vegetables":
        sub = st.radio("Type", ["Fruit","Leafy","Root"], horizontal=True)
        filtered = [p for p in plants if p["category"]=="vegetable" and p["type"]==sub.lower()]
    else:
        filtered = [p for p in plants if p["category"]=="flower"]

    st.markdown("<div class='section'></div>", unsafe_allow_html=True)

    for p in filtered:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.markdown(f"### {p['name']}")
        st.write(f"⏱ Harvest: ~{p['harvest']} days")
        st.write(f"💡 {p['tip']}")

        if st.button("Add to Garden", key=p["name"]):
            if p not in st.session_state.garden:
                st.session_state.garden.append(p)

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- GARDEN ----------
with tabs[2]:
    st.subheader("Your Garden Plan")

    if st.session_state.garden:
        for p in st.session_state.garden:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            st.markdown(f"### {p['name']}")

            if "frost" in st.session_state:
                f = st.session_state.frost
                outdoor = f + datetime.timedelta(weeks=2)
                harvest_date = harvest_window(outdoor, p["harvest"])

                st.write(f"🌿 Plant: {outdoor}")
                st.write(f"🍅 Harvest: ~{harvest_date}")

            st.write(f"💡 {p['tip']}")

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Add some plants first 🌱")

# ---------- ADVICE ----------
with tabs[3]:
    if "temps" in st.session_state:
        if min(st.session_state.temps[:3]) < 35:
            st.warning("Cold snap coming — wait before planting")
        else:
            st.success("Conditions look good 🌿")
    else:
        st.info("Enter location first")
