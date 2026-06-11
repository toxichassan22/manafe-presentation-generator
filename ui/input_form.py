"""
Input Form UI – Streamlit form for project data entry.
Stage 1 of the workflow: Input → Preview → Edit.
"""

import streamlit as st
from config.branding import branding
from prompts.image_prompts import STYLES


def render_input_form() -> dict | None:
    """Render the project data input form.

    Returns:
        Dict with project data if form is submitted, else None.
    """
    st.markdown(
        f"""
        <h2 style='text-align: right; color: var(--color-primary);'>
            بيانات المشروع العقاري
        </h2>
        <p style='text-align: right; color: var(--color-text-secondary);'>
            أدخل بيانات المشروع لتوليد العرض التقديمي
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Load previously saved data if available
    from utils import state_manager as sm
    saved = sm.get_project_data() or {}

    with st.form("project_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            project_name = st.text_input(
                "اسم المشروع *",
                value=saved.get("project_name", ""),
                placeholder="مثال: مشروع الواحة السكني",
                help="اسم المشروع العقاري",
            )
            location = st.text_input(
                "الموقع *",
                value=saved.get("location", ""),
                placeholder="مثال: الرياض - حي النرجس",
                help="موقع المشروع",
            )
            land_area = st.text_input(
                "مساحة الأرض *",
                value=saved.get("land_area", ""),
                placeholder="مثال: 5000 متر مربع",
                help="مساحة الأرض بالمتر المربع",
            )
            budget = st.text_input(
                "الميزانية التقديرية",
                value=saved.get("budget", ""),
                placeholder="مثال: 10-15 مليون ريال",
                help="نطاق الميزانية المتوقعة",
            )

        with col2:
            building_style = st.selectbox(
                "الطراز المعماري *",
                options=list(STYLES.keys()),
                format_func=lambda x: {
                    "modern": "حديث (Modern)",
                    "classic": "كلاسيكي (Classic)",
                    "commercial": "تجاري (Commercial)",
                    "mixed_use": "متعدد الاستخدامات (Mixed Use)",
                    "luxury_villa": "فيلا فاخرة (Luxury Villa)",
                    "islamic": "إسلامي معاصر (Islamic Contemporary)",
                }.get(x, x),
                help="اختر الطراز المعماري المناسب",
            )
            floors = st.number_input(
                "عدد الطوابق *",
                min_value=1,
                max_value=100,
                value=saved.get("floors", 5),
                help="عدد طوابق المبنى",
            )
            num_slides = st.slider(
                "عدد الشرائح المطلوب *",
                min_value=3,
                max_value=25,
                value=max(3, saved.get("num_slides", 15)),
                step=1,
                help="اختر عدد شرائح العرض التقديمي",
            )

        building_description = st.text_area(
            "وصف المبنى *",
            value=saved.get("building_description", ""),
            placeholder="مثال: مبنى سكني فاخر يتكون من 5 طوابق مع مواقف سيارات تحت الأرض، مسبح على السطح، ومساحات خضراء محيطة",
            height=80,
            help="وصف تفصيلي للمبنى المطلوب",
        )
        
        floor_distribution = st.text_area(
            "توزيع الأدوار *",
            value=saved.get("floor_distribution", ""),
            placeholder="مثال: الدور الأرضي معارض تجارية، الدور الأول والثاني مكاتب إدارية، الدور الثالث والرابع شقق سكنية...",
            height=80,
            help="تفصيل ما يحتويه كل دور بناءً على طلب العميل",
        )

        st.markdown("---")
        st.markdown(
            "<p style='text-align: right; font-weight: bold;'>صورة الأرض</p>",
            unsafe_allow_html=True,
        )
        land_images = st.file_uploader(
            "ارفع صور الأرض (من عدة اتجاهات - اختياري لكن مُستحسن)",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            help="صور الأرض ستُستخدم لتحليل الموقع وتوليد تصورات معمارية مرتبطة بالبيئة المحيطة",
        )

        st.markdown("---")
        submitted = st.form_submit_button(
            "توليد العرض التقديمي",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            # Validate required fields
            errors = []
            if not project_name:
                errors.append("اسم المشروع مطلوب")
            if not location:
                errors.append("الموقع مطلوب")
            if not land_area:
                errors.append("مساحة الأرض مطلوبة")
            if not building_description:
                errors.append("وصف المبنى مطلوب")
            if not floor_distribution:
                errors.append("توزيع الأدوار مطلوب")

            if errors:
                for err in errors:
                    st.error(err)
                return None

            project_data = {
                "project_name": project_name,
                "location": location,
                "land_area": land_area,
                "building_description": building_description,
                "floor_distribution": floor_distribution,
                "building_style": building_style,
                "floors": floors,
                "budget": budget or "غير محدد",
                "num_slides": num_slides,
            }

            return {
                "project_data": project_data,
                "land_images": land_images,
            }

    return None
