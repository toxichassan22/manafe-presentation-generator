import streamlit as st
from ui import i18n
import utils.state_manager as sm

ALL_STEPS = [
    {
        "id": "cover",
        "title": "🏠 شريحة الغلاف (Cover Slide)",
        "label": "🏠 1. الغلاف",
        "desc": "بيانات عنوان التقرير، تصنيف المشروع، موقع العقار، واسم العميل والتاريخ."
    },
    {
        "id": "introduction",
        "title": "📄 شريحة المقدمة (Introduction Slide)",
        "label": "📄 2. المقدمة والتمهيد",
        "desc": "التمهيد والوصف العام للمقترح الاستثماري وتحديد أهداف دراسة التطوير العقاري."
    },
    {
        "id": "executive_summary",
        "title": "📊 شريحة الملخص التنفيذي (Executive Summary)",
        "label": "📊 3. الملخص التنفيذي",
        "desc": "نظرة عامة على نوع المشروع الموصى به، مكوناته، المساحات التقديرية والمؤشرات المالية."
    },
    {
        "id": "site_analysis",
        "title": "📍 شريحة تحليل الموقع (Site Analysis)",
        "label": "📍 4. تحليل الموقع",
        "desc": "دراسة الشوارع المحيطة بالأرض، إمكانية الوصول، الحركة المرورية ونقاط القوة والتحديات."
    },
    {
        "id": "surrounding_landmarks",
        "title": "🏛️ شريحة المعالم المحيطة (Surrounding Landmarks)",
        "label": "🏛️ 5. المعالم المحيطة",
        "desc": "رصد المعالم التجارية أو الخدمية المحيطة المباشرة وتصنيفاتها واتجاهها الجغرافي."
    },
    {
        "id": "nearby_landmarks",
        "title": "🚗 شريحة المعالم القريبة (Nearby Landmarks & Drive Times)",
        "label": "🚗 6. المعالم القريبة",
        "desc": "تحديد أهم معالم الجذب الرئيسية بالمدينة ومسافة/زمن الوصول إليها بالسيارة."
    },
    {
        "id": "site_characteristics",
        "title": "📐 شريحة خصائص الموقع الجغرافية (Site Characteristics)",
        "label": "📐 7. خصائص الموقع",
        "desc": "بيانات الصك الرسمية، شكل الأرض، المناسيب، ونظام البناء المعتمد من البلدية."
    },
    {
        "id": "site_images",
        "title": "📸 شريحة صور الموقع (Site Images Layout)",
        "label": "📸 8. صور الموقع",
        "desc": "وصف اللقطات والصور الميدانية الحقيقية للأرض واتجاه تصويرها الأساسي."
    },
    {
        "id": "site_visits",
        "title": "📋 شريحة ملاحظات الزيارات الميدانية (Site Visit Notes)",
        "label": "📋 9. الزيارة الميدانية",
        "desc": "توثيق تاريخ الزيارة الميدانية وأبرز الملاحظات المرصودة على الطبيعة ومدى تأثيرها."
    },
    {
        "id": "key_brands",
        "title": "🏷️ شريحة العلامات التجارية بمنطقة العقار (Key Brands)",
        "label": "🏷️ 10. العلامات التجارية",
        "desc": "تحليل البراندات والأنشطة التجارية القائمة لتقييم الجاذبية السوقية للمستأجرين."
    },
    {
        "id": "development_options",
        "title": "🔄 شريحة بدائل التطوير والمقترحات المعمارية (Development Alternatives)",
        "label": "🔄 11. بدائل التطوير",
        "desc": "عرض الخيارات التقديرية لاستغلال الأرض، وتفصيل البديل الموصى به وأسباب التوصية."
    },
    {
        "id": "similar_projects",
        "title": "🏢 شريحة نماذج مشابهة ودراسة حالات مقارنة (Similar Projects)",
        "label": "🏢 12. نماذج مشابهة",
        "desc": "تحليل ودراسة مشاريع قائمة وناجحة مشابهة لاستنباط الدروس والفرص المقارنة."
    }
]

def init_structured_state():
    """Initialize structured proposal data state in st.session_state if not present."""
    if "structured_data" not in st.session_state:
        st.session_state["structured_data"] = {
            # Tab 1: Cover
            "cover_project_name": "",
            "cover_project_type": "تجاري إداري",
            "cover_project_type_custom": "",
            "cover_location": "",
            "cover_client_name": "",
            "cover_date": "مايو 2026",
            
            # Tab 2: Intro
            "intro_client_name": "",
            "intro_brief_desc": "",
            "intro_goal": "مقترح دراسة جدوى أولية",
            "intro_goal_custom": "",
            "intro_plot_number": "",
            "intro_location_details": "",
            "intro_land_area": "",
            
            # Tab 3: Exec
            "exec_project_type": "تجاري إداري",
            "exec_components": [],
            "exec_components_custom": "",
            "exec_land_area": "",
            "exec_built_area": "",
            "exec_leasable_area": "",
            "exec_units_count": "",
            "exec_duration": "",
            "exec_exit_strategy": "تطوير وتشغيل ثم تخارج",
            "exec_financial_indicators": "",
            
            # Tab 4: Site
            "site_desc": "",
            "site_streets": "",
            "site_accessibility": "ممتازة",
            "site_entrances": "",
            "site_traffic_level": "متوسطة",
            "site_traffic_notes": "",
            "site_strengths": "",
            "site_challenges": "",
            
            # Tab 5: Surrounding
            "surr_landmarks": "",
            "surr_landmark_type": [],
            "surr_landmark_direction": "شمال",
            
            # Tab 6: Nearby
            "near_landmarks": "",
            "near_travel_time": "",
            "near_landmark_type": "مشروع تطويري",
            
            # Tab 7: Specs
            "char_plot_map": "",
            "char_plot_num": "",
            "char_building_sys": "",
            "char_shape": "منتظم",
            "char_levels": "متساوية",
            "char_infrastructure": [],
            "char_additional_notes": "",
            
            # Tab 8: Images
            "site_images_direction": "من الشمال إلى الجنوب",
            "site_images_desc": "",
            
            # Tab 9: Visit
            "visit_date": "",
            "visit_observations": "",
            "visit_observation_type": "حركة مرورية",
            "visit_impact_level": "متوسط",
            
            # Tab 10: Brands
            "brands_names": "",
            "brands_activity": [],
            "brands_notes": "",
            
            # Tab 11: Alternatives
            "dev_options_count": "بديلين",
            "dev_opt1_name": "البديل الأول: تجاري إداري",
            "dev_opt1_desc": "تطوير مشروع تجاري إداري معارض في الأرضي ومكاتب في الأدوار العليا",
            "dev_opt1_elements": [],
            "dev_opt2_name": "البديل الثاني: متعدد الاستخدامات",
            "dev_opt2_desc": "تطوير مشروع يضم معارض تجارية في الأرضي وشقق سكنية/مكاتب في الأدوار العليا",
            "dev_opt2_elements": [],
            "dev_opt3_name": "",
            "dev_opt3_desc": "",
            "dev_opt3_elements": [],
            "dev_opt4_name": "",
            "dev_opt4_desc": "",
            "dev_opt4_elements": [],
            "dev_recommended": "البديل الأول",
            "dev_recommendation_reason": "أعلى عائد استثماري",
            "dev_recommendation_reason_custom": "",
            
            # Tab 12: Similar
            "similar_proj_name": "",
            "similar_proj_desc": "",
            "similar_proj_lessons": "",
        }
    if "custom_slides" not in st.session_state:
        st.session_state["custom_slides"] = []

    if "structured_selected_slide_ids" not in st.session_state:
        # Default all selected
        st.session_state["structured_selected_slide_ids"] = [step["id"] for step in ALL_STEPS]
        
    if "structured_step_index" not in st.session_state:
        st.session_state["structured_step_index"] = 0

