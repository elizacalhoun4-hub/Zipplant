import streamlit as st
import requests
import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# ---------- 🌸 STYLE ----------
st.markdown("""
<style>

/* Background */
body {
    background-color: #f7fdf7;
}

/* Container spacing */
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

/* Headings */
h1, h2, h3 {
    color: #2f5d3a;
}

/* Buttons */
.stButton>button {
    border-radius: 20px;
    background-color: #6bbf59;
    color: white;
    font-size: 16px;
    padding: 10px;
    border: none;
}

/* Pills */
.pill {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 20px;
    background-color: #e6f4ea;
    margin: 4px;
    cursor: pointer;
}

/* Cards */
.card {
    background: white;
    padding: 16px;
    border-radius: 18px;
    margin-bottom: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* Section divider */
.section {
    margin-top: 20px;
    margin-bottom: 10px;
}

/* Weather */
.weather {
    background: #eef9f0;
    padding: 12px;
    border-radius: 14px;
    margin-bottom: 8px;
}

</style>
""", unsafe_allow_html=True)

# ---------- 🌿 DATA ----------
def generate_plants():
    veg = [
        ("Tomato","fruit",75),("Pepper","fruit",80),("Cucumber","fruit",55),
        ("Zucchini","fruit",50),("Bean","fruit",50),
        ("Carrot","root",70),("Beet","root",60),("Radish","root",30),
        ("Lettuce","leafy",30),("Spinach","leafy",35),("Kale","leafy",55)
    ]

    flowers = [
        ("Zinnia",60),("Marigold",50),("Sunflower",80),
        ("Cosmos",65),("Petunia",70),("Lavender",90)
    ]

    plants = []
    for i in range(5):
        for v in veg:
            plants.append({
                "name": v[0] if i==0 else f"{v[0]} {i+1}",
                "category":"vegetable",
                "sub":v[1],
                "harvest_days":v[2],
                "indoor":-6,
                "outdoor":2,
                "tip":"Plant after frost"
            })
        for f in flowers:
            plants.append({
                "name": f[0] if i==0 else f"{f[0]} {i+1}",
                "category":"flower",
                "sub":"flower",
                "harvest_days":f[1],
                "indoor":-4,
                "outdoor":2,
                "tip":"Full sun preferred"
            })
    return plants

plants = generate_plants()

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
    return [round(t) for t in r["daily"]["temperature_2m_min"][:10]]

def frost(temps):
    today = datetime.date.today()
    for i,t in enumerate(temps):
        if t > 36:
            return today + datetime.timedelta(days=i)
    return today

def harvest(outdoor, days):
    return (
        outdoor + datetime.timedelta(days=days-7),
        outdoor + datetime.timedelta(days=days+7)
    )

def faux_ai(garden, temps):
    if not garden: return "Add a few plants to begin 🌿"
    if min(temps[:3]) < 35: return "Cold snap coming — wait to plant"
    if min(temps[:3]) > 50: return "Perfect planting weather 🌱"
    return "You're on track 🌼"

def make_pdf(garden):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf)
    styles = getSampleStyleSheet()
    el = []
    for p in garden:
        el.append(Paragraph(p["name"], styles["Heading2"]))
        el.append(Spacer(1,10))
    doc.build(el)
    return buf

# ---------- STATE ----------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------- UI ----------
st.title("🌱 ZipPlant Calendar")

tabs = st.tabs(["📍","🌿","🌼","🧠"])

# ---------- LOCATION ----------
with tabs[0]:
    st.subheader("Where are you planting?")

    zip = st.text_input("ZIP Code")

    if st.button("Get Weather 🌤"):
        lat, lon = geocode(zip)
        if lat:
            temps = weather(lat, lon)
            st.session_state.temps = temps
            st.session_state.frost = frost(temps)

    if "temps" in st.session_state:
        for i,t in enumerate(st.session_state.temps[:7]):
            day = datetime.date.today() + datetime.timedelta(days=i)
            st.markdown(
                f"<div class='weather'>{day.strftime('%a')} — {t}°F</div>",
                unsafe_allow_html=True
            )

# ---------- BUILD ----------
with tabs[1]:
    st.subheader("Choose your plants 🌿")

    category = st.radio("Category", ["Vegetables","Flowers"], horizontal=True)

    if category == "Vegetables":
        sub = st.radio("Type", ["Leafy","Root","Fruit"], horizontal=True)
        filtered = [p for p in plants if p["category"]=="vegetable" and p["sub"]==sub.lower()]
    else:
        filtered = [p for p in plants if p["category"]=="flower"]

    cols = st.columns(2)

    for i,p in enumerate(filtered[:30]):
        with cols[i%2]:
            if st.button(p["name"], key=p["name"]):
                if p not in st.session_state.garden:
                    st.session_state.garden.append(p)

# ---------- GARDEN ----------
with tabs[2]:
    st.subheader("Your garden 🌼")

    if st.session_state.garden:
        for p in st.session_state.garden:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            st.markdown(f"### {p['name']}")

            if "frost" in st.session_state:
                f = st.session_state.frost
                outdoor = f + datetime.timedelta(weeks=p["outdoor"])
                start = f + datetime.timedelta(weeks=p["indoor"])

                st.write(f"🌱 Start: {start}")
                st.write(f"🌿 Plant: {outdoor}")

                h1,h2 = harvest(outdoor, p["harvest_days"])
                st.write(f"🍅 Harvest: {h1} → {h2}")

            st.write(f"💡 {p['tip']}")

            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("📄 Export Garden PDF"):
            pdf = make_pdf(st.session_state.garden)
            st.download_button("Download", pdf, "garden.pdf")

    else:
        st.info("Add plants to begin 🌱")

# ---------- SMART ----------
with tabs[3]:
    st.subheader("Garden wisdom 🧠")

    if "temps" in st.session_state:
        st.success(faux_ai(st.session_state.garden, st.session_state.temps))
    else:
        st.info("Enter location first 🌤")
