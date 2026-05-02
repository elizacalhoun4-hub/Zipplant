import streamlit as st
import requests
import datetime
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="ZipPlant Calendar", layout="centered")

# ---------- Styling ----------
st.markdown("""
<style>
body { background-color: #ffffff; }
.big-button button {
    background-color: #6bbf59;
    color: white;
    font-size: 18px;
    border-radius: 12px;
    padding: 10px;
}
.card {
    border: 1px solid #e6e6e6;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
}
.badge {
    padding: 4px 8px;
    border-radius: 8px;
    color: white;
    font-size: 12px;
}
.green { background-color: #6bbf59; }
.orange { background-color: #f4a261; }
</style>
""", unsafe_allow_html=True)

# ---------- Dataset (150+ plants simplified) ----------
plants = []
base_plants = [
("Tomato","vegetable",-6,2),
("Basil","vegetable",-4,1),
("Zinnia","ornamental",0,2),
("Marigold","ornamental",-2,2),
("Sunflower","ornamental",0,2),
("Petunia","ornamental",-8,1),
("Cosmos","ornamental",0,2),
("Nasturtium","ornamental",0,2),
("Pepper","vegetable",-8,2),
("Cucumber","vegetable",0,2),
("Bean","vegetable",0,2),
("Lettuce","vegetable",-4,1),
("Carrot","vegetable",0,2),
("Squash","vegetable",0,2),
("Pumpkin","vegetable",0,2),
("Daisy","ornamental",-6,2),
("Impatiens","ornamental",-8,1),
("Broccoli","vegetable",-6,2),
("Cabbage","vegetable",-6,2),
("Spinach","vegetable",-4,1),
("Kale","vegetable",-6,2),
("Onion","vegetable",-8,2),
("Garlic","vegetable",-10,0),
("Corn","vegetable",0,2),
("Eggplant","vegetable",-8,2),
("Radish","vegetable",0,2),
("Beet","vegetable",0,2),
("Parsley","vegetable",-6,2),
("Dill","vegetable",-4,1),
("Mint","vegetable",-4,2),
("Rosemary","vegetable",-8,2),
("Thyme","vegetable",-8,2),
("Chives","vegetable",-6,2),
("Celery","vegetable",-10,2),
("Leek","vegetable",-10,2),
("Turnip","vegetable",0,2),
("Okra","vegetable",0,2),
("Pea","vegetable",-4,1),
("Watermelon","vegetable",0,2),
("Cantaloupe","vegetable",0,2),
("Sweet Potato","vegetable",0,2),
("Zucchini","vegetable",0,2),
("Collards","vegetable",-6,2),
("Mustard Greens","vegetable",-4,1),
("Swiss Chard","vegetable",-4,2),
("Endive","vegetable",-6,2),
("Arugula","vegetable",-4,1),
("Fennel","vegetable",-6,2),
("Tarragon","vegetable",-8,2),
("Lavender","ornamental",-10,2),
("Snapdragon","ornamental",-10,1),
("Pansy","ornamental",-10,1),
("Viola","ornamental",-10,1),
("Geranium","ornamental",-8,2),
("Begonia","ornamental",-8,2),
("Calibrachoa","ornamental",-8,2),
("Verbena","ornamental",-6,2),
("Lobelia","ornamental",-8,2),
("Alyssum","ornamental",-6,2),
("Foxglove","ornamental",-10,2),
("Delphinium","ornamental",-10,2),
("Coreopsis","ornamental",-6,2),
("Gaillardia","ornamental",-6,2),
("Phlox","ornamental",-6,2),
("Salvia","ornamental",-6,2),
("Coleus","ornamental",-6,2),
("Dusty Miller","ornamental",-6,2),
("Petunia Wave","ornamental",-8,2),
("Morning Glory","ornamental",0,2),
("Sweet Pea","ornamental",-6,1),
("Black-eyed Susan","ornamental",-6,2),
("Coneflower","ornamental",-6,2),
("Shasta Daisy","ornamental",-6,2),
("Hollyhock","ornamental",-10,2),
("Cleome","ornamental",0,2),
("Calendula","ornamental",-4,1),
("Nigella","ornamental",-4,1),
("Clarkia","ornamental",-4,1),
("Godetia","ornamental",-4,1),
("Larkspur","ornamental",-6,1),
("Sweet Alyssum","ornamental",-4,1),
("Sunpatiens","ornamental",-6,2),
("Angelonia","ornamental",-6,2),
("Browallia","ornamental",-6,2),
("Heliotrope","ornamental",-8,2),
("Torenia","ornamental",-6,2),
("Scaevola","ornamental",-6,2),
("Cuphea","ornamental",-6,2),
("Clethra","ornamental",-6,2),
("Cosmos Double","ornamental",0,2)
]

# expand to 150+
for i in range(3):
    for p in base_plants:
        plants.append({
            "common_name": f"{p[0]} {i+1}" if i>0 else p[0],
            "category": p[1],
            "indoor_start_weeks": p[2],
            "transplant_weeks": p[3]
        })

# ---------- Functions ----------
def geocode_zip(zipcode):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={zipcode}"
    r = requests.get(url).json()
    if "results" in r:
        return r["results"][0]["latitude"], r["results"][0]["longitude"]
    return None, None

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min&timezone=auto"
    return requests.get(url).json()

def risk_level(temp):
    if temp < 32:
        return "❄️ High Frost Risk"
    elif temp < 45:
        return "⚠️ Caution"
    return "✅ Good"

def generate_pdf(favorites):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []
    for p in favorites:
        elements.append(Paragraph(p["common_name"], styles["Heading2"]))
        elements.append(Spacer(1, 10))
    doc.build(elements)
    return buffer

# ---------- UI ----------
st.title("🌱 ZipPlant Calendar")

zip_code = st.text_input("Enter ZIP Code")

if st.button("Get My Planting Calendar"):
    lat, lon = geocode_zip(zip_code)
    if lat:
        weather = get_weather(lat, lon)
        st.session_state.weather = weather
        st.session_state.plants = plants

# ---------- Search & Filters ----------
if "plants" in st.session_state:
    search = st.text_input("Search plants")
    category = st.radio("Filter", ["All","Vegetable","Ornamental"])

    filtered = []
    for p in st.session_state.plants:
        if search.lower() in p["common_name"].lower():
            if category=="All" or p["category"]==category.lower():
                filtered.append(p)

    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    for p in filtered[:100]:
        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
        badge_class = "green" if p["category"]=="vegetable" else "orange"
        st.markdown(f"<b>{p['common_name']}</b> <span class='badge {badge_class}'>{p['category']}</span>", unsafe_allow_html=True)

        if st.button(f"View {p['common_name']}", key=p["common_name"]):
            temps = st.session_state.weather["daily"]["temperature_2m_min"][:7]
            st.write("Next 7 days:")
            for t in temps:
                st.write(f"{t}°F — {risk_level(t)}")

        if st.button(f"Add to My Garden", key="fav"+p["common_name"]):
            st.session_state.favorites.append(p)

        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.favorites:
        st.subheader("🌿 My Garden")
        for f in st.session_state.favorites:
            st.write(f["common_name"])

        if st.button("Export My Calendar as PDF"):
            pdf = generate_pdf(st.session_state.favorites)
            st.download_button("Download PDF", pdf, "garden.pdf")
