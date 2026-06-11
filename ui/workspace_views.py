from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from ui import i18n
from utils import state_manager as sm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


def render_home() -> None:
    project_data = sm.get_project_data() or {}
    slides = sm.get_slides() or []
    files = _collect_output_items()
    project_name = _get_project_name(project_data)
    stage = _get_stage_label(sm.get_stage())
    
    with st.container(border=True):
        st.header(i18n.t("home.title"))
        st.write(i18n.t("home.subtitle"))
        st.info(i18n.t("home.pitch_desc"))

        col1, col2, col3 = st.columns(3)
        col1.metric(i18n.t("home.slides"), str(len(slides) or project_data.get("num_slides", 0) or 0))
        col2.metric(i18n.t("home.files"), str(len(files)))
        col3.metric(i18n.t("home.stage"), stage)

    with st.container(border=True):
        st.subheader(i18n.t("home.snapshot_title"))
        st.write(project_name)
        st.write(i18n.t("home.snapshot_desc"))

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(i18n.t("home.open_process"), key="home_open_process", use_container_width=True, type="primary"):
                sm.set_workspace_tab("project_process")
                st.rerun()
        with col2:
            if st.button(i18n.t("home.open_preview"), key="home_open_preview", use_container_width=True, disabled=not slides):
                sm.set_workspace_tab("project_process")
                if slides:
                    sm.set_stage("preview")
                st.rerun()
        with col3:
            if st.button(i18n.t("home.new_project"), key="home_new_project", use_container_width=True):
                sm.reset()
                sm.set_workspace_tab("project_process")
                st.rerun()

    st.markdown(_build_home_features_html(), unsafe_allow_html=True)
    st.markdown(_build_home_journey_html(), unsafe_allow_html=True)

    left, right = st.columns([6, 5])
    with left:
        _render_info_card(
            i18n.t("home.quick_actions"),
            i18n.t("home.quick_desc"),
            [
                (i18n.t("nav.process"), stage),
                (i18n.t("dashboard.title"), f"{len(slides)} {i18n.t('home.slides').lower()}"),
                (i18n.t("nav.archive"), str(len(files))),
            ],
        )
    with right:
        _render_recent_outputs_panel(files[:4])


def render_dashboard() -> None:
    project_data = sm.get_project_data() or {}
    slides = sm.get_slides() or []
    images = sm.get_images() or {}
    files = _collect_output_items()
    
    with st.container(border=True):
        st.subheader(i18n.t("dashboard.title"))
        st.write(i18n.t("dashboard.subtitle"))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(i18n.t("dashboard.metric_project"), _get_project_name(project_data))
        c2.metric(i18n.t("dashboard.metric_stage"), sm.get_stage().replace("_", " ").title())
        c3.metric(i18n.t("dashboard.metric_slides"), str(len(slides)))
        c4.metric(i18n.t("dashboard.metric_assets"), str(len(images) + len(files)))

    if not project_data and not slides:
        st.info(i18n.t("dashboard.no_data"))
        return

    _render_output_table(files[:6])


def render_recent() -> None:
    with st.container(border=True):
        st.subheader(i18n.t("recent.title"))
        st.write(i18n.t("recent.subtitle"))
        _render_output_table(_collect_output_items()[:8])


def render_archive() -> None:
    with st.container(border=True):
        st.subheader(i18n.t("archive.title"))
        st.write(i18n.t("archive.subtitle"))
        _render_output_table(_collect_output_items(include_all=True))


def render_shared() -> None:
    pptx_path = sm.get_pptx_path()
    pdf_path = sm.get_pdf_path()

    with st.container(border=True):
        st.subheader(i18n.t("shared.title"))
        st.write(i18n.t("shared.subtitle"))

        paths = [p for p in [pptx_path, pdf_path] if p]
        if not paths:
            st.info(i18n.t("workspace.empty"))
            return

        for raw_path in paths:
            path = Path(raw_path)
            if not path.exists():
                continue
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{path.name}**")
                st.caption(f"{i18n.t('workspace.status_ready')} · {_format_dt(path.stat().st_mtime)}")
            with col2:
                with open(path, "rb") as fh:
                    st.download_button(
                        label=i18n.t("preview.download"),
                        data=fh.read(),
                        file_name=path.name,
                        mime=_guess_mime(path),
                        key=f"shared_download_{path.name}",
                        use_container_width=True,
                    )


