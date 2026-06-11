"""
Preview UI – light SaaS slide editor with inline editing and download.
"""

import base64
from pathlib import Path

import streamlit as st

from ui import i18n
from utils import state_manager as sm
from ui.components import render_slide_editor


def render_preview():
    slides = sm.get_slides()
    images = sm.get_images() or {}
    pptx_path = sm.get_pptx_path()
    project_data = sm.get_project_data() or {}
    project_name = project_data.get(
        "project_name",
        project_data.get("description", i18n.t("prompt.project_name_ph"))[:50],
    )

    if not slides:
        st.warning(i18n.t("preview.no_slides"))
        return

    st.markdown(
        """
        <style>
        .preview-stage .block-container { max-width: 100% !important; padding-top: 0 !important; }
        </style>
        <div class="preview-stage"></div>
        """,
        unsafe_allow_html=True,
    )

    pptx_b64 = ""
    pptx_filename = ""
    if pptx_path:
        pptx_path_obj = Path(pptx_path)
        if pptx_path_obj.exists():
            try:
                pptx_b64 = base64.b64encode(pptx_path_obj.read_bytes()).decode("utf-8")
                pptx_filename = pptx_path_obj.name
            except Exception as e:
                st.error(f"Error reading presentation file: {e}")

    slides_for_component = _prepare_slides_data(slides, images)

    result = render_slide_editor(
        slides=slides_for_component,
        project_name=project_name,
        lang=i18n.get_lang(),
        key=f"slide_editor_{i18n.get_lang()}",
        pptx_b64=pptx_b64,
        pptx_filename=pptx_filename,
    )

    if result is not None:
        action = result.get("action")

        if action == "save_slides":
            updated = result.get("slides")
            if updated:
                try:
                    sm.set_slides(updated)
                    # Rebuild the .pptx file dynamically on text save
                    slide_contents = sm.get_slides()
                    slide_images = sm.get_images() or {}
                    project_data = sm.get_project_data() or {}
                    theme = sm.get("theme")
                    from generators.pptx_builder import build_presentation
                    new_pptx_path = build_presentation(
                        slide_contents,
                        slide_images,
                        project_data.get("project_name", "proposal"),
                        theme=theme,
                    )
                    sm.set_pptx_path(new_pptx_path)
                    st.toast(i18n.t("toast.saved"))
                    st.rerun()
                except Exception as e:
                    st.error(f"{i18n.t('error.save')}: {e}")
        elif action == "download":
            _trigger_download(pptx_path)
        elif action == "new":
            sm.reset()
            st.rerun()
        elif action in ("theme", "share", "present", "add_slide", "add_content", "layout"):
            st.toast(f"🔧 {action} - قريباً!", icon="⚙️")
        elif action == "regen":
            slide_idx = result.get("slide_index", 0)
            _regenerate_text(slide_idx)


def _prepare_slides_data(slides, images):
    prepared = []
    for idx, slide in enumerate(slides):
        s = dict(slide)
        if idx in images and images[idx]:
            try:
                s["image_b64"] = base64.b64encode(images[idx]).decode("utf-8")
            except Exception:
                s["image_b64"] = None
        else:
            s["image_b64"] = None
        prepared.append(s)
    return prepared


def _trigger_download(pptx_path):
    if pptx_path:
        pptx_path = Path(pptx_path)
        if pptx_path.exists():
            try:
                bytes_data = pptx_path.read_bytes()
                b64 = base64.b64encode(bytes_data).decode("utf-8")
                filename = pptx_path.name
                
                # Dynamic HTML component that creates and clicks a virtual link programmatically
                js_downloader = f"""
                <script>
                (function() {{
                    try {{
                        const b64 = "{b64}";
                        const filename = "{filename}";
                        const byteCharacters = atob(b64);
                        const byteNumbers = new Array(byteCharacters.length);
                        for (let i = 0; i < byteCharacters.length; i++) {{
                            byteNumbers[i] = byteCharacters.charCodeAt(i);
                        }}
                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], {{ type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' }});
                        const url = URL.createObjectURL(blob);
                        
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }} catch (err) {{
                        console.error("Auto download failed:", err);
                    }}
                }})();
                </script>
                """
                import streamlit.components.v1 as components
                components.html(js_downloader, height=0, width=0)
                st.toast(i18n.t("toast.download_started") or "جاري بدء التحميل...")
            except Exception as e:
                st.error(f"Error executing download: {e}")


def _regenerate_text(idx):
    project_data = sm.get_project_data()
    if not project_data:
        return
    try:
        from generators.content_generator import regenerate_slide
        land_analysis = sm.get_land_analysis() or {}
        new_slide = regenerate_slide(idx, project_data, land_analysis, sm.get_slides())
        sm.update_slide(idx, new_slide)
        sm.set_slides(sm.get_slides())
        st.rerun()
    except Exception:
        st.error(i18n.t("error.regen"))
