import streamlit as st
import requests
import datetime
from plants_data import plants

st.set_page_config(page_title="ZipPlant 🌱", layout="centered", page_icon="🌱")

# Theme (same as before)
st.markdown("""<style> ... </style>""", unsafe_allow_html=True)  # keep your existing theme

# State
if "garden" not in st.session_state: st.session_state.garden = []
if "weather" not in st.session_state: st.session_state.weather = None
if "zone" not in st.session_state: st.session_state.zone = None
if "zip_code" not in st.session_state: st.session_state.zip_code = ""

st.title("ZipPlant 🌱")
st.markdown("**Find the best planting day • Build your garden • Grow smarter**")
st.divider()

tabs = st.tabs(["📍 Location", "🌱 Build Garden", "🌿 My Garden"])

# LOCATION TAB (kept rich as before - not changed)
with tabs[0]:
    # (your rich weather tab code stays here unchanged)
    pass

# BUILD GARDEN TAB (kept as is)
with tabs[1]:
    # (your current Build Garden code)
    pass

# ==================== MY GARDEN TAB - UPGRADED ====================
with tabs[2]:
    if not st.session_state.garden:
        st.info("Your garden is empty. Go add some plants!")
    else:
        st.subheader(f"My Garden ({len(st.session_state.garden)} plants)")
        for i, p in enumerate(st.session_state.garden[:]):
            with st.expander(f"🌱 {p['name']}", expanded=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    # Dynamic Granny Tip
                    granny_tip = p.get('granny_says', 'Great choice!')
                    if 'germination_temp' in p and st.session_state.weather:
                        soil_temp = st.session_state.weather["temperature_2m_min"][0] - 5
                        if soil_temp < p.get('germination_temp', 60):
                            granny_tip += " 🌱 Soil is still a bit cool for this one."
                    st.markdown(f"**🌾 Granny Fanny says:** *{granny_tip}*")

                    # Grid Spacing Toggle
                    if st.checkbox("Show Grid Spacing (plants per sq ft)", key=f"grid_{i}"):
                        st.write(f"**Grid Spacing:** {p.get('grid_spacing', 'N/A')} plants per square foot")
                    else:
                        st.write(f"**Traditional Spacing:** {p.get('spacing')}")

                    st.write(f"**Sowing Depth:** {p.get('sowing_depth_desc', p.get('sowing_depth', 'N/A'))}")
                    st.write(f"**Companions:** {', '.join(p.get('companions', [])) or 'None listed'}")
                    st.write(f"**Avoid:** {', '.join(p.get('avoid', [])) or 'None listed'}")

                    # Cultural Heritage Badge
                    if p.get('heritage_origin'):
                        st.success(f"🏷️ {p['heritage_origin']}")

                with col_b:
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.garden.pop(i)
                        st.rerun()

st.caption("Made with ❤️ for gardeners")
