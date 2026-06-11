
"""Create Project page – stage-based proposal workflow."""
import base64
import html
import os
from pathlib import Path
import re

import streamlit as st

from ui import i18n
from utils import state_manager as sm
from ui.app_shell import render_app_shell


def _handle_generation_stage():
    project_data = sm.get_project_data()
    if not project_data:
        sm.set_stage("prompt")
        st.rerun()
        return

    # Check if slides are already generated to bypass running the generation on rerun
    outline = sm.get("outline")
    total_slides = len(outline) if outline else 0
    slides = sm.get_slides()
    pptx_path = sm.get_pptx_path()
    if slides and len(slides) == total_slides and pptx_path and Path(pptx_path).exists():
        st.session_state["_generation_running"] = False
        st.success(i18n.t("gen.done_title"))
        slide_images = sm.get_images() or {}
        st.write(i18n.t("gen.done_sub", slides=total_slides, images=len(slide_images)))

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(i18n.t("gen.preview_cta"), use_container_width=True, type="primary"):
                sm.set_stage("preview")
                st.rerun()
            with open(pptx_path, "rb") as f:
                st.download_button(
                    i18n.t("gen.download"),
                    data=f.read(),
                    file_name=Path(pptx_path).name,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True,
                )
        return

    st.warning(i18n.t("gen.warning_refresh"))

    st.session_state["_generation_running"] = True

    project_name = project_data.get("project_name", i18n.t("prompt.project_name_ph"))
    
    # Project-level commercial detection to keep building styling consistent across all slides
    is_commercial_project = False
    for val in project_data.values():
        if isinstance(val, str) and any(kw in val.lower() for kw in [
            "تجاري", "إداري", "إداريه", "تجاريه", "مكتب", "برج", "عمارة", "مجمع", "مكاتب", "أبراج",
            "commercial", "office", "administrative", "tower", "complex", "building"
        ]):
            is_commercial_project = True
            break

    outline = sm.get("outline")
    if not outline:
        st.error(i18n.t("gen.no_outline"))
        st.session_state["_generation_running"] = False
        st.stop()

    import logging
    logger = logging.getLogger(__name__)

    total_slides = len(outline)

    # 1. Render title block first so it is at the top
    st.markdown(
        f'<div class="surface-card" style="margin-bottom: 2rem;">'
        f'<h2 style="margin:0 0 0.5rem 0;">{i18n.t("gen.title")}: {project_name}</h2>'
        f'<div style="color: var(--color-primary); font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">'
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--color-success);animation:pulse 2s infinite;"></span>'
        f'{i18n.t("gen.live")}</div></div>',
        unsafe_allow_html=True,
    )

    # 2. Render progress bar and phase chips placeholder
    progress_bar = st.progress(0)
    phase_placeholder = st.empty()
    
    # 3. Pre-allocate dynamic placeholders for slides below the title
    slide_placeholders = [st.empty() for _ in range(total_slides)]

    def _render_phase_chips(active_phase: str):
        phases = [
            ("writing", "gen.phase_writing"),
            ("imaging", "gen.phase_imaging"),
            ("building", "gen.phase_building"),
        ]
        order = ["writing", "imaging", "building"]
        active_idx = order.index(active_phase) if active_phase in order else 0
        chips_html = ['<div style="display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap;">']
        for i, (pid, key) in enumerate(phases):
            if i < active_idx:
                bg = "rgba(16, 185, 129, 0.1)"
                color = "var(--color-success)"
                label = f"&#10003; {i18n.t(key)}"
            elif i == active_idx:
                bg = "var(--color-primary-dim)"
                color = "var(--color-primary)"
                label = f"&bull; {i18n.t(key)}"
            else:
                bg = "var(--color-surface-raised)"
                color = "var(--color-text-tertiary)"
                label = f"{i18n.t(key)}"
            chips_html.append(
                f'<div style="padding: 0.5rem 1rem; border-radius: 999px; background: {bg}; color: {color}; font-weight: 600; font-size: 0.875rem;">{label}</div>'
            )
        chips_html.append('</div>')
        phase_placeholder.markdown("".join(chips_html), unsafe_allow_html=True)

    def _render_slide_html(idx, slide_type, title, body, image_b64=None):
        if image_b64:
            img_html = f'<div style="flex: 1; min-width: 200px; border-radius: var(--radius-sm); overflow: hidden;"><img src="data:image/png;base64,{image_b64}" style="width: 100%; height: auto; object-fit: cover;"></div>'
        else:
            img_html = '<div style="flex: 1; min-width: 200px; border-radius: var(--radius-sm); background: var(--color-surface-raised); display: flex; align-items: center; justify-content: center; color: var(--color-text-tertiary); font-size: 0.875rem; padding: 2rem;">No image</div>'
        body_html = body.replace("\\n", "<br>")
        return f"""
        <div class="surface-card" style="display: flex; gap: 1.5rem; flex-wrap: wrap; align-items: flex-start;">
            {img_html}
            <div style="flex: 2; min-width: 300px;">
                <div style="font-size: 0.875rem; color: var(--color-primary); font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">Slide {idx + 1} &bull; {slide_type.title()}</div>
                <h3 style="margin-top: 0; margin-bottom: 1rem; color: var(--color-text-primary);">{title}</h3>
                <div style="color: var(--color-text-secondary); font-size: 0.95rem; line-height: 1.6;">{body_html}</div>
            </div>
        </div>
        """

    def _extract_readable(data_or_text):
        if isinstance(data_or_text, dict):
            parts = []
            title = data_or_text.get("title", "")
            for key in ["description", "subtitle", "vision", "mission", "concept", "message", "summary", "cta"]:
                if key in data_or_text:
                    parts.append(str(data_or_text[key]))
            for key in ["bullets", "highlights", "key_features", "features", "materials", "strengths"]:
                if key in data_or_text and isinstance(data_or_text[key], list):
                    for item in data_or_text[key][:5]:
                        parts.append(f"&bull; {item}" if isinstance(item, str) else f"&bull; {item}")
            return title, "\\n".join(parts) if parts else ""
        if isinstance(data_or_text, str):
            clean = data_or_text.replace("```json", "").replace("```", "").strip()
            return "", clean
        return "", ""

    # Load previously generated slides to allow resuming seamlessly
    slide_contents = sm.get("slide_contents") or []
    if not isinstance(slide_contents, list) or len(slide_contents) > total_slides:
        slide_contents = []

    # 4. Initialize all placeholders with current state or waiting card IMMEDIATELY
    for idx, slide_spec in enumerate(outline):
        topic = slide_spec.get("topic", f"{i18n.t('gen.slide_n')} {idx + 1}")
        slide_type = slide_spec.get("slide_type", "standard")
        
        if idx < len(slide_contents):
            title, body = _extract_readable(slide_contents[idx])
            slide_placeholders[idx].markdown(
                _render_slide_html(idx, slide_type, title or topic, body),
                unsafe_allow_html=True,
            )
        else:
            slide_placeholders[idx].markdown(
                _render_slide_html(idx, slide_type, topic, "<i>جاري الانتظار لبدء توليد المحتوى...</i>"),
                unsafe_allow_html=True,
            )

    from services.llm_service import generate_json
    from prompts.content_prompts import generate_slide_content_prompt

    density = sm.get("density")
    theme = sm.get("theme")
    image_settings = sm.get("image_settings")
    docs_text = sm.get("docs_text")

    context_data = dict(project_data)
    if docs_text:
        context_data["docs_text"] = docs_text
    context_data["density_preference"] = density
    context_data["structured_project_data"] = sm.get_val("structured_project_data")
    
    # ── Initialize Image Generation Settings ──
    project_image_key = None
    project_seed = 0
    project_reference_image = None
    style_signature = ""
    fallback_style_text = ""
    ref_images_b64 = []
    
    if image_settings and image_settings.get("generate_images"):
        import hashlib
        from services.image_gen_service import (
            generate_image,
            get_project_image_key,
            get_project_reference_image,
            get_project_slide_image,
            set_project_reference_image,
            set_project_slide_image,
        )

        project_image_key = get_project_image_key(project_data)
        project_seed = int(hashlib.sha256(project_image_key.encode("utf-8")).hexdigest()[:8], 16) % 1000000000
        project_reference_image = get_project_reference_image(project_image_key)

        # Collect user-uploaded reference images
        docs_imgs = sm.get_val("docs_images") or []
        for d_img in docs_imgs:
            if isinstance(d_img, dict) and "base64" in d_img:
                ref_images_b64.append(d_img["base64"])
                
        prompts_cfg = image_settings.get("prompts", {})
        for heading, img_list in prompts_cfg.items():
            if isinstance(img_list, list):
                for img_item in img_list:
                    if isinstance(img_item, dict) and img_item.get("references_b64"):
                        ref_images_b64.extend(img_item["references_b64"])

        # Set first reference image as project reference ONLY if we don't already have one approved/set
        if ref_images_b64 and not project_reference_image:
            try:
                first_ref_bytes = base64.b64decode(ref_images_b64[0])
                set_project_reference_image(project_image_key, first_ref_bytes)
                project_reference_image = get_project_reference_image(project_image_key)
                logger.info("Project master reference image set from user-uploaded style reference.")
            except Exception as ref_err:
                logger.error("Failed to set project reference image from user upload: %s", ref_err)

        from services.gemini_service import extract_style_signature, generate_consistent_image_prompt
        
        fallback_style_text = (
            f"Project: {project_data.get('project_name')}\n"
            f"Description: {project_data.get('description')}\n"
            f"Floor Details: {project_data.get('floor_distribution')}\n"
            f"Visual Style: {project_data.get('image_style_description', '')}"
        )
        style_signature = sm.get_val("style_signature") or ""
        logger.info("Visual Style Signature configured for generation.")

    _render_phase_chips("writing")
    
    clarifications = sm.get("clarifications") or {}
    slide_images = {}
    
    if project_image_key:
        for idx in range(total_slides):
            img_data = get_project_slide_image(project_image_key, idx)
            if img_data:
                slide_images[idx] = img_data

    style_signature_cached = sm.get_val("style_signature") or ""

    # ══════════════════════════════════════════════════════════════════════
    # Phase 1: Generate ALL slide text sequentially (DeepSeek) — main thread
    # ══════════════════════════════════════════════════════════════════════
    for idx, slide_spec in enumerate(outline):
        topic = slide_spec.get("topic", f"{i18n.t('gen.slide_n')} {idx + 1}")
        slide_type = slide_spec.get("slide_type", "standard")

        # ── Check or Generate Slide Text ──
        if idx < len(slide_contents):
            content = slide_contents[idx]
            title, body = _extract_readable(content)
            slide_placeholders[idx].markdown(
                _render_slide_html(idx, slide_type, title or topic, body),
                unsafe_allow_html=True,
            )
        else:
            slide_placeholders[idx].markdown(
                _render_slide_html(idx, slide_type, topic, "<i>جاري توليد وصياغة المحتوى العقاري...</i>"),
                unsafe_allow_html=True,
            )

            def make_stream_cb(s_idx, s_type, s_topic):
                def cb(raw_text):
                    if '"needs_clarification"' in raw_text:
                        return
                    title_match = re.search(r'"title"\s*:\s*"([^"]+)"', raw_text)
                    stream_title = title_match.group(1) if title_match else s_topic
                    all_values = re.findall(
                        r'"(?:description|subtitle|vision|mission|concept|message|summary)"\s*:\s*"([^"]+)"',
                        raw_text,
                    )
                    bullets = re.findall(
                        r'"(?:bullets|highlights|key_features|features|materials|strengths|amenities)"\s*:\s*\[([^\]]*)\]',
                        raw_text,
                    )
                    bullet_items = []
                    if bullets:
                        bullet_items = re.findall(r'"([^"]+)"', bullets[0])
                    body_parts = list(all_values) + [f"&bull; {b}" for b in bullet_items[:6]]
                    display = "\\n".join(body_parts)
                    slide_placeholders[s_idx].markdown(
                        _render_slide_html(s_idx, s_type, stream_title, display),
                        unsafe_allow_html=True,
                    )
                return cb

            modified_slide_spec = dict(slide_spec)
            if idx in clarifications:
                modified_slide_spec["user_clarification"] = clarifications[idx]

            sys_sp, usr_sp = generate_slide_content_prompt(modified_slide_spec, context_data)
            try:
                content = generate_json(sys_sp, usr_sp, stream_callback=make_stream_cb(idx, slide_type, topic), images=None)
            except Exception as e:
                content = {"title": topic, "description": str(e)}

            content["slide_type"] = slide_type
            content["slide_index"] = idx

            if content.get("needs_clarification") == True:
                q_text = content.get("clarification_question", "الرجاء توضيح بعض التفاصيل لهذه الشريحة.")
                progress_bar.progress(int((idx / total_slides) * 50))
                st.session_state["_generation_running"] = False
                
                clarification_html = f"""
                <div style="padding: 1.5rem; background: rgba(245, 158, 11, 0.05); border: 2px solid #F59E0B; border-radius: var(--radius-sm); margin-top: 1rem; margin-bottom: 1rem;">
                    <div style="display:flex; align-items:center; gap: 0.5rem; color: #D97706; font-weight: bold; margin-bottom: 0.75rem;">
                        <span style="font-size: 1.25rem;">🔔</span>
                        <span>استفسار فني من منصة منافع</span>
                    </div>
                    <div style="color: var(--color-text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1rem; font-weight: 500;">
                        {q_text}
                    </div>
                </div>
                """
                slide_placeholders[idx].markdown(clarification_html, unsafe_allow_html=True)
                
                st.write("")
                user_ans = st.text_area(
                    "توضيحك أو الإجابة على السؤال:", 
                    key=f"ans_{idx}",
                    placeholder="اكتب هنا التفاصيل الإضافية التي تريد من منصة منافع استخدامها لصياغة هذه الشريحة بدقة..."
                )
                
                col1, col2 = st.columns([1, 4])
                submitted = False
                with col1:
                    if st.button("تحديث ومتابعة 🚀", key=f"btn_ans_{idx}", type="primary"):
                        submitted = True
                
                if submitted:
                    if user_ans.strip():
                        clarifications[idx] = user_ans.strip()
                        sm.set_val("clarifications", clarifications)
                        st.session_state["_generation_running"] = True
                        st.rerun()
                    else:
                        st.error("الرجاء كتابة إجابة ليتمكن النظام من المتابعة.")
                st.stop()

            # Determine if image is required based directly on DeepSeek/User outline spec,
            # with the Cover slide always enabled as a basic requirement.
            requires_img = slide_spec.get("requires_image", False)
            if slide_type == "cover":
                requires_img = True
                
            # If the user configured custom prompts in settings_stage, strictly respect that selection.
            custom_prompts = (image_settings or {}).get("prompts", {}) if image_settings else {}
            if custom_prompts:
                slide_title_clean = (content.get("title") or topic or "").strip()
                if slide_type != "cover":
                    requires_img = slide_title_clean in custom_prompts
                
            content["requires_image"] = requires_img
            content["image_prompt"] = slide_spec.get("image_prompt", "")
            slide_contents.append(content)
            sm.set_slides(slide_contents)

            title, body = _extract_readable(content)
            slide_placeholders[idx].markdown(
                _render_slide_html(idx, slide_type, title or topic, body),
                unsafe_allow_html=True,
            )

        progress_bar.progress(int(((idx + 1) / total_slides) * 50))

    # ══════════════════════════════════════════════════════════════════════
    # Phase 2: Generate ALL images sequentially (GPT) — unified reference
    # No threading, no cover_ready_event, no interdependency.
    # Same reference_image for ALL slides → same building identity.
    # ══════════════════════════════════════════════════════════════════════
    if image_settings and image_settings.get("generate_images"):
        _render_phase_chips("imaging")

        # Read the unified reference image ONCE before the loop (never changes inside)
        reference_image = get_project_reference_image(project_image_key) if project_image_key else None

        # Extract style signature once if not already cached
        if not style_signature_cached:
            try:
                style_signature_cached = extract_style_signature(ref_images_b64, fallback_style_text)
                sm.set_val("style_signature", style_signature_cached)
            except Exception as sig_err:
                logger.error("Failed to extract style signature: %s", sig_err)
                style_signature_cached = "modern architecture, photorealistic rendering"

        # Build list of slides that need images
        image_slides = [
            (i, slide_contents[i])
            for i in range(len(slide_contents))
            if slide_contents[i].get("requires_image")
        ]
        total_imgs = len(image_slides)

        for n, (idx, content) in enumerate(image_slides):
            slide_type = content.get("slide_type", "standard")
            topic = outline[idx].get("topic", f"{i18n.t('gen.slide_n')} {idx + 1}") if idx < len(outline) else ""
            title, body = _extract_readable(content)

            # Show spinner on this slide
            slide_placeholders[idx].markdown(
                _render_slide_html(
                    idx, slide_type, title or topic,
                    body + (
                        "<br><br><div style='display:flex;align-items:center;gap:0.5rem;"
                        "color:var(--color-primary);font-weight:600;font-size:0.9rem;'>"
                        "<span style='display:inline-block;width:12px;height:12px;"
                        "border:2px solid var(--color-primary);border-top-color:transparent;"
                        "border-radius:50%;animation:spin 0.8s linear infinite;'></span>"
                        "<i>جاري توليد الصورة...</i></div>"
                        "<style>@keyframes spin{to{transform:rotate(360deg)}}</style>"
                    )
                ),
                unsafe_allow_html=True,
            )

            # Check cache first
            cached = None
            if os.getenv("FORCE_REGENERATE_PROJECT_IMAGES", "").lower() not in {"1", "true", "yes"}:
                cached = get_project_slide_image(project_image_key, idx) if project_image_key else None

            try:
                if cached:
                    img_bytes = cached
                else:
                    # Determine image prompt
                    custom_prompt = content.get("image_prompt", "").strip()
                    if not custom_prompt:
                        target_prompts = image_settings.get("prompts", {}).get(title or topic, [])
                        if isinstance(target_prompts, str):
                            custom_prompt = target_prompts
                        elif isinstance(target_prompts, list) and target_prompts:
                            custom_prompt = target_prompts[0].get("prompt", "") if isinstance(target_prompts[0], dict) else ""

                    if custom_prompt:
                        img_prompt = custom_prompt
                    else:
                        scene = generate_consistent_image_prompt(
                            slide_title=title or content.get("title", ""),
                            slide_body=body,
                            style_signature=style_signature_cached,
                            slide_type=slide_type,
                        )
                        img_prompt = (
                            f"{scene}, matching the styling and structural identity of: {style_signature_cached}, "
                            f"highly detailed, photorealistic architectural visualization, clear architectural style, "
                            f"sharp focus, award-winning architectural photography, 8k resolution, no people, no text"
                        )

                    # Generate with unified reference_image → same building for ALL slides
                    img_bytes = generate_image(
                        prompt=img_prompt,
                        reference_image=reference_image,
                        seed=(project_seed + idx) % 1000000000,
                        is_commercial=is_commercial_project,
                    )
                    if project_image_key:
                        set_project_slide_image(project_image_key, idx, img_bytes)

                slide_images[idx] = img_bytes
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                slide_placeholders[idx].markdown(
                    _render_slide_html(idx, slide_type, title or topic, body, b64),
                    unsafe_allow_html=True,
                )
            except Exception as e:
                # ❗ Single image failure does NOT stop the rest
                logger.error("Image failed for slide %d: %s", idx, e, exc_info=True)
                slide_placeholders[idx].markdown(
                    _render_slide_html(
                        idx, slide_type, title or topic,
                        body + (
                            f"<br><br><div style='padding:0.75rem;background:rgba(239,68,68,0.1);"
                            f"border:1px solid var(--color-error);border-radius:var(--radius-sm);"
                            f"color:var(--color-error);font-size:0.875rem;'>"
                            f"<strong>تعذر توليد الصورة:</strong> {html.escape(str(e))}</div>"
                        )
                    ),
                    unsafe_allow_html=True,
                )

            progress_bar.progress(50 + int(((n + 1) / max(1, total_imgs)) * 35))

    sm.set_images(slide_images)

    _render_phase_chips("building")
    progress_bar.progress(88)
    pptx_path = None

    try:
        from generators.pptx_builder import build_presentation
        pptx_path = build_presentation(
            slide_contents,
            slide_images,
            project_data.get("project_name", "proposal"),
            theme=theme,
        )
        sm.set_pptx_path(pptx_path)
    except Exception as e:
        st.error(str(e))

    progress_bar.progress(95)

    try:
        from utils.pdf_exporter import export_to_pdf
        pdf_path = export_to_pdf(pptx_path)
        if pdf_path:
            sm.set_pdf_path(pdf_path)
        else:
            st.warning("⚠️ PDF export failed. PPTX is ready for download.")
    except Exception as e:
        st.warning(f"⚠️ PDF export unavailable: {e}")

    progress_bar.progress(100)
    st.session_state["_generation_running"] = False

    if pptx_path and Path(pptx_path).exists():
        st.success(i18n.t("gen.done_title"))
        st.write(i18n.t("gen.done_sub", slides=total_slides, images=len(slide_images)))

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(i18n.t("gen.preview_cta"), use_container_width=True, type="primary"):
                sm.set_stage("preview")
                st.rerun()
            with open(pptx_path, "rb") as f:
                st.download_button(
                    i18n.t("gen.download"),
                    data=f.read(),
                    file_name=Path(pptx_path).name,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True,
                )


def main():
    stage = sm.get_stage()
    render_app_shell(stage)

    if stage == "prompt":
        from ui.prompt_stage import render_prompt_stage
        render_prompt_stage()
    elif stage == "smart_review":
        from ui.smart_review_stage import render_smart_review
        render_smart_review()
    elif stage == "outline_review":
        from ui.outline_stage import render_outline_stage
        render_outline_stage()
    elif stage == "reference_image_setup":
        from ui.reference_image_setup import render_reference_image_setup
        render_reference_image_setup()
    elif stage == "settings":
        sm.set_stage("outline_review")
        st.rerun()
    elif stage == "generating":
        _handle_generation_stage()
    elif stage in ("preview", "editing"):
        from ui.preview import render_preview
        render_preview()
    else:
        sm.set_stage("prompt")
        st.rerun()