def render_structured_form():
    """Renders the comprehensive structured wizard with customizable slide counts and step-by-step navigation."""
    init_structured_state()
    sdata = st.session_state["structured_data"]
    
    st.markdown(
        f"""
        <div style="background: var(--color-surface); padding: 1.5rem; border-radius: var(--radius-md); border: 1px solid var(--color-border); margin-bottom: 1.5rem; direction: rtl; text-align: right;">
            <h3 style="color: var(--color-primary); margin-top: 0; margin-bottom: 0.5rem;">📋 نموذج الإدخال الهيكلي الموجه لشركة منافع</h3>
            <p style="color: var(--color-text-secondary); font-size: 0.95rem; margin-bottom: 0;">
                قم بتخصيص هيكل تقريرك وتحديد الشرائح التي تريدها، ثم املأ البيانات خطوة بخطوة بالأسفل للتصدير المتناسق.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Define options from the PDF
    PROJECT_TYPES = [
        "تجاري", "إداري", "تجاري إداري", "سكني", "فندقي", "ضيافة", "متعدد الاستخدامات", 
        "تجزئة", "معارض", "مكاتب", "طبي", "تعليمي", "ترفيهي", "مطاعم ومقاهي", 
        "لوجستي", "مستودعات", "صناعي خفيف", "مواقف سيارات", "محطة خدمات", 
        "مجمع أعمال", "مركز تجاري", "بوليفارد تجاري", "مشروع واجهة طريق", 
        "مشروع استثماري مختلط", "أخرى"
    ]
    
    GOAL_OPTIONS = ["مقترح دراسة جدوى أولية", "تقييم فرصة استثمارية", "تحديد أفضل بديل تطويري", "تحليل موقع", "عرض استثماري", "أخرى"]
    EXIT_OPTIONS = ["تطوير ثم بيع", "تطوير وتشغيل", "تطوير وتشغيل ثم تخارج", "احتفاظ طويل الأجل", "أخرى"]
    ACCESSIBILITY_OPTIONS = ["ممتازة", "جيدة", "متوسطة", "محدودة"]
    TRAFFIC_OPTIONS = ["عالية", "متوسطة", "منخفضة"]
    LANDMARK_TYPES = ["موالت", "مستشفيات", "معارض سيارات", "بنوك", "مطاعم ومقاهي", "فنادق", "مراكز معارض", "محطات نقل", "أخرى"]
    DIRECTIONS = ["شمال", "جنوب", "شرق", "غرب", "شمال شرق", "شمال غرب", "جنوب شرق", "جنوب غرب"]
    NEARBY_TYPES = ["مطار", "مستشفى", "مركز تجاري", "مركز معارض", "مشروع تطويري", "طريق رئيسي", "محطة نقل", "أخرى"]
    SHAPE_OPTIONS = ["منتظم", "غير منتظم"]
    LEVELS_OPTIONS = ["متساوية", "متفاوتة", "مرتفعة عن الشارع", "منخفضة عن الشارع"]
    INFRASTRUCTURE_OPTIONS = ["مياه", "كهرباء", "صرف صحي", "اتصالات", "طرق قائمة"]
    VISIT_OBS_TYPES = ["حركة مرورية", "بنية تحتية", "مناسيب الأرض", "عوائق بالموقع", "لوحات إعلانية", "مبان مجاورة", "مداخل ومخارج", "ملاحظات بيئية", "أخرى"]
    IMPACT_OPTIONS = ["عالي", "متوسط", "منخفض"]
    BRANDS_ACTIVITIES = ["معارض سيارات", "صيانة سيارات", "قطع غيار", "مطاعم ومقاهي", "بنوك", "مواد بناء", "أجهزة ومعدات", "ترفيه", "تجزئة", "أخرى"]
    DEV_COUNT_OPTIONS = ["بديل واحد", "بديلين", "ثلاثة بدائل", "أربعة بدائل"]
    RECOMMENDATION_REASONS = ["أعلى عائد استثماري", "أفضل استغلال للموقع", "أقل تكلفة تطوير", "أسهل في التنفيذ", "أكثر ملاءمة للسوق", "أكثر مرونة في التأجير", "أخرى"]


    # 1. Slide Configurator - Collapsible expander
    all_available_steps = ALL_STEPS + st.session_state.get("custom_slides", [])
    
    with st.expander("⚙️ تخصيص وتحديد شرائح التقرير (تعديل عدد الصفحات والنوع)", expanded=False):
        st.markdown(
            """
            <div style="direction: rtl; text-align: right; margin-bottom: 1rem;">
                <p style="font-size: 0.9rem; color: var(--color-text-secondary);">اختر الشرائح التي تريد تضمينها في عرضك التقديمي. شريحة الغلاف إلزامية دائماً:</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Render checklist in a clean grid
        cols = st.columns(3)
        selected_slide_ids = ["cover"] # Cover is mandatory
        
        for idx, step in enumerate(ALL_STEPS):
            if step["id"] == "cover":
                with cols[0]:
                    st.checkbox("🏠 1. الغلاف (إلزامي)", value=True, disabled=True, key="chk_cover")
                continue
                
            col_idx = (idx) % 3
            with cols[col_idx]:
                was_selected = step["id"] in st.session_state["structured_selected_slide_ids"]
                is_selected = st.checkbox(step["label"], value=was_selected, key=f"chk_{step['id']}")
                if is_selected:
                    selected_slide_ids.append(step["id"])
                    
        # Now render custom slides if any exist
        custom_slides = st.session_state.get("custom_slides", [])
        if custom_slides:
            st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
            st.markdown("#### ✨ الشرائح المخصصة الحالية:")
            
            for idx, c_slide in enumerate(custom_slides):
                c_col1, c_col2 = st.columns([5, 1])
                with c_col1:
                    was_selected = c_slide["id"] in st.session_state["structured_selected_slide_ids"]
                    is_selected = st.checkbox(c_slide["label"], value=was_selected, key=f"chk_{c_slide['id']}")
                    if is_selected:
                        selected_slide_ids.append(c_slide["id"])
                with c_col2:
                    if st.button("🗑️", key=f"del_{c_slide['id']}", help="حذف هذه الشريحة تماماً"):
                        # Remove from custom_slides and selected_ids
                        st.session_state["custom_slides"] = [cs for cs in st.session_state["custom_slides"] if cs["id"] != c_slide["id"]]
                        if c_slide["id"] in st.session_state["structured_selected_slide_ids"]:
                            st.session_state["structured_selected_slide_ids"].remove(c_slide["id"])
                        st.toast(f"تم حذف شريحة {c_slide['label']}!")
                        st.rerun()

        # Dynamic Add Custom Slide Form
        st.markdown("<hr style='margin: 1.2rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### ➕ إضافة شريحة مخصصة جديدة (Add Custom Slide)")
        
        c_title = st.text_input("عنوان الشريحة المخصصة الجديدة", placeholder="مثال: تحليل المخاطر الاستثمارية / دراسة التربة...", key="add_custom_title")
        c_desc = st.text_input("وصف الشريحة (اختياري)", placeholder="مثال: تفصيل لأهم المخاطر المحتملة واستراتيجيات الحد منها...", key="add_custom_desc")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            c_type = st.selectbox("تخطيط الشريحة (Layout)", options=["standard", "two_column", "timeline", "chart", "cover"], format_func=lambda x: {
                "standard": "شريحة عادية مع رصاصات (Standard)",
                "two_column": "عمودين (Two Columns)",
                "timeline": "جدول زمني (Timeline)",
                "chart": "رسم بياني (Chart)",
                "cover": "غلاف قسم (Section Cover)"
            }.get(x, x), key="add_custom_type")
        with col_c2:
            c_req_img = st.checkbox("تتطلب صورة بالذكاء الاصطناعي", value=False, key="add_custom_req_img")
            
        if st.button("➕ إضافة الشريحة للقائمة", type="secondary", use_container_width=True):
            if c_title.strip():
                new_id = f"custom_{len(st.session_state['custom_slides']) + 1}_{hash(c_title.strip()) % 1000}"
                new_slide = {
                    "id": new_id,
                    "title": f"✨ {c_title.strip()}",
                    "label": f"✨ {c_title.strip()}",
                    "desc": c_desc.strip() or "شريحة مخصصة مضافة بواسطة المستخدم.",
                    "slide_type": c_type,
                    "requires_image": c_req_img,
                    "image_prompt": f"Professional real estate architectural rendering for {c_title.strip()}, modern style" if c_req_img else "",
                    "content": ""
                }
                st.session_state["custom_slides"].append(new_slide)
                st.session_state["structured_selected_slide_ids"].append(new_id)
                st.toast(f"تمت إضافة شريحة '{c_title.strip()}' بنجاح!")
                st.rerun()
            else:
                st.error("الرجاء إدخال عنوان الشريحة أولاً!")

        # Update session state with new selection
        st.session_state["structured_selected_slide_ids"] = selected_slide_ids

    # Get current list of selected steps
    selected_steps = [step for step in all_available_steps if step["id"] in st.session_state["structured_selected_slide_ids"]]
    total_steps = len(selected_steps)

    # Clamp step index to valid range
    if st.session_state["structured_step_index"] >= total_steps:
        st.session_state["structured_step_index"] = max(0, total_steps - 1)
        
    current_idx = st.session_state["structured_step_index"]
    active_step = selected_steps[current_idx]
    
    # 2. Sleek Custom Header/Progress Bar
    completion_percentage = int(((current_idx + 1) / total_steps) * 100)
    
    st.markdown(
        f"""
        <div style="background: var(--color-surface); padding: 1.25rem; border-radius: var(--radius-md); border-right: 5px solid var(--color-primary); border: 1px solid var(--color-border); border-right: 5px solid var(--color-primary); margin-bottom: 2rem; direction: rtl; text-align: right;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span style="font-size: 0.9rem; font-weight: 600; color: var(--color-primary);">
                    📍 {active_step['title']}
                </span>
                <span style="font-size: 0.85rem; color: var(--color-text-secondary); font-weight: 500;">
                    الخطوة {current_idx + 1} من {total_steps} ({completion_percentage}%)
                </span>
            </div>
            <p style="margin: 0 0 1rem 0; font-size: 0.85rem; color: var(--color-text-secondary); line-height: 1.4;">
                {active_step['desc']}
            </p>
            <div style="background: rgba(103, 13, 12, 0.1); width: 100%; height: 6px; border-radius: 99px; overflow: hidden;">
                <div style="background: var(--color-primary); width: {completion_percentage}%; height: 100%; transition: width 0.3s ease;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 3. Render only the active step
    step_id = active_step["id"]
    
    if step_id == "cover":
        st.subheader("🏠 بيانات شريحة الغلاف")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            sdata["cover_project_name"] = st.text_input(
                "اسم الدراسة / المشروع كتابة *",
                value=sdata["cover_project_name"],
                placeholder="مثال: دراسة جدوى تطوير أرض مجمع تجاري بالصحافة",
                key="scover_project_name"
            )
            sdata["cover_location"] = st.text_input(
                "موقع المشروع كتابة *",
                value=sdata["cover_location"],
                placeholder="مثال: الرياض، حي الصحافة، تقاطع طريق الملك فهد مع طريق أنس بن مالك",
                key="scover_location"
            )
        with col_c2:
            sdata["cover_project_type"] = st.selectbox(
                "نوع المشروع *",
                options=PROJECT_TYPES,
                index=PROJECT_TYPES.index(sdata["cover_project_type"]) if sdata["cover_project_type"] in PROJECT_TYPES else 2,
                key="scover_project_type"
            )
            if sdata["cover_project_type"] == "أخرى":
                sdata["cover_project_type_custom"] = st.text_input(
                    "اكتب نوع المشروع المخصص *",
                    value=sdata["cover_project_type_custom"],
                    placeholder="اكتب نوع المشروع هنا...",
                    key="scover_project_type_custom"
                )
            
            sdata["cover_client_name"] = st.text_input(
                "اسم الجهة المالكة / العميل كتابة *",
                value=sdata["cover_client_name"],
                placeholder="مثال: شركة منافع الاقتصادية للعقار / شركة ركاز الاستثمارية",
                key="scover_client_name"
            )
            
        sdata["cover_date"] = st.text_input(
            "تاريخ الإصدار كتابة *",
            value=sdata["cover_date"],
            placeholder="مثال: مايو 2026 / 1447 هـ",
            key="scover_date"
        )

    elif step_id == "introduction":
        st.subheader("📄 بيانات شريحة المقدمة")
        sdata["intro_client_name"] = st.text_input(
            "اسم العميل كتابة *",
            value=sdata["intro_client_name"] or sdata["cover_client_name"],
            placeholder="اسم العميل أو الجهة المستفيدة...",
            key="sintro_client_name"
        )
        
        sdata["intro_brief_desc"] = st.text_area(
            "وصف مختصر للمشروع كتابة *",
            value=sdata["intro_brief_desc"],
            placeholder="مثال: يهدف المشروع إلى دراسة وتطوير فرصة استثمارية عقارية متميزة لإنشاء مجمع تجاري إداري فاخر يلبي الطلب المتزايد على المكاتب والمعارض الراقية بالمنطقة...",
            height=120,
            key="sintro_brief_desc"
        )
        
        sdata["intro_goal"] = st.selectbox(
            "الهدف من الدراسة خيار مقترح *",
            options=GOAL_OPTIONS,
            index=GOAL_OPTIONS.index(sdata["intro_goal"]) if sdata["intro_goal"] in GOAL_OPTIONS else 0,
            key="sintro_goal"
        )
        if sdata["intro_goal"] == "أخرى":
            sdata["intro_goal_custom"] = st.text_input(
                "اكتب الهدف المخصص *",
                value=sdata["intro_goal_custom"],
                key="sintro_goal_custom"
            )
            
        col1, col2 = st.columns(2)
        with col1:
            sdata["intro_plot_number"] = st.text_input(
                "رقم الأرض / رقم المخطط كتابة",
                value=sdata["intro_plot_number"],
                placeholder="مثال: قطعة رقم 45، مخطط رقم 1200",
                key="sintro_plot_number"
            )
            sdata["intro_land_area"] = st.text_input(
                "مساحة الأرض كتابة *",
                value=sdata["intro_land_area"],
                placeholder="مثال: 4,500 متر مربع",
                key="sintro_land_area"
            )
        with col2:
            sdata["intro_location_details"] = st.text_input(
                "المدينة / الحي / الشارع كتابة *",
                value=sdata["intro_location_details"] or sdata["cover_location"],
                placeholder="مثال: الرياض، حي الصحافة، شارع العليا العام",
                key="sintro_location_details"
            )

    elif step_id == "executive_summary":
        st.subheader("📊 بيانات الملخص التنفيذي")
        sdata["exec_project_type"] = st.text_input(
            "نوع المشروع المقترح *",
            value=sdata["exec_project_type"] or sdata["cover_project_type"],
            placeholder="مثال: مجمع تجاري إداري فاخر (بوليفارد)",
            key="sexec_project_type"
        )
        
        sdata["exec_components"] = st.multiselect(
            "مكونات المشروع اختيار *",
            options=PROJECT_TYPES,
            default=[c for c in sdata["exec_components"] if c in PROJECT_TYPES],
            key="sexec_components"
        )
        sdata["exec_components_custom"] = st.text_input(
            "مكونات إضافية (اكتب يدوياً في حال لم تجدها بالخيارات)",
            value=sdata["exec_components_custom"],
            placeholder="مثال: نادي صحي، مواقف ذكية، شاشات إعلانية ضخمة...",
            key="sexec_components_custom"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            sdata["exec_land_area"] = st.text_input(
                "مساحة الأرض *",
                value=sdata["exec_land_area"] or sdata["intro_land_area"],
                placeholder="مثال: 4,500 م²",
                key="sexec_land_area"
            )
            sdata["exec_built_area"] = st.text_input(
                "المساحة المبنية (BUA) كتابة *",
                value=sdata["exec_built_area"],
                placeholder="مثال: 9,800 م²",
                key="sexec_built_area"
            )
            sdata["exec_leasable_area"] = st.text_input(
                "المساحة التأجيرية (GLA) كتابة *",
                value=sdata["exec_leasable_area"],
                placeholder="مثال: 7,500 م²",
                key="sexec_leasable_area"
            )
        with col2:
            sdata["exec_units_count"] = st.text_input(
                "عدد الوحدات كتابة *",
                value=sdata["exec_units_count"],
                placeholder="مثال: 12 معرضاً تجارياً، و45 مكتباً إدارياً",
                key="sexec_units_count"
            )
            sdata["exec_duration"] = st.text_input(
                "مدة التطوير والتشغيل كتابة *",
                value=sdata["exec_duration"],
                placeholder="مثال: سنتين للتطوير، و15 سنة تشغيل واستثمار",
                key="sexec_duration"
            )
            sdata["exec_exit_strategy"] = st.selectbox(
                "استراتيجية التخارج خيار مقترح *",
                options=EXIT_OPTIONS,
                index=EXIT_OPTIONS.index(sdata["exec_exit_strategy"]) if sdata["exec_exit_strategy"] in EXIT_OPTIONS else 2,
                key="sexec_exit_strategy"
            )
            
        sdata["exec_financial_indicators"] = st.text_area(
            "أبرز المؤشرات المالية المتوقعة كتابة *",
            value=sdata["exec_financial_indicators"],
            placeholder="مثال: \n- إجمالي التكاليف الاستثمارية: 45 مليون ريال\n- صافي القيمة الحالية (NPV): 12 مليون ريال\n- معدل العائد الداخلي (IRR): 18.5%\n- فترة استرداد رأس المال: 6.5 سنوات",
            height=120,
            key="sexec_financial_indicators"
        )

    elif step_id == "site_analysis":
        st.subheader("📍 بيانات شريحة تحليل الموقع")
        sdata["site_desc"] = st.text_area(
            "وصف موقع الأرض كتابة *",
            value=sdata["site_desc"],
            placeholder="مثال: تقع الأرض في موقع استراتيجي في شمال مدينة الرياض بحي الصحافة، وتتميز بواجهة مباشرة على طريق العليا العام وخطوط بصرية وحركة مرورية متميزة وتجاور حي الملقا وحي الياسمين الراقيين...",
            height=100,
            key="ssite_desc"
        )
        
        sdata["site_streets"] = st.text_input(
            "الشوارع المحيطة كتابة *",
            value=sdata["site_streets"],
            placeholder="مثال: طريق العليا العام من الشرق بعرض 60م، وشارع تجاري فرعي من الجنوب بعرض 20م",
            key="ssite_streets"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            sdata["site_accessibility"] = st.selectbox(
                "سهولة الوصول للموقع خيار مقترح *",
                options=ACCESSIBILITY_OPTIONS,
                index=ACCESSIBILITY_OPTIONS.index(sdata["site_accessibility"]) if sdata["site_accessibility"] in ACCESSIBILITY_OPTIONS else 0,
                key="ssite_accessibility"
            )
            sdata["site_entrances"] = st.text_input(
                "المداخل والمخارج كتابة *",
                value=sdata["site_entrances"],
                placeholder="مثال: مدخل رئيسي مباشر من طريق العليا العام، ومخرج خدمي فرعي من الشارع الجنوبي",
                key="ssite_entrances"
            )
        with col2:
            sdata["site_traffic_level"] = st.selectbox(
                "مستوى الحركة المرورية خيار مقترح *",
                options=TRAFFIC_OPTIONS,
                index=TRAFFIC_OPTIONS.index(sdata["site_traffic_level"]) if sdata["site_traffic_level"] in TRAFFIC_OPTIONS else 1,
                key="ssite_traffic_level"
            )
            sdata["site_traffic_notes"] = st.text_input(
                "الملاحظات المرورية كتابة",
                value=sdata["site_traffic_notes"],
                placeholder="مثال: ذروة مرورية عالية خلال فترات الصباح والمساء نتيجة القرب من مراكز الأعمال",
                key="ssite_traffic_notes"
            )
            
        sdata["site_strengths"] = st.text_area(
            "مميزات الموقع كتابة *",
            value=sdata["site_strengths"],
            placeholder="مثال: \n- موقع حيوي للغاية في منطقة أعمال نشطة\n- سهولة وصول فائقة من الطرق المحورية الكبرى\n- واجهة عريضة تعطي بروزاً إعلانياً وتجارياً فائقاً للمستأجرين",
            height=100,
            key="ssite_strengths"
        )
        
        sdata["site_challenges"] = st.text_area(
            "تحديات الموقع وعوائقه كتابة *",
            value=sdata["site_challenges"],
            placeholder="مثال: \n- الازدحام المروري أوقات الذروة مما يتطلب زيادة مساحات المواقف والقبو\n- ارتفاع أسعار الأراضي المجاورة مما يزيد من أهمية التوظيف الاستثماري الأمثل للمساحات",
            height=100,
            key="ssite_challenges"
        )

    elif step_id == "surrounding_landmarks":
        st.subheader("🏛️ بيانات المعالم المحيطة")
        sdata["surr_landmarks"] = st.text_area(
            "أسماء المعالم التجارية أو الخدمية حول الموقع كتابة *",
            value=sdata["surr_landmarks"],
            placeholder="مثال: مجمع رياض بارك، فندق هيلتون الصحافة، مبنى الهيئة العامة للغذاء والدواء، مستشفى الحبيب بالعليا...",
            height=100,
            key="ssurr_landmarks"
        )
        
        sdata["surr_landmark_type"] = st.multiselect(
            "نوع المعالم خيار مقترح *",
            options=LANDMARK_TYPES,
            default=[t for t in sdata["surr_landmark_type"] if t in LANDMARK_TYPES],
            key="ssurr_landmark_type"
        )
        
        sdata["surr_landmark_direction"] = st.selectbox(
            "موقع أغلب هذه المعالم بالنسبة للأرض *",
            options=DIRECTIONS,
            index=DIRECTIONS.index(sdata["surr_landmark_direction"]) if sdata["surr_landmark_direction"] in DIRECTIONS else 0,
            key="ssurr_landmark_direction"
        )

    elif step_id == "nearby_landmarks":
        st.subheader("🚗 بيانات المعالم القريبة وأوقات الوصول")
        sdata["near_landmarks"] = st.text_area(
            "أسماء أهم المعالم القريبة الرئيسية كتابة *",
            value=sdata["near_landmarks"],
            placeholder="مثال:\n- مركز الملك عبد الله المالي (KAFD)\n- مطار الملك خالد الدولي\n- محطة مترو الرياض الصحافة",
            height=100,
            key="snear_landmarks"
        )
        
        sdata["near_travel_time"] = st.text_area(
            "مدة الوصول للسيارة لكل معلم كتابة *",
            value=sdata["near_travel_time"],
            placeholder="مثال:\n- مركز الملك عبد الله المالي (KAFD): 5 دقائق\n- مطار الملك خالد الدولي: 15 دقيقة\n- محطة مترو الرياض الصحافة: 3 دقائق سيراً على الأقدام",
            height=100,
            key="snear_travel_time"
        )
        
        sdata["near_landmark_type"] = st.selectbox(
            "نوع المعلم الغالب *",
            options=NEARBY_TYPES,
            index=NEARBY_TYPES.index(sdata["near_landmark_type"]) if sdata["near_landmark_type"] in NEARBY_TYPES else 4,
            key="snear_landmark_type"
        )

    elif step_id == "site_characteristics":
        st.subheader("📐 بيانات خصائص الموقع الجغرافية ونظام البناء")
        col1, col2 = st.columns(2)
        with col1:
            sdata["char_plot_map"] = st.text_input("رقم المخطط كتابة *", value=sdata["char_plot_map"], placeholder="مثال: مخطط رقم 2345 / ب", key="schar_plot_map")
            sdata["char_plot_num"] = st.text_input("رقم القطعة كتابة *", value=sdata["char_plot_num"], placeholder="مثال: قطعة رقم 12 و 13", key="schar_plot_num")
            sdata["char_building_sys"] = st.text_input("نظام البناء والارتدادات كتابة *", value=sdata["char_building_sys"], placeholder="مثال: تجاري - أرضي + 3 متكرر، نسبة التغطية 60%", key="schar_building_sys")
        with col2:
            sdata["char_shape"] = st.selectbox("شكل الأرض خيار مقترح *", options=SHAPE_OPTIONS, index=SHAPE_OPTIONS.index(sdata["char_shape"]), key="schar_shape")
            sdata["char_levels"] = st.selectbox("المناسيب خيار مقترح *", options=LEVELS_OPTIONS, index=LEVELS_OPTIONS.index(sdata["char_levels"]), key="schar_levels")
            sdata["char_infrastructure"] = st.multiselect(
                "توفر البنية التحتية خيار مقترح *",
                options=INFRASTRUCTURE_OPTIONS,
                default=[i for i in sdata["char_infrastructure"] if i in INFRASTRUCTURE_OPTIONS],
                key="schar_infrastructure"
            )
            
        sdata["char_additional_notes"] = st.text_area(
            "ملاحظات إضافية على الأرض والتربة",
            value=sdata["char_additional_notes"],
            placeholder="مثال: الأرض مستوية تماماً وصالحة للحفر المباشر لبناء القبو، متوفر كافة الخدمات الرئيسية من اتصالات ومياه وكهرباء ذات أحمال عالية بمحيط الأرض المباشر...",
            height=100,
            key="schar_additional_notes"
        )

    elif step_id == "site_images":
        st.subheader("📸 بيانات صور الموقع واللقطات الميدانية")
        st.info("💡 سيتم دمج صور الأرض الحقيقية المرفوعة في تبويب 'ملفات مرجعية' تلقائياً داخل هذه الشريحة وتسميتها بالبيانات أدناه.")
        
        sdata["site_images_direction"] = st.selectbox(
            "اتجاه التقاط الصورة الأساسي خيار مقترح",
            options=[
                "من الشمال إلى الجنوب", "من الجنوب إلى الشمال", "من الشرق إلى الغرب", "من الغرب إلى الشرق",
                "من شمال شرق", "من شمال غرب", "من جنوب شرق", "من جنوب غرب"
            ],
            index=0,
            key="ssite_images_direction"
        )
        
        sdata["site_images_desc"] = st.text_area(
            "وصف وتفاصيل الصور كتابة *",
            value=sdata["site_images_desc"],
            placeholder="مثال: لقطات ميدانية حديثة للأرض المخصصة للمشروع من اتجاه طريق العليا العام توضح واجهة الأرض المستوية وخلوها من العوائق المادية أو الصخرية مع توفر الأرصفة الجاهزة والشوارع المحيطة...",
            height=120,
            key="ssite_images_desc"
        )

    elif step_id == "site_visits":
        st.subheader("📋 تقرير وملاحظات الزيارة الميدانية")
        sdata["visit_date"] = st.text_input(
            "تاريخ الزيارة الميدانية كتابة *",
            value=sdata["visit_date"],
            placeholder="مثال: 15 مايو 2026م",
            key="svisit_date"
        )
        
        sdata["visit_observations"] = st.text_area(
            "أبرز الملاحظات والنتائج المرصودة بالزيارة كتابة *",
            value=sdata["visit_observations"],
            placeholder="مثال: \n- سهولة وصول ممتازة للموقع وخلو الشوارع الفرعية من الاختناقات الكبرى\n- تجاور الأرض مع مجمع سكني فاخر يعطي ميزة لبناء مجمع يخدم المنطقة بالكامل\n- تم التأكد من عدم وجود أي خطوط كهرباء هوائية أو أبراج ضغط تعيق الإنشاء",
            height=120,
            key="svisit_observations"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            sdata["visit_observation_type"] = st.selectbox(
                "نوع الملاحظة الغالب خيار مقترح *",
                options=VISIT_OBS_TYPES,
                index=VISIT_OBS_TYPES.index(sdata["visit_observation_type"]) if sdata["visit_observation_type"] in VISIT_OBS_TYPES else 0,
                key="svisit_observation_type"
            )
        with col2:
            sdata["visit_impact_level"] = st.selectbox(
                "مستوى الأثر على دراسة المشروع خيار مقترح *",
                options=IMPACT_OPTIONS,
                index=IMPACT_OPTIONS.index(sdata["visit_impact_level"]) if sdata["visit_impact_level"] in IMPACT_OPTIONS else 1,
                key="svisit_impact_level"
            )

    elif step_id == "key_brands":
        st.subheader("🏷️ تحليل العلامات التجارية بالمنطقة")
        sdata["brands_names"] = st.text_area(
            "أسماء العلامات التجارية القريبة كتابة *",
            value=sdata["brands_names"],
            placeholder="مثال: ستاربكس، دانكن، صيدلية الدواء، جرير، أسواق التميمي، بنك الراجحي، شاورمر...",
            height=100,
            key="sbrands_names"
        )
        
        sdata["brands_activity"] = st.multiselect(
            "تصنيف الأنشطة الموجودة بالمنطقة خيار مقترح *",
            options=BRANDS_ACTIVITIES,
            default=[a for a in sdata["brands_activity"] if a in BRANDS_ACTIVITIES],
            key="sbrands_activity"
        )
        
        sdata["brands_notes"] = st.text_area(
            "ملاحظات على طبيعة وجاذبية النشاط التجاري المحيط كتابة *",
            value=sdata["brands_notes"],
            placeholder="مثال: يلاحظ تركز العلامات التجارية الفاخرة للقهوة والمطاعم الراقية في محيط 500 متر من الأرض، مما يدل على القوة الشرائية المرتفعة لسكان الحي ورواد المنطقة ويعطي مؤشراً ممتازاً لنجاح العلامات التجارية المستهدفة بمشروعنا...",
            height=120,
            key="sbrands_notes"
        )

    elif step_id == "development_options":
        st.subheader("🔄 بدائل التطوير والمقترحات المعمارية")
        sdata["dev_options_count"] = st.selectbox(
            "كم عدد البدائل التي ترغب بدراستها وعرضها؟ *",
            options=DEV_COUNT_OPTIONS,
            index=DEV_COUNT_OPTIONS.index(sdata["dev_options_count"]),
            key="sdev_options_count"
        )
        
        st.markdown("#### تفاصيل البدائل المحددة:")
        
        # البديل الأول (دائماً معروض)
        with st.expander(sdata["dev_opt1_name"] or "تفاصيل البديل الأول", expanded=True):
            sdata["dev_opt1_name"] = st.text_input("اسم البديل الأول *", value=sdata["dev_opt1_name"], placeholder="مثال: البديل الأول (مجمع معارض ومكاتب)", key="sdev_opt1_name")
            sdata["dev_opt1_desc"] = st.text_area("وصف البديل الأول وأرقامه التقديرية *", value=sdata["dev_opt1_desc"], placeholder="مثال: مجمع تجاري إداري بارتفاع 3 طوابق، يحتوي على 14 معرضاً تجارياً في الدور الأرضي و40 مكتباً إدارياً للأدوار العليا مع توفير قبو للمواقف بمساحة كامل الأرض...", key="sdev_opt1_desc")
            
        # البديل الثاني
        if sdata["dev_options_count"] in ["بديلين", "ثلاثة بدائل", "أربعة بدائل"]:
            with st.expander(sdata["dev_opt2_name"] or "تفاصيل البديل الثاني", expanded=True):
                sdata["dev_opt2_name"] = st.text_input("اسم البديل الثاني *", value=sdata["dev_opt2_name"] or "البديل الثاني: متعدد الاستخدامات (تجزئة وسكني)", placeholder="مثال: البديل الثاني (تجزئة وسكني فاخر)", key="sdev_opt2_name")
                sdata["dev_opt2_desc"] = st.text_area("وصف البديل الثاني وأرقامه التقديرية *", value=sdata["dev_opt2_desc"], placeholder="مثال: مبنى متعدد الاستخدامات يحتوي معارض تجارية في الأرضي والميزانين، وطوابق علوية تضم شققاً سكنية فاخرة أو شققاً فندقية ذات عوائد استثمارية تشغيلية ممتازة...", key="sdev_opt2_desc")
                
        # البديل الثالث
        if sdata["dev_options_count"] in ["ثلاثة بدائل", "أربعة بدائل"]:
            with st.expander(sdata["dev_opt3_name"] or "تفاصيل البديل الثالث", expanded=True):
                sdata["dev_opt3_name"] = st.text_input("اسم البديل الثالث *", value=sdata["dev_opt3_name"] or "البديل الثالث: طبي أو مكاتب مستقلة", placeholder="مثال: البديل الثالث (مجمع طبي متكامل)", key="sdev_opt3_name")
                sdata["dev_opt3_desc"] = st.text_area("وصف البديل الثالث وأرقامه التقديرية *", value=sdata["dev_opt3_desc"], key="sdev_opt3_desc")

        # البديل الرابع
        if sdata["dev_options_count"] == "أربعة بدائل":
            with st.expander(sdata["dev_opt4_name"] or "تفاصيل البديل الرابع", expanded=True):
                sdata["dev_opt4_name"] = st.text_input("اسم البديل الرابع *", value=sdata["dev_opt4_name"] or "البديل الرابع: فندقي وضيافة", placeholder="مثال: البديل الرابع (شقق فندقية راقية)", key="sdev_opt4_name")
                sdata["dev_opt4_desc"] = st.text_area("وصف البديل الرابع وأرقامه التقديرية *", value=sdata["dev_opt4_desc"], key="sdev_opt4_desc")
                
        st.markdown("#### التوصية والبديل الموصى به:")
        col1, col2 = st.columns(2)
        with col1:
            sdata["dev_recommended"] = st.text_input(
                "اسم البديل الموصى به *",
                value=sdata["dev_recommended"],
                placeholder="مثال: البديل الأول (مجمع معارض ومكاتب)",
                key="sdev_recommended"
            )
        with col2:
            sdata["dev_recommendation_reason"] = st.selectbox(
                "أبرز أسباب التوصية خيار مقترح *",
                options=RECOMMENDATION_REASONS,
                index=RECOMMENDATION_REASONS.index(sdata["dev_recommendation_reason"]) if sdata["dev_recommendation_reason"] in RECOMMENDATION_REASONS else 0,
                key="sdev_recommendation_reason"
            )
            if sdata["dev_recommendation_reason"] == "أخرى":
                sdata["dev_recommendation_reason_custom"] = st.text_input(
                    "اكتب سبب التوصية المخصص *",
                    value=sdata["dev_recommendation_reason_custom"],
                    key="sdev_recommendation_reason_custom"
                )

    elif step_id == "similar_projects":
        st.subheader("🏢 دراسة الحالات والمشاريع المرجعية المشابهة")
        sdata["similar_proj_name"] = st.text_input(
            "أسماء وموقع المشاريع المشابهة المقارنة *",
            value=sdata["similar_proj_name"],
            placeholder="مثال: مشروع بوليفارد يو ووك (طريق الأمير تركي بن عبد العزيز الأول)، مجمع الواحة سكوير",
            key="ssimilar_proj_name"
        )
        
        sdata["similar_proj_desc"] = st.text_area(
            "وصف وتفاصيل المشاريع المشابهة ونجاحها بالمنطقة كتابة *",
            value=sdata["similar_proj_desc"],
            placeholder="مثال: مجمع يو ووك يتميز بتوفير ممرات مشاة ومطاعم ومعارض مفتوحة فاخرة وحقق نسبة إشغال 100% خلال السنة الأولى من تشغيله مع متوسط إيجار مرتفع للمتر التجاري والمكتبي...",
            height=120,
            key="ssimilar_proj_desc"
        )
        
        sdata["similar_proj_lessons"] = st.text_area(
            "النقاط المستفادة والتوصيات المقارنة لمشروعنا كتابة *",
            value=sdata["similar_proj_lessons"],
            placeholder="مثال: يوصى بالاقتداء بنموذج المعارض المفتوحة والواجهات الزجاجية الواسعة مع تدعيم مواقف القبو، وتوفير خيارات لدمج المكاتب مع تراسات خارجية للاستفادة من الميزة التنافسية للأرض وحجم الطلب...",
            height=120,
            key="ssimilar_proj_lessons"
        )
        
    elif step_id.startswith("custom_"):
        # Find the custom slide details
        custom_slide = next((cs for cs in st.session_state["custom_slides"] if cs["id"] == step_id), None)
        if custom_slide:
            st.subheader(f"✨ شريحة مخصصة: {custom_slide['title'].replace('✨ ', '')}")
            
            custom_slide["title"] = st.text_input(
                "عنوان الشريحة *",
                value=custom_slide["title"],
                key=f"custom_title_input_{step_id}"
            )
            custom_slide["label"] = custom_slide["title"]
            
            custom_slide["requires_image"] = st.checkbox(
                "تتطلب صورة بالذكاء الاصطناعي",
                value=custom_slide["requires_image"],
                key=f"custom_req_img_input_{step_id}"
            )
            
            if custom_slide["requires_image"]:
                custom_slide["image_prompt"] = st.text_area(
                    "وصف الصورة المطلوبة (Image Prompt) *",
                    value=custom_slide["image_prompt"],
                    placeholder="مثال: تصميم داخلي فاخر ومودرن للمكتب المشترك بإضاءة طبيعية...",
                    key=f"custom_img_prompt_input_{step_id}"
                )
                
            custom_slide["content"] = st.text_area(
                "محتوى الشريحة التفصيلي كتابة (اتركه فارغاً ليقوم الذكاء الاصطناعي بصياغته تلقائياً) *",
                value=custom_slide.get("content", ""),
                placeholder="اكتب المحتوى أو النقاط الأساسية التي ترغب بظهورها في الشريحة باللغة العربية...",
                height=150,
                key=f"custom_content_input_{step_id}"
            )
            
    # 4. Step Bottom Navigation Bar
    st.markdown("---")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    
    with nav_col1:
        if current_idx > 0:
            if st.button("⬅️ السابق", use_container_width=True, key="btn_prev_step"):
                st.session_state["structured_step_index"] -= 1
                st.rerun()
                
    with nav_col2:
        st.markdown(
            f"""
            <div style="text-align: center; color: var(--color-text-secondary); padding-top: 0.5rem; font-size: 0.9rem; font-weight: 500;">
                شريحة {current_idx + 1} من {total_steps}
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with nav_col3:
        if current_idx < total_steps - 1:
            if st.button("التالي ➡️", use_container_width=True, key="btn_next_step"):
                # Basic validation for current step before going forward (optional)
                if step_id == "cover" and not sdata["cover_project_name"].strip():
                    st.error("الرجاء إدخال اسم المشروع للمتابعة")
                else:
                    st.session_state["structured_step_index"] += 1
                    st.rerun()
        else:
            st.markdown(
                """
                <div style="text-align: center; background: rgba(16, 185, 129, 0.1); color: var(--color-success); border: 1px solid var(--color-success); padding: 0.4rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.85rem; font-weight: bold; direction: rtl;">
                    🎉 وصلت للخطوة الأخيرة! يمكنك الآن توليد المقترح بالأسفل.
                </div>
                """, 
                unsafe_allow_html=True
            )
            
    return sdata
