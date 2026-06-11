"""
Editor UI – per-slide text editing and regeneration.
Stage 3 of the workflow: Input → Preview → Edit.
"""

import streamlit as st

from utils import state_manager as sm


def render_editor():
    """Render the slide editor interface."""
    slides = sm.get_slides()
    images = sm.get_images() or {}

    if not slides:
        st.warning("لا توجد شرائح للتعديل.")
        return

    st.markdown(
        """
        <h2 style='text-align: right; color: var(--color-primary);'>
            تعديل الشرائح
        </h2>
        <p style='text-align: right; color: var(--color-text-secondary);'>
            عدّل النصوص وأعد توليد الشرائح أو الصور حسب الحاجة
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Navigation buttons
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        if st.button("العودة للمعاينة", use_container_width=True):
            sm.set_stage("preview")
            st.rerun()
    with col2:
        if st.button("إعادة بناء PPTX", use_container_width=True, type="primary"):
            _rebuild_pptx()
    with col3:
        if st.button("بداية جديدة", use_container_width=True):
            sm.reset()
            st.rerun()

    st.markdown("---")

    # ── Slide-by-slide editor ─────────────────────────────────────
    for idx, slide in enumerate(slides):
        _render_slide_editor(idx, slide, images.get(idx))


def _render_slide_editor(idx: int, slide: dict, image_bytes: bytes | None):
    """Render editor for a single slide."""
    slide_type = slide.get("slide_type", "unknown")
    content = slide.get("content", {})
    title = content.get("title", f"شريحة {idx + 1}")

    with st.expander(f"شريحة {idx + 1}: {title}", expanded=False):
        # Title editor
        new_title = st.text_input(
            "العنوان",
            value=title,
            key=f"title_{idx}",
        )
        if new_title != title:
            content["title"] = new_title
            slide["content"] = content
            sm.update_slide(idx, slide)

        # Content editors based on what's in the content
        _edit_content_fields(idx, content, slide)

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"إعادة توليد النص", key=f"regen_text_{idx}"):
                _regenerate_text(idx)
        with col2:
            if slide_type in ["cover", "land_overview", "architectural_concept",
                              "exterior_design", "interior_design", "amenities"]:
                if st.button(f"إعادة توليد الصورة", key=f"regen_img_{idx}"):
                    _regenerate_image(idx)


def _edit_content_fields(idx: int, content: dict, slide: dict):
    """Render appropriate editors for the content dict fields."""
    # Edit text fields
    text_fields = ["description", "concept", "summary", "message", "vision",
                   "mission", "subtitle", "roi_note", "note", "cta", "certification"]
    for field in text_fields:
        if field in content and content[field]:
            new_val = st.text_area(
                field.replace("_", " ").title(),
                value=content[field],
                key=f"{field}_{idx}",
                height=100,
            )
            if new_val != content[field]:
                content[field] = new_val
                slide["content"] = content
                sm.update_slide(idx, slide)

    # Edit bullet lists
    list_fields = ["bullets", "highlights", "key_features", "features", "materials"]
    for field in list_fields:
        if field in content and isinstance(content[field], list):
            items = content[field]
            if items and isinstance(items[0], str):
                new_text = st.text_area(
                    f"{field.replace('_', ' ').title()} (سطر لكل عنصر)",
                    value="\n".join(items),
                    key=f"{field}_{idx}",
                    height=150,
                )
                new_items = [line.strip() for line in new_text.split("\n") if line.strip()]
                if new_items != items:
                    content[field] = new_items
                    slide["content"] = content
                    sm.update_slide(idx, slide)


def _regenerate_text(idx: int):
    """Regenerate text content for a single slide."""
    project_data = sm.get_project_data()
    land_analysis = sm.get_land_analysis() or {}

    if not project_data:
        st.error("بيانات المشروع غير متوفرة")
        return

    with st.spinner(f"جاري إعادة توليد الشريحة {idx + 1}..."):
        try:
            from generators.content_generator import regenerate_slide
            new_slide = regenerate_slide(idx, project_data, land_analysis, sm.get_slides())
            sm.update_slide(idx, new_slide)
            st.success(f"تم إعادة توليد الشريحة {idx + 1}")
            st.rerun()
        except Exception as e:
            st.error(f"خطأ: {e}")


def _regenerate_image(idx: int):
    """Regenerate image for a single slide."""
    project_data = sm.get_project_data()
    land_image = sm.get_land_image()

    if not project_data:
        st.error("بيانات المشروع غير متوفرة")
        return

    with st.spinner(f"جاري إعادة توليد صورة الشريحة {idx + 1}..."):
        try:
            from generators.image_generator import regenerate_image
            img_bytes = regenerate_image(idx, project_data, land_image, sm.get_slides(), sm.get_images() or {})
            if img_bytes:
                sm.update_image(idx, img_bytes)
                st.success(f"تم إعادة توليد صورة الشريحة {idx + 1}")
                st.rerun()
            else:
                st.warning("هذه الشريحة لا تحتوي على صورة")
        except Exception as e:
            st.error(f"خطأ: {e}")


def _rebuild_pptx():
    """Rebuild the PPTX with current (possibly edited) content."""
    slides = sm.get_slides()
    images = sm.get_images() or {}
    project_data = sm.get_project_data()

    if not slides or not project_data:
        st.error("لا توجد بيانات كافية لبناء العرض")
        return

    with st.spinner("جاري إعادة بناء العرض التقديمي..."):
        try:
            from generators.pptx_builder import build_presentation
            pptx_path = build_presentation(
                slides, images, project_data.get("project_name", "proposal")
            )
            sm.set_pptx_path(pptx_path)
            sm.set_pdf_path(None)  # Reset PDF since PPTX changed
            st.success(f"تم إعادة بناء العرض: {pptx_path.name}")
            sm.set_stage("preview")
            st.rerun()
        except Exception as e:
            st.error(f"خطأ في بناء العرض: {e}")
