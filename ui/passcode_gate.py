import os
import streamlit as st
from assets import LOGO_B64
from ui import i18n

def render_passcode_gate():
    """Renders a premium corporate passcode gate for online deployments."""
    lang = i18n.get_lang()
    
    # Clean full page overlay style matching corporate burgundy theme
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 500px !important;
            padding-top: 5rem !important;
            margin: 0 auto !important;
        }
        [data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div class="surface-card" style="text-align: center; padding: 3rem 2rem; border-radius: var(--radius-lg); border: 1px solid var(--color-border); box-shadow: var(--shadow-md); background: radial-gradient(circle at 50% 0%, rgba(103, 13, 12, 0.03) 0%, rgba(255, 255, 255, 0.98) 100%);">
            <img src="{LOGO_B64}" style="height: 100px; object-fit: contain; margin-bottom: 2rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05));">
            <h2 style="color: var(--color-primary); font-size: 1.6rem; font-weight: 800; margin: 0 0 0.5rem 0;">
                {"شركة منافع الاقتصادية للعقار" if lang == "ar" else "Manafe Economic Real Estate"}
            </h2>
            <div style="font-size: 0.95rem; color: var(--color-text-secondary); margin-bottom: 2rem; font-weight: 500;">
                {"🔐 بوابة الدخول الآمن للمنصة" if lang == "ar" else "🔐 Secure Platform Access Gate"}
            </div>
            <p style="color: var(--color-text-secondary); font-size: 0.88rem; line-height: 1.6; margin-bottom: 2rem;">
                {"هذا التطبيق محمي ومخصص لعملاء وشركاء منصة منافع الاقتصادية. يرجى إدخال رمز المرور المعتمد للدخول والتصفح." 
                if lang == "ar" else 
                "This application is protected and restricted to clients and partners of Manafe Economic Platform. Please enter the access passcode to proceed."}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Load target passcode from environment or use default 'manafe3'
    target_passcode = os.getenv("APP_PASSCODE", "manafe3").strip()

    with st.form("login_form", clear_on_submit=False):
        passcode = st.text_input(
            "🔑 رمز مرور المنصة (Access Passcode):" if lang == "ar" else "🔑 Access Passcode:",
            type="password",
            placeholder="••••••••"
        )
        
        st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
        
        submit = st.form_submit_button(
            "🚪 دخول المنصة" if lang == "ar" else "🚪 Enter Platform",
            use_container_width=True,
            type="primary"
        )
        
        if submit:
            if passcode.strip() == target_passcode:
                st.session_state["authenticated"] = True
                st.toast("تم تسجيل الدخول بنجاح!" if lang == "ar" else "Logged in successfully!")
                st.rerun()
            else:
                st.error(
                    "❌ رمز المرور غير صحيح! يرجى مراجعة إدارة شركة منافع." 
                    if lang == "ar" else 
                    "❌ Incorrect passcode! Please contact Manafe Platform administration."
                )
