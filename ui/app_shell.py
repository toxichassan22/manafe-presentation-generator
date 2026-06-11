"""App shell: unified navbar, workspace tabs, language toggle, and step progress."""

import streamlit as st

from config.branding import branding
from ui import i18n
from ui.design_tokens import STAGE_ORDER, inject_global_css
from utils import state_manager as sm


def render_app_shell(current_stage: str) -> None:
    inject_global_css(i18n.get_lang())
    if not st.session_state.get("show_chat"):
        steps_html = _build_step_bar_html(current_stage)
        st.markdown(steps_html, unsafe_allow_html=True)


def _render_language_toggle() -> None:
    lang = i18n.get_lang()
    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            i18n.t("lang.ar"),
            use_container_width=True,
            type="primary" if lang == "ar" else "secondary",
            key="lang_toggle_ar",
        ):
            if lang != "ar":
                sm.set_ui_language("ar")
                st.rerun()
    with c2:
        if st.button(
            i18n.t("lang.en"),
            use_container_width=True,
            type="primary" if lang == "en" else "secondary",
            key="lang_toggle_en",
        ):
            if lang != "en":
                sm.set_ui_language("en")
                st.rerun()


def _build_step_bar_html(current_stage: str) -> str:
    steps = [
        ("prompt", "step.prompt", 1),
        ("outline_review", "step.outline", 2),
        ("reference_image_setup", "step.reference", 3),
        ("generating", "step.generate", 4),
        ("preview", "step.preview", 5),
    ]
    stage_key = "preview" if current_stage in ("preview", "editing") else current_stage
    if stage_key == "settings":
        stage_key = "outline_review"

    current_idx = STAGE_ORDER.index(stage_key) if stage_key in STAGE_ORDER else 0

    parts = ['<div class="step-container">']
    for i, (sid, label_key, num) in enumerate(steps):
        sid_idx = STAGE_ORDER.index(sid)
        if sid_idx < current_idx:
            state = "done"
            dot_inner = "&#10003;"  # checkmark
        elif sid_idx == current_idx:
            state = "active"
            dot_inner = str(num)
        else:
            state = ""
            dot_inner = str(num)

        label = i18n.t(label_key)
        parts.append(
            f'<div class="step-item {state}">'
            f'<span class="step-dot">{dot_inner}</span>'
            f'<span style="font-size: 0.75rem; color: var(--color-text-secondary);">{label}</span></div>'
        )
        if i < len(steps) - 1:
            conn_done = "done" if sid_idx < current_idx else ""
            parts.append(f'<div class="step-connector {conn_done}"></div>')

    parts.append("</div>")
    return "".join(parts)