def _render_info_card(title: str, desc: str, items: list[tuple[str, str]]) -> None:
    rows_html = ""
    for label, value in items:
        rows_html += f"""
        <div class="wv-info-row">
            <span class="wv-info-label">{label}</span>
            <span class="wv-info-value">{value}</span>
        </div>"""

    html = f"""
    <style>
    .wv-info-card {{
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-inline-start: 3px solid transparent;
        border-image: linear-gradient(180deg, var(--color-primary), var(--color-secondary)) 1;
        border-image-slice: 0 0 0 1;
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        margin-bottom: var(--space-4);
        animation: fadeInUp 0.5s ease both;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .wv-info-card:hover {{
        border-color: var(--color-primary);
        box-shadow: 0 8px 30px rgba(var(--color-primary-rgb), 0.12);
        transform: translateY(-2px);
    }}
    .wv-info-card-title {{
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--color-text-primary);
        margin: 0 0 4px 0;
        text-align: start;
    }}
    .wv-info-card-desc {{
        font-size: 0.85rem;
        color: var(--color-text-tertiary);
        margin: 0 0 var(--space-4) 0;
        text-align: start;
    }}
    .wv-info-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--space-3) var(--space-4);
        margin-bottom: var(--space-2);
        background: var(--color-surface-raised);
        border-radius: var(--radius-sm);
        border: 1px solid var(--color-border);
        transition: all 0.2s ease;
    }}
    .wv-info-row:hover {{
        border-color: var(--color-border-strong);
        background: rgba(var(--color-primary-rgb), 0.05);
    }}
    .wv-info-label {{
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--color-text-secondary);
        text-align: start;
    }}
    .wv-info-value {{
        font-size: 0.875rem;
        font-weight: 700;
        color: var(--color-primary);
        text-align: end;
    }}
    </style>
    <div class="wv-info-card">
        <div class="wv-info-card-title">{title}</div>
        <div class="wv-info-card-desc">{desc}</div>
        {rows_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def _build_home_features_html() -> str:
    svg_sparkle = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.912 5.813a2 2 0 0 0 1.275 1.275L21 12l-5.813 1.912a2 2 0 0 0-1.275 1.275L12 21l-1.912-5.813a2 2 0 0 0-1.275-1.275L3 12l5.813-1.912a2 2 0 0 0 1.275-1.275L12 3z"/></svg>'
    svg_palette = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></svg>'
    svg_download = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'

    features = [
        (svg_sparkle, i18n.t("home.feature_ai_title"), i18n.t("home.feature_ai_desc")),
        (svg_palette, i18n.t("home.feature_brand_title"), i18n.t("home.feature_brand_desc")),
        (svg_download, i18n.t("home.feature_export_title"), i18n.t("home.feature_export_desc")),
    ]

    cards_html = ""
    for idx, (icon_svg, title, desc) in enumerate(features):
        delay = idx * 0.12
        cards_html += f"""
        <div class="wv-feat-card" style="animation-delay: {delay}s;">
            <div class="wv-feat-icon">{icon_svg}</div>
            <div class="wv-feat-title">{title}</div>
            <div class="wv-feat-desc">{desc}</div>
        </div>"""

    return f"""
    <style>
    .wv-feat-grid {{
        display: flex;
        gap: var(--space-4);
        margin-bottom: var(--space-4);
    }}
    .wv-feat-card {{
        flex: 1;
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        text-align: start;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.5s ease both;
        position: relative;
        overflow: hidden;
    }}
    .wv-feat-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    .wv-feat-card:hover {{
        transform: translateY(-4px);
        border-color: var(--color-primary);
        box-shadow: 0 12px 36px rgba(var(--color-primary-rgb), 0.15), 0 0 0 1px rgba(var(--color-primary-rgb), 0.1);
    }}
    .wv-feat-card:hover::before {{ opacity: 1; }}
    .wv-feat-icon {{
        width: 52px;
        height: 52px;
        border-radius: var(--radius-md);
        background: linear-gradient(135deg, rgba(var(--color-primary-rgb), 0.15), rgba(var(--color-primary-rgb), 0.05));
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--color-primary);
        margin-bottom: var(--space-4);
        transition: all 0.3s ease;
    }}
    .wv-feat-card:hover .wv-feat-icon {{
        background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
        color: #FFFFFF;
        box-shadow: 0 4px 16px rgba(var(--color-primary-rgb), 0.35);
    }}
    .wv-feat-title {{
        font-size: 1rem;
        font-weight: 700;
        color: var(--color-text-primary);
        margin-bottom: var(--space-2);
    }}
    .wv-feat-desc {{
        font-size: 0.85rem;
        color: var(--color-text-tertiary);
        line-height: 1.6;
    }}
    @media (max-width: 768px) {{
        .wv-feat-grid {{ flex-direction: column; }}
    }}
    </style>
    <div class="wv-feat-grid">
        {cards_html}
    </div>
    """


def _build_home_journey_html() -> str:
    steps = [
        ("01", i18n.t("step.prompt"), i18n.t("home.step_project_desc")),
        ("02", i18n.t("step.outline"), i18n.t("home.step_outline_desc")),
        ("03", i18n.t("step.generate"), i18n.t("home.step_generate_desc")),
        ("04", i18n.t("step.preview"), i18n.t("home.step_preview_desc")),
    ]

    steps_html = ""
    for idx, (index, title, desc) in enumerate(steps):
        delay = 0.1 + idx * 0.1
        connector = ""
        if idx < len(steps) - 1:
            connector = '<div class="wv-tl-connector"><div class="wv-tl-connector-fill"></div></div>'
        steps_html += f"""
        <div class="wv-tl-step" style="animation-delay: {delay}s;">
            <div class="wv-tl-marker">
                <div class="wv-tl-number">{index}</div>
                {connector}
            </div>
            <div class="wv-tl-content">
                <div class="wv-tl-title">{title}</div>
                <div class="wv-tl-desc">{desc}</div>
            </div>
        </div>"""

    journey_title = i18n.t("home.journey_title")
    journey_desc = i18n.t("home.journey_desc")

    return f"""
    <style>
    .wv-journey-card {{
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: var(--space-6) var(--space-5);
        margin-bottom: var(--space-4);
        animation: fadeInUp 0.5s ease both;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .wv-journey-card:hover {{
        border-color: var(--color-primary);
        box-shadow: 0 8px 30px rgba(var(--color-primary-rgb), 0.10);
    }}
    .wv-journey-header {{
        margin-bottom: var(--space-5);
        text-align: start;
    }}
    .wv-journey-title {{
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--color-text-primary);
        margin: 0 0 4px 0;
    }}
    .wv-journey-subtitle {{
        font-size: 0.85rem;
        color: var(--color-text-tertiary);
        margin: 0;
    }}
    .wv-tl-steps {{
        display: flex;
        flex-direction: column;
        gap: 0;
    }}
    .wv-tl-step {{
        display: flex;
        gap: var(--space-4);
        animation: fadeInUp 0.45s ease both;
    }}
    .wv-tl-marker {{
        display: flex;
        flex-direction: column;
        align-items: center;
        flex-shrink: 0;
    }}
    .wv-tl-number {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, rgba(var(--color-primary-rgb), 0.18), rgba(var(--color-primary-rgb), 0.06));
        border: 2px solid rgba(var(--color-primary-rgb), 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 800;
        color: var(--color-primary);
        flex-shrink: 0;
        transition: all 0.3s ease;
    }}
    .wv-tl-step:hover .wv-tl-number {{
        background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
        color: #FFFFFF;
        border-color: var(--color-primary);
        box-shadow: 0 0 0 4px rgba(var(--color-primary-rgb), 0.15), 0 4px 12px rgba(var(--color-primary-rgb), 0.25);
    }}
    .wv-tl-connector {{
        width: 2px;
        height: 28px;
        background: var(--color-border);
        position: relative;
        overflow: hidden;
        border-radius: 1px;
    }}
    .wv-tl-connector-fill {{
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: linear-gradient(180deg, var(--color-primary), var(--color-secondary));
        opacity: 0.45;
    }}
    .wv-tl-content {{
        padding-bottom: var(--space-5);
        text-align: start;
    }}
    .wv-tl-title {{
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--color-text-primary);
        margin-bottom: 2px;
    }}
    .wv-tl-desc {{
        font-size: 0.825rem;
        color: var(--color-text-tertiary);
        line-height: 1.55;
    }}
    @media (max-width: 768px) {{
        .wv-tl-number {{ width: 32px; height: 32px; font-size: 0.7rem; }}
    }}
    </style>
    <div class="wv-journey-card">
        <div class="wv-journey-header">
            <div class="wv-journey-title">{journey_title}</div>
            <p class="wv-journey-subtitle">{journey_desc}</p>
        </div>
        <div class="wv-tl-steps">
            {steps_html}
        </div>
    </div>
    """


def _render_recent_outputs_panel(items: list[dict]) -> None:
    with st.container(border=True):
        st.subheader(i18n.t("home.recent_outputs"))
        st.write(i18n.t("home.recent_outputs_desc"))
        if not items:
            st.info(i18n.t("home.empty_outputs"))
        else:
            for item in items:
                st.write(f"**{item['name']}**")
                st.caption(f"{item['suffix']} · {i18n.t('workspace.modified')}: {item['modified']}")


def _render_output_table(items: list[dict]) -> None:
    if not items:
        st.info(i18n.t("workspace.empty"))
        if st.button(i18n.t("workspace.goto_process"), key="workspace_go_process", type="primary"):
            sm.set_workspace_tab("project_process")
            st.rerun()
        return

    svg_pptx = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/><path d="M7 8h2m2 0h2m2 0h2"/><path d="M7 12h10"/></svg>'
    svg_pdf = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>'

    file_label = i18n.t('workspace.file')
    mod_label = i18n.t('workspace.modified')

    for item in items:
        icon = svg_pptx if item['suffix'] == 'PPTX' else svg_pdf
        badge_color = 'var(--color-primary)' if item['suffix'] == 'PPTX' else 'var(--color-accent)'

        card_html = f"""
        <style>
        .wv-file-card {{
            display: flex;
            align-items: center;
            gap: var(--space-4);
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            padding: var(--space-3) var(--space-4);
            margin-bottom: var(--space-2);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInUp 0.4s ease both;
        }}
        .wv-file-card:hover {{
            border-color: var(--color-border-strong);
            background: var(--color-surface-raised);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
        }}
        .wv-file-icon {{
            width: 42px;
            height: 42px;
            border-radius: var(--radius-sm);
            background: var(--color-surface-raised);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--color-text-tertiary);
            flex-shrink: 0;
            border: 1px solid var(--color-border);
            transition: all 0.25s ease;
        }}
        .wv-file-card:hover .wv-file-icon {{
            color: var(--color-primary);
            border-color: rgba(var(--color-primary-rgb), 0.3);
            background: rgba(var(--color-primary-rgb), 0.08);
        }}
        .wv-file-info {{
            flex: 1;
            min-width: 0;
            text-align: start;
        }}
        .wv-file-name {{
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--color-text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .wv-file-meta {{
            font-size: 0.75rem;
            color: var(--color-text-tertiary);
            margin-top: 2px;
            display: flex;
            align-items: center;
            gap: var(--space-2);
            flex-wrap: wrap;
        }}
        .wv-file-badge {{
            display: inline-block;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            padding: 1px 8px;
            border-radius: var(--radius-full);
            border: 1px solid;
        }}
        </style>
        <div class="wv-file-card">
            <div class="wv-file-icon">{icon}</div>
            <div class="wv-file-info">
                <div class="wv-file-name">{item['name']}</div>
                <div class="wv-file-meta">
                    <span class="wv-file-badge" style="color: {badge_color}; border-color: {badge_color}; background: color-mix(in srgb, {badge_color} 10%, transparent);">{item['suffix']}</span>
                    <span>{mod_label}: {item['modified']}</span>
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)


def _collect_output_items(include_all: bool = False) -> list[dict]:
    if not OUTPUTS_DIR.exists():
        return []

    patterns = ("*.pptx", "*.pdf") if include_all else ("*.pptx", "*.pdf")
    items = []
    for pattern in patterns:
        for path in OUTPUTS_DIR.glob(pattern):
            try:
                stat = path.stat()
                items.append(
                    {
                        "name": path.name,
                        "suffix": path.suffix.lstrip(".").upper(),
                        "modified": _format_dt(stat.st_mtime),
                        "mtime": stat.st_mtime,
                    }
                )
            except OSError:
                continue
    return sorted(items, key=lambda item: item["mtime"], reverse=True)


def _get_project_name(project_data: dict) -> str:
    if not project_data:
        return i18n.t("home.no_project")
    return (
        project_data.get("project_name")
        or project_data.get("description", "")[:60]
        or i18n.t("home.no_project")
    )


def _get_stage_label(stage_key: str) -> str:
    mapping = {
        "prompt": i18n.t("step.prompt"),
        "outline_review": i18n.t("step.outline"),
        "settings": i18n.t("step.outline"),
        "generating": i18n.t("step.generate"),
        "preview": i18n.t("step.preview"),
        "editing": i18n.t("step.preview"),
    }
    return mapping.get(stage_key, stage_key.replace("_", " ").title())


def _format_dt(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


def _metric_html(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        "</div>"
    )


def _guess_mime(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return "application/pdf"
    return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
