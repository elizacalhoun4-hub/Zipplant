import streamlit as st
import requests
import datetime
from plants_data import plants

st.set_page_config(page_title="ZipPlant 🌱", layout="centered", page_icon="🌱")

# ==================== THEME ====================
st.markdown("""
<style>
    .stApp { background-color: #0b0f14; color: #e6edf3; }
    h1, h2, h3 { color: #9be28f; }
    .stButton>button { background: #1f6f4a; color: white; border-radius: 8px; padding: 0.5rem 1rem; }
    .plant-card { background: #161b22; padding: 1.2rem; border-radius: 12px; border: 1px solid #2a3a2f; margin-bottom: 1rem; }
    .success-msg { color: #9be28f; font-weight: 500; }
    .granny-box { background: #1f2a1f; padding: 1.2rem; border-radius: 12px; border: 2px solid #9be28f; margin-bottom: 1.5rem; font-size: 1.05em; }
    .alert-banner { background: #4a1f1f; padding: 1rem; border-radius: 12px; border: 2px solid #ff6b6b; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ==================== HELPERS (same as before) ====================
def get_weather(zip_code): ...   # (unchanged from previous version)
def get_hardiness_zone(zip_code): ... 
def format_date(date_str): ...
def best_day(weather): ...
def soil_readiness(temp_f): ...
def get_alerts(weather): ...

# ==================== STATE ====================
if "garden" not in st.session_state: st.session_state.garden = []
if "weather" not in st.session_state: st.session_state.weather = None
if "zone" not in st.session_state: st.session_state.zone = None
if "zip_code" not in st.session_state: st.session_state.zip_code = ""

st.title("ZipPlant 🌱")
st.markdown("**Find the best planting day • Build your garden • Grow smarter**")
st.divider()

tabs = st.tabs(["📍 Location", "🌱 Build Garden", "🌿 My Garden"])

# ==================== LOCATION TAB (unchanged) ====================
with tabs[0]:
    # (keep the exact same code from the previous complete version)

# ==================== BUILD GARDEN TAB — ENHANCED ====================
with tabs[1]:
    st.subheader("Available Plants")
    
    col_search, col_zone = st.columns([3, 1])
    with col_search:
        search_term = st.text_input("🔍 Search plants", placeholder="tomato, basil, red, easy, heirloom...", key="plant_search")
    with col_zone:
        st.caption(f"🌍 Your Zone: {st.session_state.zone or '??'}")

    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        category = st.selectbox("Category", ["All", "Tomatoes", "Peppers", "Herbs", "Greens", "Roots", "Vegetables"])
    with colf2:
        sun_pref = st.selectbox("Sun", ["Any", "Full sun", "Partial"])
    with colf3:
        difficulty = st.selectbox("Skill Level", ["Any", "Beginner", "Intermediate"])
    with colf4:
        plant_type = st.selectbox("Type", ["Any", "Heirloom", "Hybrid"])

    # Filter logic with new fields
    filtered = []
    for p in plants:
        matches_search = (not search_term or 
                         search_term.lower() in p["name"].lower() or 
                         search_term.lower() in p.get("type","").lower() or 
                         search_term.lower() in p.get("tags","").lower())
        matches_cat = (category == "All" or category.lower() in p["type"].lower())
        matches_sun = (sun_pref == "Any" or sun_pref.lower() in p["sun"].lower())
        matches_diff = (difficulty == "Any" or difficulty.lower() in p.get("difficulty","").lower())
        matches_type = (plant_type == "Any" or plant_type.lower() == p.get("heirloom_hybrid","").lower())

        if matches_search and matches_cat and matches_sun and matches_diff and matches_type:
            filtered.append(p)

    if not filtered:
        st.info("No plants found. Try different filters.")
    else:
        cols = st.columns(2)
        for idx, p in enumerate(filtered):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="plant-card">
                    <h3>{p['name']}</h3>
                    <small><em>{p['type']}</em></small><br>
                    <em>{p['pitch']}</em>
                </div>
                """, unsafe_allow_html=True)

                # Zone & Type badges
                if st.session_state.zone:
                    st.success("✅ Great for your zone")
                st.caption(f"**{p['heirloom_hybrid']}** • Zones {p['recommended_zones']}")

                st.write(f"**Spacing:** {p['spacing']}")
                st.write(f"**Sun:** {p['sun']}")
                st.write(f"**Days to Harvest:** {p['harvest_days']}")

                if "granny_says" in p:
                    st.markdown(f"**🌾 Granny says:** *{p['granny_says']}*")

                # Companion quick-add (same as before)
                if p.get("companions"):
                    st.markdown("**Great Companions:**")
                    for comp in p["companions"]:
                        if st.button(f"+ {comp}", key=f"comp_{idx}_{comp}"):
                            companion = next((pl for pl in plants if pl["name"] == comp), None)
                            if companion and companion not in st.session_state.garden:
                                st.session_state.garden.append(companion)
                                st.success(f"Added {comp}!")
                                st.rerun()

                if
