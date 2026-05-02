import streamlit as st
import requests
import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.block-container { padding-top: 1rem; }
button { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
plants = [
{"name":"Tomato","category":"vegetable","indoor":-6,"outdoor":2,"harvest_days":75,"companions":["Basil","Marigold"],"tip":"Wait until nights stay above 55°F"},
{"name":"Basil","category":"vegetable","indoor":-4,"outdoor":2,"harvest_days":40,"companions":["Tomato"],"tip":"Hates cold — plant late"},
{"name":"Zinnia","category":"ornamental","indoor":0,"outdoor":2,"harvest_days":60,"companions":[],"tip":"Loves heat"},
{"name":"Marigold","category":"ornamental","indoor":-2,"outdoor":2,"harvest_days":50,"companions":["Tomato"],"tip":"Repels pests"},
{"name":"Pepper","category":"vegetable","indoor":-8,"outdoor":2,"harvest_days":80,"companions":["Basil"],"tip":"Needs warm soil"},
{"name":"Cucumber","category":"vegetable","indoor":0,"outdoor":2,"harvest_days":55,"companions":["Beans"],"tip":"Plant after frost"},
{"name":"Lettuce","category":"vegetable","indoor":-4,"outdoor":0,"harvest_days":30,"companions":["Carrot"],"tip":"Cool weather crop"},
{"name":"Carrot","category":"vegetable","indoor":0,"outdoor":0,"harvest_days":70,"companions":["Lettuce"],"tip":"Direct sow only"},
{"name":"Sunflower","category":"ornamental","indoor":0,"outdoor":2,"harvest_days":80,"companions":[],"tip":"Direct sow"},
{"name":"Cosmos","category":"ornamental","indoor":0,"outdoor":2,"harvest_days":65,"companions":[],"tip":"Thrives in poor soil"},
]

# ---------------- FUNCTIONS ----------------
def geocode(zipcode):
    try:
        r = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={zipcode}",
            timeout=10
        ).json()
        if "results" in r:
            return r["results"][0]["latitude"], r["results"][0]["longitude"]
    except:
        pass
    return None, None

def get_weather(lat, lon):
    try:
        r = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min&timezone=auto",
            timeout=10
        ).json()
        return r["daily"]["temperature_2m_min"][:10]
    except:
        return []

def frost_risk(temp):
    if temp < 32: return "❄️ Frost"
    if temp < 45: return "⚠️ Risk"
    return "✅ Safe"

def estimate_last_frost(temps):
    today = datetime.date.today()
    for i, t in enumerate(temps):
        if t > 36:
            return today + datetime.timedelta(days=i)
    return today

def estimate_harvest(outdoor_date, harvest_days):
    start = outdoor_date + datetime.timedelta(days=harvest_days - 7)
    end = outdoor_date + datetime.timedelta(days=harvest_days + 7)
    return start, end

# -------- FAUX AI --------
def faux_ai(garden, temps, frost):
    advice = []

    if not garden:
        return "Start by adding plants to your garden 🌿"

    if temps:
        if min(temps[:3]) < 35:
            advice.append("Cold snap coming — hold off on tender plants.")
        elif min(temps[:3]) > 50:
            advice.append("Warm nights ahead — great planting conditions.")

    names = [p["name"] for p in garden]

    if "Tomato" in names and min(temps[:5]) < 45:
        advice.append("Tomatoes may struggle — consider waiting a few days.")

    if "Lettuce" in names and max(temps) > 75:
        advice.append("Lettuce may bolt soon — harvest early.")

    if not advice:
        advice.append("You're right on schedule 🌱")

    return " ".join(advice)

# -------- MOON PHASE --------
def moon_phase():
    day = datetime.date.today().day
    if day < 7: return "🌑 New Moon — plant leafy crops"
    elif day < 15: return "🌓 Growing Moon — plant above-ground crops"
    elif day < 22: return "🌕 Full Moon — strong growth period"
    else: return "🌗 Waning Moon — root crops thrive"

def make_pdf(plants):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    for p in plants:
        elements.append(Paragraph(p["name"], styles["Heading2"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    return buffer

# ---------------- STATE ----------------
if "garden" not in st.session_state:
    st.session_state.garden = []

# ---------------- UI ----------------
st.title("🌱 ZipPlant Calendar")

tabs = st.tabs(["📍 Location","🌿 Build Garden","🌼 My Garden","🧠 Smart Tips"])

# ---------- LOCATION ----------
with tabs[0]:
    zip_code = st.text_input("Enter ZIP Code")

    if st.button("Get Weather"):
        lat, lon = geocode(zip_code)

        if lat:
            temps = get_weather(lat, lon)
            st.session_state.temps = temps
            st.session_state.frost = estimate_last_frost(temps)
        else:
            st.error("ZIP not found")

    if "temps" in st.session_state:
        st.subheader("🌤 Next 10 Nights")

        for i, t in enumerate(st.session_state.temps):
            day = datetime.date.today() + datetime.timedelta(days=i)
            st.write(f"{day.strftime('%a')}: {t}°F — {frost_risk(t)}")

        st.success(f"Estimated Last Frost: {st.session_state.frost}")

# ---------- BUILD ----------
with tabs[1]:
    st.subheader("🌿 Build Your Garden")

    search = st.text_input("Search plants")

    for p in plants:
        if search.lower() in p["name"].lower():
            col1, col2 = st.columns([3,1])
            col1.write(p["name"])
            if col2.button("Add", key=p["name"]):
                if p not in st.session_state.garden:
                    st.session_state.garden.append(p)

# ---------- MY GARDEN ----------
with tabs[2]:
    st.subheader("🌼 My Garden")

    if st.session_state.garden:
        for p in st.session_state.garden:
            st.markdown(f"### {p['name']}")

            if "frost" in st.session_state:
                frost = st.session_state.frost
                indoor = frost + datetime.timedelta(weeks=p["indoor"])
                outdoor = frost + datetime.timedelta(weeks=p["outdoor"])

                st.write(f"🌱 Start indoors: {indoor}")
                st.write(f"🌿 Transplant outdoors: {outdoor}")

                harvest_start, harvest_end = estimate_harvest(outdoor, p["harvest_days"])
                st.write(f"🍅 Harvest window: {harvest_start} → {harvest_end}")

            st.write(f"💡 {p['tip']}")

            if p["companions"]:
                st.write(f"🤝 Companion plants: {', '.join(p['companions'])}")

        if st.button("📄 Export PDF"):
            pdf = make_pdf(st.session_state.garden)
            st.download_button("Download PDF", pdf, "garden.pdf")

    else:
        st.info("Add plants from Build Garden")

# ---------- SMART ----------
with tabs[3]:
    st.subheader("🧠 Smart Garden Advice")

    if "temps" in st.session_state:
        advice = faux_ai(
            st.session_state.garden,
            st.session_state.temps,
            st.session_state.frost
        )
        st.success(advice)

        st.write("🌙 Moon Phase:")
        st.write(moon_phase())
    else:
        st.info("Enter location first")
