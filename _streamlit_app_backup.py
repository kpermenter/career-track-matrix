"""
Engineering Growth Framework - Main Entry Point
This is a minimal entry point. All content is in the pages directory.
"""

import streamlit as st

st.set_page_config(
    page_title="Engineering Career Track",
    page_icon="🧭",
    layout="wide"
)

# Minimal content to hide this tab
st.markdown("""
<style>
/* Hide the main tab from showing in sidebar */
.css-1d391kg { display: none; }
</style>
""", unsafe_allow_html=True)

# Just show a minimal message
st.markdown("### 👈 Use the sidebar to navigate")