"""Shared design tokens and global CSS injection."""

import streamlit as st

from ui.styles.generator import generate_global_css

STAGE_ORDER = ["prompt", "outline_review", "reference_image_setup", "generating", "preview"]


def inject_global_css(lang: str = "ar") -> None:
    """Inject Google Fonts and token-driven global CSS into the Streamlit app."""
    font_link = """
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    """
    css = generate_global_css(lang)
    st.markdown(font_link + css, unsafe_allow_html=True)
