import streamlit as st
import utils.state_manager as sm


def render_settings_stage():
    """Renders the theme and AI settings UI."""

    st.markdown(
        '<div class="surface-card" style="max-width: 900px; margin: 0 auto; padding: var(--space-5);">',
        unsafe_allow_html=True,
    )
    st.markdown('<h2 style="text-align: center; font-size: 1.75rem; font-weight: 700; color: var(--color-text-primary); margin-bottom: 0.5rem;">اللمسات الفنية والإعدادات</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: var(--color-text-secondary); margin-bottom: 2rem;">اختر كثافة النصوص، المظهر البصري، وإعدادات توليد الصور.</p>', unsafe_allow_html=True)

    # 1. Text Content Volume
    st.markdown('<h3 style="color: var(--color-text-primary); border-bottom: 1px solid var(--color-border); padding-bottom: 8px; margin-top: 30px; margin-bottom: 20px;">كثافة المحتوى (Text Content Volume)</h3>', unsafe_allow_html=True)
    density = st.radio(
        "اختر حجم وتفاصيل المحتوى المكتوب:",
        options=["Minimal (نقاط مختصرة جداً)", "Concise (موجز ومباشر)", "Detailed (تفصيلي)", "Extensive (شامل ومطول)"],
        index=1,
        horizontal=True,
    )

    # 2. Visual Theme
    st.markdown('<h3 style="color: var(--color-text-primary); border-bottom: 1px solid var(--color-border); padding-bottom: 8px; margin-top: 30px; margin-bottom: 20px;">المظهر البصري (Visual Theme)</h3>', unsafe_allow_html=True)
    col_t1, col_t2, col_t3 = st.columns(3)

    with col_t1:
        font_type = st.selectbox("نوع الخط (Font Type)", ["Arial", "Calibri", "Tajawal", "Cairo", "Almarai"])
    with col_t2:
        bg_color = st.color_picker("لون الخلفية (BG Color)", "#0B1120")
    with col_t3:
        text_color = st.color_picker("لون النص الأساسي (Font Color)", "#F1F5F9")

    theme = {
        "font": font_type,
        "bg_color": bg_color,
        "text_color": text_color,
    }

    # 3. AI Image Settings
    st.markdown('<h3 style="color: var(--color-text-primary); border-bottom: 1px solid var(--color-border); padding-bottom: 8px; margin-top: 30px; margin-bottom: 20px;">الصور والذكاء الاصطناعي</h3>', unsafe_allow_html=True)

    generate_images = st.toggle("توليد صور بالذكاء الاصطناعي للمشروع؟", value=True)

    image_settings = {
        "generate_images": generate_images,
        "prompts": {},
        "references": {},
    }

    if generate_images:
        outline = sm.get("outline") or []
        slide_topics = [s.get("topic", "شريحة بدون عنوان") for s in outline]

        if not slide_topics:
            st.warning("لا يوجد شرائح في الهيكل لاختيارها كعناوين.")
        else:
            num_images = st.number_input("عدد الصور المطلوبة", min_value=1, max_value=20, value=3)

            for i in range(int(num_images)):
                st.markdown(
                    '<div style="background: var(--color-surface-raised); border: 1px solid var(--color-border); padding: 15px; border-radius: var(--radius-md); margin-bottom: 15px;">',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**إعدادات الصورة #{i+1}**")

                target_heading = st.selectbox(
                    "مكان الصورة (تحت أي عنوان؟)",
                    options=slide_topics,
                    key=f"img_heading_{i}",
                )

                img_prompt = st.text_area(
                    "وصف دقيق للصورة",
                    placeholder="مثال: واجهة زجاجية حديثة لمبنى تجاري في شارع العليا وقت الغروب...",
                    key=f"img_prompt_{i}",
                )

                ref_images = st.file_uploader(
                    "صور مرجعية (اختياري)",
                    type=["png", "jpg", "jpeg"],
                    accept_multiple_files=True,
                    key=f"img_ref_{i}",
                )

                if target_heading not in image_settings["prompts"]:
                    image_settings["prompts"][target_heading] = []

                image_data = {
                    "prompt": img_prompt,
                    "reference_files": ref_images,
                }
                image_settings["prompts"][target_heading].append(image_data)

                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("رجوع للهيكل", use_container_width=True):
            sm.set_stage("outline_review")
            st.rerun()

    with col2:
        if st.button("بدء التوليد الحي", type="primary", use_container_width=True):
            sm.set_val("density", density)
            sm.set_val("theme", theme)

            from utils.document_parser import extract_base64_image
            clean_image_settings = {
                "generate_images": image_settings["generate_images"],
                "prompts": {},
            }

            for heading, img_list in image_settings["prompts"].items():
                clean_image_settings["prompts"][heading] = []
                for img in img_list:
                    base64_refs = []
                    if img["reference_files"]:
                        for f in img["reference_files"]:
                            base64_refs.append(extract_base64_image(f.getvalue()))

                    clean_image_settings["prompts"][heading].append({
                        "prompt": img["prompt"],
                        "references_b64": base64_refs,
                    })

            sm.set_val("image_settings", clean_image_settings)

            sm.set_stage("generating")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
