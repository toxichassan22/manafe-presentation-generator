"""Real Estate Proposal Generator – Streamlit Entry Point"""
import sys
import textwrap
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.branding import branding
from config.settings import settings
from ui import i18n
from ui.design_tokens import inject_global_css
from utils import state_manager as sm
from assets import LOGO_B64

# Validate required settings on startup
_validation_errors = settings.validate()
for _err in _validation_errors:
    st.warning(f"⚙️ {_err}")


st.set_page_config(
    page_title=f"مواد العروض العقارية | {branding.COMPANY_NAME_AR}",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

sm.init_state()
st.logo(LOGO_B64)
inject_global_css(i18n.get_lang())

def render_landing():
    """Clean, corporate landing page for internal employees."""
    render_top_navbar("Home")
    
    # Simple, elegant hero without dashboard or stats
    raw_html = """<style>
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}

.hero-scene {
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    background: radial-gradient(circle at 50% 30%, #FFFFFF, #F8FAFC);
    position: relative;
    overflow: hidden;
    padding: 2rem;
}

/* Subtle corporate pattern background */
.hero-scene::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: 
        linear-gradient(30deg, rgba(103, 13, 12, 0.02) 12%, transparent 12.5%, transparent 87%, rgba(103, 13, 12, 0.02) 87.5%, rgba(103, 13, 12, 0.02)),
        linear-gradient(150deg, rgba(103, 13, 12, 0.02) 12%, transparent 12.5%, transparent 87%, rgba(103, 13, 12, 0.02) 87.5%, rgba(103, 13, 12, 0.02)),
        linear-gradient(30deg, rgba(103, 13, 12, 0.02) 12%, transparent 12.5%, transparent 87%, rgba(103, 13, 12, 0.02) 87.5%, rgba(103, 13, 12, 0.02)),
        linear-gradient(150deg, rgba(103, 13, 12, 0.02) 12%, transparent 12.5%, transparent 87%, rgba(103, 13, 12, 0.02) 87.5%, rgba(103, 13, 12, 0.02)),
        linear-gradient(60deg, rgba(194, 161, 118, 0.02) 25%, transparent 25.5%, transparent 75%, rgba(194, 161, 118, 0.02) 75%, rgba(194, 161, 118, 0.02)),
        linear-gradient(60deg, rgba(194, 161, 118, 0.02) 25%, transparent 25.5%, transparent 75%, rgba(194, 161, 118, 0.02) 75%, rgba(194, 161, 118, 0.02));
    background-size: 80px 140px;
    background-position: 0 0, 0 0, 40px 70px, 40px 70px, 0 0, 40px 70px;
    pointer-events: none;
    animation: fadeIn 1.5s ease both;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.hero-content {
    max-width: 800px;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    animation: slideUp 0.8s ease both;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    color: #670D0C;
    margin-bottom: 1.5rem;
    line-height: 1.3;
}

.hero-subtitle {
    font-size: 1.2rem;
    color: #475569;
    margin-bottom: 3.5rem;
    line-height: 1.6;
    max-width: 650px;
}

.hero-logo {
    height: 130px;
    object-fit: contain;
    margin-bottom: 2.5rem;
}

@media (max-width: 768px) {
    .hero-title { font-size: 2.2rem; }
    .hero-logo { height: 90px; }
}
</style>

<div class="hero-scene">
    <div class="hero-content">
        <img src="__LOGO_B64__" class="hero-logo">
        <div class="hero-title">__LANDING_TITLE__</div>
        <div class="hero-subtitle">__LANDING_SUBTITLE__</div>
    </div>
</div>
"""
    cleaned_html = "\n".join(line.strip() for line in raw_html.splitlines())
    cleaned_html = cleaned_html.replace("__LANDING_TITLE__", i18n.t("landing.title"))
    cleaned_html = cleaned_html.replace("__LANDING_SUBTITLE__", i18n.t("landing.subtitle"))
    cleaned_html = cleaned_html.replace("__LOGO_B64__", LOGO_B64)
    
    st.markdown(cleaned_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button(i18n.t("landing.cta"), use_container_width=True, type="primary", key="get_started_btn"):
            sm.reset()
            st.switch_page(create_project_page)

def render_create_project():
    """Create Project page – delegates to the stage-based workflow."""
    render_top_navbar("Create Project")
    from pages._create_project import main
    main()


def render_dashboard():
    """Dashboard page."""
    render_top_navbar("Dashboard")
    from ui.workspace_views import render_dashboard as _dashboard, render_recent, render_shared

    _dashboard()
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        render_recent()
    with col2:
        render_shared()


def render_archive():
    """Archive page."""
    render_top_navbar("Archive")
    from ui.workspace_views import render_archive

    render_archive()

def render_top_navbar(active_page: str):
    """Renders a gorgeous, responsive, glassmorphic top navbar using Streamlit columns."""
    lang = i18n.get_lang()
    
    st.markdown("""
    <style>
    /* Prevent streamlit from padding the top too much now that we have a navbar */
    .block-container {
        padding-top: 0.5rem !important;
    }
    /* Hide top right Streamlit header completely */
    header { visibility: hidden; }
    /* Force top navigation buttons to never wrap text and be perfectly centered */
    div[data-testid="stColumn"] button {
        white-space: nowrap !important;
        word-break: keep-all !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
    }
    div[data-testid="stColumn"] button * {
        white-space: nowrap !important;
        word-break: keep-all !important;
        display: inline-flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        margin: 0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Dynamic Column layout: Logo & Beta badge, Home, Create Project, Dashboard, Archive, Deploy, Language Toggle
    # We do NOT reverse columns in python for RTL because Streamlit/browser flex layout
    # naturally reverses the visual order of columns when direction is RTL.
    col_widths = [1.8, 1, 1.5, 1.1, 1, 1.2, 1.1]
    cols = st.columns(col_widths)
    logo_col = cols[0]
    home_col = cols[1]
    create_col = cols[2]
    dash_col = cols[3]
    archive_col = cols[4]
    deploy_col = cols[5]
    lang_col = cols[6]
    
    
    with logo_col:
        logo_align = "right" if lang == "ar" else "left"
        logo_html = f"""
        <div style="display: flex; align-items: center; justify-content: {logo_align}; gap: 8px; margin-top: 5px; width: 100%;">
            <img src="{LOGO_B64}" style="height: 80px; object-fit: contain;">
        </div>
        """
        st.markdown(logo_html, unsafe_allow_html=True)
        
    with home_col:
        label = "الرئيسية" if lang == "ar" else "Home"
        if st.button(label, key="nav_home", use_container_width=True, type="primary" if active_page == "Home" else "secondary"):
            sm.reset()
            st.switch_page(pages[0])
            
    with create_col:
        label = "إنشاء مشروع" if lang == "ar" else "Create Project"
        if st.button(label, key="nav_create", use_container_width=True, type="primary" if active_page == "Create Project" else "secondary"):
            st.switch_page(create_project_page)
            
    with dash_col:
        label = "لوحة التحكم" if lang == "ar" else "Dashboard"
        if st.button(label, key="nav_dashboard", use_container_width=True, type="primary" if active_page == "Dashboard" else "secondary"):
            st.switch_page(pages[2])
            
    with archive_col:
        label = "الأرشيف" if lang == "ar" else "Archive"
        if st.button(label, key="nav_archive", use_container_width=True, type="primary" if active_page == "Archive" else "secondary"):
            st.switch_page(pages[3])

    with deploy_col:
        label = "الرفع أونلاين" if lang == "ar" else "Deploy HF"
        if st.button(label, key="nav_deploy", use_container_width=True, type="primary" if active_page == "Deploy" else "secondary"):
            st.switch_page(deploy_page)
            
    with lang_col:
        lang_label = "English" if lang == "ar" else "عربي"
        if st.button(lang_label, key="nav_lang_toggle", use_container_width=True, type="secondary"):
            new_lang = "en" if lang == "ar" else "ar"
            sm.set_ui_language(new_lang)
            st.rerun()
            
    st.markdown("<hr style='margin: 4px 0 8px 0; border-color: rgba(255, 255, 255, 0.08);'>", unsafe_allow_html=True)


create_project_page = st.Page(
    render_create_project,
    title="Create Project",
    icon="\U0001f4c4",
    url_path="create-project",
)

def render_deploy():
    """Renders the Hugging Face Space Deployer page."""
    render_top_navbar("Deploy")
    from pages._deploy_hf import render_deploy_page
    render_deploy_page()

deploy_page = st.Page(
    render_deploy,
    title="Deploy to HF",
    icon="🚀",
    url_path="deploy",
)

pages = [
    st.Page(render_landing, title="Home", icon="\U0001f3e0", default=True, url_path=""),
    create_project_page,
    st.Page(
        render_dashboard,
        title="Dashboard",
        icon="\U0001f4ca",
        url_path="dashboard",
    ),
    st.Page(
        render_archive,
        title="Archive",
        icon="\U0001f5c4\ufe0f",
        url_path="archive",
    ),
    deploy_page,
]

import os
# Passcode Gate for Hugging Face Spaces (Activated only when running online)
is_huggingface = os.getenv("SPACE_ID") is not None
if is_huggingface and not st.session_state.get("authenticated", False):
    from ui.passcode_gate import render_passcode_gate
    render_passcode_gate()
else:
    pg = st.navigation(pages, position="hidden")
    pg.run()
