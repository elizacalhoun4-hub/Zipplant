import streamlit as st
import requests
import datetime
from plants_data import plants

st.set_page_config(page_title="ZipPlant 🌱", layout="centered", page_icon="🌱")

# Theme and Helpers (same as previous rich version)
st.markdown("""<style>.stApp { background-color: #0b0f14; color: #e6edf3; } h1, h2, h3 { color: #9be28f; } .plant-card { background: #161b22; padding: 1.2rem; border-radius: 12px; border: 1px solid #2a3a2f; margin-bottom: 1rem; } .granny-box { background: #1f2a1f; padding: 1.2rem; border-radius: 12px; border: 2px solid #9be28f; margin-bottom: 1.5rem; font-size: 1.05em; } .alert-banner { background: #4a1f1f; padding: 1rem; border-radius: 12px; border: 2px solid #ff6b6b; margin-bottom: 1rem; }</style>""", unsafe_allow_html=True)

# (Keep all the weather helpers from the rich version you liked — get_weather, best_day, soil_readiness, get_alerts, etc.)

# STATE
if "garden" not in st.session_state: st.session_state.garden = []
if "weather" not in st.session_state: st.session_state.weather = None
if "zone" not in st.session_state: st.session_state.zone = None
if "zip_code" not in st.session_state: st.session_state.zip_code = ""

st.title("ZipPlant 🌱")
st.markdown("**Find the best planting day • Build your garden • Grow smarter**")
st.divider()

tabs = st.tabs(["📍 Location", "🌱 Build Garden", "🌿 My Garden"])

# LOCATION TAB — keep the rich version you liked (alerts, soil, thirst meter, etc.)

with tabs[0]:
    # Paste the full rich Location tab code from earlier messages here
    pass  # (Use the rich version I gave you previously)

# BUILD GARDEN TAB — keep enhanced version

with tabs[1]:
    # Use the enhanced version with filters, zone badges, quick-add, Granny says, etc.
    pass

# ==================== MY GARDEN TAB (Fully Detailed) ====================
with tabs[2]:
    if not st.session_state.garden:
        st.info("Your garden is empty. Go add some plants!")
    else:
        st.subheader(f"My Garden ({len(st.session_state.garden)} plants)")
        for i, p in enumerate(st.session_state.garden[:]):
            with st.expander(f"🌱 {p['name']}", expanded=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    if st.session_state.weather:
                        st.markdown(f"**Best planting day:** {best_day(st.session_state.weather)}")
                    st.write(f"**Spacing:** {p.get('spacing')} | **Row Spacing:** {p.get('row_spacing', 'N/A')}")
                    st.write(f"**Sowing Depth:** {p.get('sowing_depth')} | **Germination:** {p.get('germination_time')}")
                    st.write(f"**For Couple:** {p.get('couple')} | **For Family of 4:** {p.get('family4')}")
                    st.write(f"**Start:** {p.get('start')}")
                    st.write(f"**Care:** {p.get('care')}")
                    st.write(f"**Harvest Window:** {p.get('harvest_window')} | **Yield:** {p.get('yield')}")
                    st.write(f"**Companions:** {', '.join(p.get('companions', [])) or 'None listed'}")
                    st.write(f"**Avoid:** {', '.join(p.get('avoid', [])) or 'None listed'}")
                    st.markdown(f"**🌾 Granny Fanny says:** *{p.get('granny_says', 'Great choice!')}*")
                with col_b:
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.garden.pop(i)
                        st.rerun()

st.caption("Made with ❤️ for gardeners")
