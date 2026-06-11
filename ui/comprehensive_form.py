import streamlit as st

def render_comprehensive_form():
    if "structured_project_data" not in st.session_state:
        st.session_state["structured_project_data"] = {}
        
    # FORCE SYNC ALL W_ KEYS TO PREVENT MISSING DEFAULT VALUES
    for k, v in st.session_state.items():
        if k.startswith("w_"):
            real_key = k[2:]
            st.session_state["structured_project_data"][real_key] = v
            
    if "form_step" not in st.session_state:
        st.session_state["form_step"] = 1
        
    step = st.session_state["form_step"]
        
    def _get_val(k, default=""):
        return st.session_state["structured_project_data"].get(k, default)
        
    def _set_val(k):
        st.session_state["structured_project_data"][k] = st.session_state[f"w_{k}"]

    def _get_idx(options, val):
        return options.index(val) if val in options else 0

    if not st.session_state.get("show_chat"):
        st.markdown("### نموذج بيانات المشروع الشامل")
        st.progress(step / 13.0)
        st.markdown(
            f"""
            <div style='text-align: left; color: #8e918f; font-size: 0.9rem; margin-bottom: 1rem;'>
                الخطوة {step} من 13
            </div>
            """,
            unsafe_allow_html=True
        )

    # 1. الغلاف
    if step == 1:
        st.markdown("#### 1. الغلاف")
        
        # --- QUICK FILL BUTTONS FOR TESTING ---
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 تعبئة تجريبية (سيناريو أفق الرياض)", use_container_width=True):
                demo_data = {
                    "cover_project_name": "برج أفق الرياض الأيقوني (Riyadh Horizon Apex)",
                    "cover_project_type": "مشروع استثماري مختلط",
                    "cover_location": "الرياض، تقاطع طريق الملك فهد مع التحلية",
                    "cover_client_name": "صندوق الاستثمارات الجريئة المحدود",
                    "cover_date": "2026-06-03",
                    "intro_client_name": "شركة أفق التنمية للتطوير العقاري",
                    "intro_brief_desc": "ناطحة سحاب بارتفاع 65 طابقاً، بتصميم بيوميمتيك، تضم مركزاً تجارياً، مكاتب بانورامية، وفندق 5 نجوم.",
                    "intro_goal": "تحديد أفضل بديل تطويري",
                    "intro_plot_number": "قطعة 442A - مخطط 3392/أ",
                    "intro_location_details": "الرياض / العليا / واجهة شرقية طريق الملك فهد",
                    "intro_land_area": "14,500 متر مربع",
                    "exec_project_type": "متعدد الاستخدامات",
                    "exec_components": ["تجاري", "إداري", "فندقي"],
                    "exec_built_area": "185,000 متر مربع",
                    "exec_leasable_area": "112,000 متر مربع",
                    "exec_units_count": "45 معرضاً، 120 مكتباً، 250 غرفة فندقية",
                    "exec_duration": "48 شهراً تنفيذ + 6 أشهر تشغيل",
                    "exec_exit_strategy": "تطوير وتشغيل ثم تخارج",
                    "exec_financial_indicators": "تكلفة تطوير 1.8 مليار ريال، عائد استثماري (IRR) بنسبة 16.5%، فترة استرداد 8.5 سنوات.",
                    "site_desc": "أرض ركنية مميزة ذات واجهة 120 متراً على الشريان الرئيسي، محاطة بأبراج شاهقة وتتميز ببروز بصري استثنائي.",
                    "site_streets": "شرقاً: طريق الملك فهد (80م)، غرباً: شارع العليا (40م).",
                    "site_accessibility": "جيدة",
                    "site_entrances": "مدخل رئيسي فاخر من طريق الملك فهد، ومدخل خلفي خاص من شارع العليا.",
                    "site_traffic_level": "عالية",
                    "site_traffic_notes": "اختناقات مرورية عالية من 4 عصراً، يتطلب تصميم حارة تباطؤ هندسية.",
                    "site_strengths": "الرؤية البصرية، القوة الشرائية العالية، قربه من المركز المالي.",
                    "site_challenges": "صعوبة الحفر العميق لوجود مياه جوفية قريبة.",
                    "surr_landmarks": "برج الفيصلية، فندق نارسيس، مستشفى الحبيب.",
                    "surr_landmark_type": ["مولات", "فنادق", "مستشفيات"],
                    "surr_landmark_direction": "جنوب",
                    "near_landmarks": "مركز الملك عبدالله المالي، مطار الملك خالد، محطة مترو العليا.",
                    "near_travel_time": "المالي 15 دقيقة، المطار 30 دقيقة، المترو 3 دقائق.",
                    "near_landmark_type": "محطة نقل",
                    "char_plot_map": "3392/أ",
                    "char_plot_num": "442A",
                    "char_building_sys": "معامل البناء 12، تغطية الأرض 60%، ارتدادات 10 متر.",
                    "char_shape": "غير منتظم",
                    "char_levels": "متفاوتة",
                    "char_infrastructure": ["مياه", "كهرباء", "طرق قائمة", "اتصالات"],
                    "char_additional_notes": "انحدار 2.5 متر من الشرق للغرب يسمح بعمل ميزانين شبه أرضي.",
                    "site_images_direction": "شرق",
                    "site_images_desc": "أرض فضاء تظهر طبوغرافية مائلة مع أبراج زجاجية محيطة، وصخور جيرية بارزة.",
                    "visit_date": "2026-06-01",
                    "visit_observations": "كابلات ضغط عالي تحت الأرض تحتاج ترحيل، واكتظاظ مواقف السيارات حول الموقع.",
                    "visit_observation_type": "بنية تحتية",
                    "visit_impact_level": "عالي",
                    "brands_names": "رولكس، لويس فويتون، فورسيزونز.",
                    "brands_activity": ["مطاعم ومقاهي", "تجزئة"],
                    "brands_notes": "سيطرة واضحة للعلامات الفاخرة، ما يحتم استهداف شريحة النخبة.",
                    "dev_options_count": "ثلاثة بدائل",
                    "dev_opt1_name": "أيقونة التجزئة والفندقة",
                    "dev_opt1_desc": "بوديوم تجاري 3 أدوار وبرج فندقي 50 دور. مساحة مبنية 115,000م2. مخاطر تشغيلية عالية.",
                    "dev_opt2_name": "المجمع المكتبي المؤسسي",
                    "dev_opt2_desc": "مكاتب فقط فئة A. مساحة مبنية 120,000م2. مخاطر أقل وعقود طويلة الأجل.",
                    "dev_opt3_name": "التطوير المدمج الذكي",
                    "dev_opt3_desc": "بوديوم تجاري فاخر، برج مكتبي 30 طابقاً، وبرج فندقي 20 طابقاً. مساحة مبنية 185,000م2.",
                    "dev_recommended": "البديل الثالث",
                    "dev_recommendation_reason": "أفضل استغلال للموقع",
                    "similar_proj_name": "واجهة الرياض، برج المملكة.",
                    "similar_proj_desc": "نجحت في دمج المكاتب مع التجزئة الفاخرة وخلق وجهة متكاملة.",
                    "similar_proj_lessons": "أهمية فصل مداخل الفندق عن المكاتب، وتوفير ساحات خارجية مكيفة لتشجيع المشاة.",
                }
                st.session_state["structured_project_data"].update(demo_data)
                for k, v in demo_data.items():
                    st.session_state[f"w_{k}"] = v
                st.session_state["form_step"] = 13
                st.rerun()

        with col_btn2:
            if st.button("🚀 تعبئة تجريبية (سيناريو مشروع تركبلكس)", use_container_width=True):
                demo_data_tricomplex = {
                    "cover_project_name": "مشروع تركبلكس الخدمي المتكامل (Tricomplex Project)",
                    "cover_project_type": "مشروع استثماري مختلط",
                    "cover_location": "جدة، طريق الملك فيصل - حي الضاحية",
                    "cover_client_name": "شركة تركبلكس للاستثمار العقاري",
                    "cover_date": "2026-06-06",
                    "intro_client_name": "شركة تركبلكس للاستثمار العقاري",
                    "intro_brief_desc": "تطوير مشروع خدمي متكامل يدمج ورش الشاحنات، المعارض التجارية، وسكن العمالة على أرض بمساحة 20,583.93 متر مربع.",
                    "intro_goal": "دراسة جدوى أولية",
                    "intro_plot_number": "قطعة رقم 12 - مخطط حي الضاحية",
                    "intro_location_details": "جدة / حي الضاحية / طريق الملك فيصل",
                    "intro_land_area": "20,583.93 متر مربع",
                    "exec_project_type": "متعدد الاستخدامات",
                    "exec_components": ["تجاري", "سكني", "أخرى"],
                    "exec_built_area": "12,515 متر مربع",
                    "exec_leasable_area": "19,796 متر مربع",
                    "exec_units_count": "معارض تجارية، ورش صيانة، سكن عمالة متكامل",
                    "exec_duration": "سنة تطوير + 4 سنوات تشغيل",
                    "exec_exit_strategy": "تطوير وتشغيل ثم تخارج",
                    "exec_financial_indicators": "تكلفة إجمالية 74.58 مليون ريال، إيراد سنوي متوقع 10 مليون ريال، صافي ربح سنوي 8.7 مليون ريال، قيمة تخارج 116 مليون ريال بعائد 15%-18%.",
                    "site_desc": "أرض فضاء تقع في منطقة حيوية ومناسبة للأنشطة الخدمية واللوجستية.",
                    "site_streets": "طريق الملك فيصل الرئيسي",
                    "site_accessibility": "ممتازة",
                    "site_entrances": "مدخل مباشر ومخارج ميسرة للشاحنات من طريق الملك فيصل.",
                    "site_traffic_level": "عالية",
                    "site_traffic_notes": "حركة شاحنات مستمرة ونشطة طوال اليوم.",
                    "site_strengths": "الموقع الاستراتيجي على طريق الملك فيصل الرئيسي، وتوفر سكن العمال والخدمات في نفس الموقع.",
                    "site_challenges": "تنظيم حركة دخول وخروج المركبات الكبيرة دون تعليق الحركة المرورية.",
                    "surr_landmarks": "محطات وقود، معارض سيارات، مناطق لوجستية.",
                    "surr_landmark_type": ["معارض سيارات", "محطات نقل"],
                    "surr_landmark_direction": "شمال",
                    "near_landmarks": "ميناء جدة الإسلامي، طريق الحرمين.",
                    "near_travel_time": "الميناء 20 دقيقة، طريق الحرمين 10 دقائق.",
                    "near_landmark_type": "طريق رئيسي",
                    "char_plot_map": "مخطط الضاحية",
                    "char_plot_num": "12",
                    "char_building_sys": "نسبة البناء 38%، الارتدادات والارتفاعات نظام البلدية المعتمد.",
                    "char_shape": "منتظم",
                    "char_levels": "متساوية",
                    "char_infrastructure": ["مياه", "كهرباء", "طرق قائمة", "اتصالات"],
                    "char_additional_notes": "طبوغرافية الأرض مستوية تماماً وصالحة للبناء الفوري دون تسويات مكلفة.",
                    "site_images_direction": "جنوب شرق",
                    "site_images_desc": "صورة تظهر الأرض المستوية ممتدة بمحاذاة طريق الملك فيصل.",
                    "visit_date": "2026-06-05",
                    "visit_observations": "توفر التوصيلات الخدمية الرئيسية على حدود الأرض مباشرة.",
                    "visit_observation_type": "بنية تحتية",
                    "visit_impact_level": "منخفض",
                    "brands_names": "أرامكو، ايسوزو، مرسيدس للشاحنات.",
                    "brands_activity": ["صيانة سيارات", "قطع غيار"],
                    "brands_notes": "المنطقة محاطة بوكالات سيارات ومراكز صيانة كبرى.",
                    "dev_options_count": "بديل واحد",
                    "dev_opt1_name": "مشروع تركبلكس الخدمي المدمج",
                    "dev_opt1_desc": "تطوير معارض تجارية أرضية ثنائية الأدوار بمساحة تأجيرية 1,780 م2، ورش صيانة شاحنات بمساحة تأجيرية 14,100 م2، ومجمع سكن عمالة بمساحة تأجيرية 3,900 م2.",
                    "dev_recommended": "البديل الأول",
                    "dev_recommendation_reason": "أفضل استغلال للموقع",
                    "similar_proj_name": "مجمع الخدمات اللوجستية، المدينة الصناعية.",
                    "similar_proj_desc": "مشاريع حققت نجاحاً كبيراً عبر توفير سكن العمال بجانب ورش الصيانة لتقليل كلفة النقل.",
                    "similar_proj_lessons": "ضرورة الاهتمام بنظام عزل الصوت والتهوية الجيدة لسكن العمال لقربه من الورش.",
                }
                st.session_state["structured_project_data"].update(demo_data_tricomplex)
                for k, v in demo_data_tricomplex.items():
                    st.session_state[f"w_{k}"] = v
                st.session_state["form_step"] = 13
                st.rerun()
        # -------------------------------------
        # -------------------------------------
        
        st.text_input("اسم الدراسة / المشروع", value=_get_val("cover_project_name"), key="w_cover_project_name", on_change=_set_val, args=("cover_project_name",))
        
        proj_types = ["تجاري", "إداري", "تجاري إداري", "سكني", "فندقي", "ضيافة", "متعدد الاستخدامات", "تجزئة", "معارض", "مكاتب", "طبي", "تعليمي", "ترفيهي", "مطاعم ومقاهي", "لوجستي", "مستودعات", "صناعي خفيف", "مواقف سيارات", "محطة خدمات", "مجمع أعمال", "مركز تجاري", "بوليفارد تجاري", "مشروع واجهة طريق", "مشروع استثماري مختلط", "أخرى"]
        st.selectbox("نوع المشروع", options=proj_types, index=_get_idx(proj_types, _get_val("cover_project_type", "تجاري")), key="w_cover_project_type", on_change=_set_val, args=("cover_project_type",))
        st.text_input("نوع مشروع آخر (إن وجد)", value=_get_val("cover_project_type_custom"), key="w_cover_project_type_custom", on_change=_set_val, args=("cover_project_type_custom",))
        
        st.text_input("موقع المشروع", value=_get_val("cover_location"), key="w_cover_location", on_change=_set_val, args=("cover_location",))
        st.text_input("اسم الجهة المالكة / العميل", value=_get_val("cover_client_name"), key="w_cover_client_name", on_change=_set_val, args=("cover_client_name",))
        st.text_input("تاريخ الإصدار", value=_get_val("cover_date"), key="w_cover_date", on_change=_set_val, args=("cover_date",))

    # 2. المقدمة
    elif step == 2:
        st.markdown("#### 2. المقدمة")
        st.text_input("اسم العميل", value=_get_val("intro_client_name"), key="w_intro_client_name", on_change=_set_val, args=("intro_client_name",))
        st.text_area("وصف مختصر للمشروع", value=_get_val("intro_brief_desc"), key="w_intro_brief_desc", on_change=_set_val, args=("intro_brief_desc",))
        
        goals = ["دراسة جدوى أولية", "تقييم فرصة استثمارية", "تحديد أفضل بديل تطويري", "تحليل موقع", "عرض استثماري", "أخرى"]
        st.selectbox("الهدف من الدراسة", options=goals, index=_get_idx(goals, _get_val("intro_goal", "دراسة جدوى أولية")), key="w_intro_goal", on_change=_set_val, args=("intro_goal",))
        st.text_input("هدف آخر (إن وجد)", value=_get_val("intro_goal_custom"), key="w_intro_goal_custom", on_change=_set_val, args=("intro_goal_custom",))
        
        st.text_input("رقم الأرض / رقم المخطط", value=_get_val("intro_plot_number"), key="w_intro_plot_number", on_change=_set_val, args=("intro_plot_number",))
        st.text_input("المدينة / الحي / الشارع", value=_get_val("intro_location_details"), key="w_intro_location_details", on_change=_set_val, args=("intro_location_details",))
        st.text_input("مساحة الأرض", value=_get_val("intro_land_area"), key="w_intro_land_area", on_change=_set_val, args=("intro_land_area",))

    # 3. الملخص التنفيذي
    elif step == 3:
        st.markdown("#### 3. الملخص التنفيذي")
        proj_types = ["تجاري", "إداري", "تجاري إداري", "سكني", "فندقي", "ضيافة", "متعدد الاستخدامات", "أخرى"]
        st.selectbox("نوع المشروع المقترح", options=proj_types, index=_get_idx(proj_types, _get_val("exec_project_type", "تجاري")), key="w_exec_project_type", on_change=_set_val, args=("exec_project_type",))
        st.multiselect("مكونات المشروع", options=proj_types, default=_get_val("exec_components", []), key="w_exec_components", on_change=_set_val, args=("exec_components",))
        st.text_input("مكونات أخرى (إن وجدت)", value=_get_val("exec_components_custom"), key="w_exec_components_custom", on_change=_set_val, args=("exec_components_custom",))
        
        st.text_input("مساحة الأرض (م2)", value=_get_val("exec_land_area"), key="w_exec_land_area", on_change=_set_val, args=("exec_land_area",))
        st.text_input("المساحة المبنية", value=_get_val("exec_built_area"), key="w_exec_built_area", on_change=_set_val, args=("exec_built_area",))
        st.text_input("المساحة التأجيرية", value=_get_val("exec_leasable_area"), key="w_exec_leasable_area", on_change=_set_val, args=("exec_leasable_area",))
        st.text_input("عدد الوحدات", value=_get_val("exec_units_count"), key="w_exec_units_count", on_change=_set_val, args=("exec_units_count",))
        st.text_input("مدة التطوير والتشغيل", value=_get_val("exec_duration"), key="w_exec_duration", on_change=_set_val, args=("exec_duration",))
        
        exits = ["تطوير ثم بيع", "تطوير وتشغيل", "تطوير وتشغيل ثم تخارج", "احتفاظ طويل الأجل"]
        st.selectbox("استراتيجية التخارج", options=exits, index=_get_idx(exits, _get_val("exec_exit_strategy", exits[0])), key="w_exec_exit_strategy", on_change=_set_val, args=("exec_exit_strategy",))
        st.text_area("أبرز المؤشرات المالية", value=_get_val("exec_financial_indicators"), key="w_exec_financial_indicators", on_change=_set_val, args=("exec_financial_indicators",))

    # 4. تحليل الموقع
    elif step == 4:
        st.markdown("#### 4. تحليل الموقع")
        st.text_area("وصف موقع الأرض", value=_get_val("site_desc"), key="w_site_desc", on_change=_set_val, args=("site_desc",))
        st.text_input("الشوارع المحيطة", value=_get_val("site_streets"), key="w_site_streets", on_change=_set_val, args=("site_streets",))
        
        access_opts = ["ممتازة", "جيدة", "متوسطة", "محدودة"]
        st.selectbox("سهولة الوصول للموقع", options=access_opts, index=_get_idx(access_opts, _get_val("site_accessibility", access_opts[0])), key="w_site_accessibility", on_change=_set_val, args=("site_accessibility",))
        
        st.text_input("المداخل والمخارج", value=_get_val("site_entrances"), key="w_site_entrances", on_change=_set_val, args=("site_entrances",))
        
        traffic_opts = ["عالية", "متوسطة", "منخفضة"]
        st.selectbox("مستوى الحركة المرورية", options=traffic_opts, index=_get_idx(traffic_opts, _get_val("site_traffic_level", traffic_opts[0])), key="w_site_traffic_level", on_change=_set_val, args=("site_traffic_level",))
        
        st.text_area("الملاحظات المرورية", value=_get_val("site_traffic_notes"), key="w_site_traffic_notes", on_change=_set_val, args=("site_traffic_notes",))
        st.text_area("مميزات الموقع", value=_get_val("site_strengths"), key="w_site_strengths", on_change=_set_val, args=("site_strengths",))
        st.text_area("تحديات الموقع", value=_get_val("site_challenges"), key="w_site_challenges", on_change=_set_val, args=("site_challenges",))

    # 5. المعالم المحيطة
    elif step == 5:
        st.markdown("#### 5. المعالم المحيطة")
        st.text_area("أسماء المعالم التجارية أو الخدمية حول الموقع", value=_get_val("surr_landmarks"), key="w_surr_landmarks", on_change=_set_val, args=("surr_landmarks",))
        
        lm_types = ["مولات", "مستشفيات", "معارض سيارات", "بنوك", "مطاعم ومقاهي", "فنادق", "مراكز معارض", "محطات نقل"]
        st.multiselect("نوع المعالم", options=lm_types, default=_get_val("surr_landmark_type", []), key="w_surr_landmark_type", on_change=_set_val, args=("surr_landmark_type",))
        
        dirs = ["شمال", "جنوب", "شرق", "غرب", "شمال شرق", "شمال غرب", "جنوب شرق", "جنوب غرب"]
        st.selectbox("موقع كل معلم بالنسبة للأرض (الاتجاه الغالب)", options=dirs, index=_get_idx(dirs, _get_val("surr_landmark_direction", dirs[0])), key="w_surr_landmark_direction", on_change=_set_val, args=("surr_landmark_direction",))

    # 6. المعالم القريبة
    elif step == 6:
        st.markdown("#### 6. المعالم القريبة")
        st.text_area("أسماء أهم المعالم القريبة", value=_get_val("near_landmarks"), key="w_near_landmarks", on_change=_set_val, args=("near_landmarks",))
        st.text_input("مدة الوصول لكل معلم", value=_get_val("near_travel_time"), key="w_near_travel_time", on_change=_set_val, args=("near_travel_time",))
        
        n_lm_types = ["مطار", "مستشفى", "مركز تجاري", "مركز معارض", "مشروع تطويري", "طريق رئيسي", "محطة نقل"]
        st.selectbox("نوع المعلم الأبرز", options=n_lm_types, index=_get_idx(n_lm_types, _get_val("near_landmark_type", n_lm_types[0])), key="w_near_landmark_type", on_change=_set_val, args=("near_landmark_type",))

    # 7. خصائص الموقع
    elif step == 7:
        st.markdown("#### 7. خصائص الموقع")
        st.text_input("رقم المخطط", value=_get_val("char_plot_map"), key="w_char_plot_map", on_change=_set_val, args=("char_plot_map",))
        st.text_input("رقم القطعة", value=_get_val("char_plot_num"), key="w_char_plot_num", on_change=_set_val, args=("char_plot_num",))
        st.text_input("نظام البناء (ارتفاعات، ارتدادات)", value=_get_val("char_building_sys"), key="w_char_building_sys", on_change=_set_val, args=("char_building_sys",))
        
        shapes = ["منتظم", "غير منتظم"]
        st.selectbox("شكل الأرض", options=shapes, index=_get_idx(shapes, _get_val("char_shape", shapes[0])), key="w_char_shape", on_change=_set_val, args=("char_shape",))
        
        levels = ["متساوية", "متفاوتة", "مرتفعة عن الشارع", "منخفضة عن الشارع"]
        st.selectbox("المناسيب", options=levels, index=_get_idx(levels, _get_val("char_levels", levels[0])), key="w_char_levels", on_change=_set_val, args=("char_levels",))
        
        infras = ["مياه", "كهرباء", "صرف صحي", "اتصالات", "طرق قائمة"]
        st.multiselect("توفر البنية التحتية", options=infras, default=_get_val("char_infrastructure", []), key="w_char_infrastructure", on_change=_set_val, args=("char_infrastructure",))
        
        st.text_area("ملاحظات إضافية على الأرض", value=_get_val("char_additional_notes"), key="w_char_additional_notes", on_change=_set_val, args=("char_additional_notes",))

    # 8. صور الموقع
    elif step == 8:
        st.markdown("#### 8. صور الموقع")
        dirs = ["شمال", "جنوب", "شرق", "غرب", "شمال شرق", "شمال غرب", "جنوب شرق", "جنوب غرب"]
        st.selectbox("اتجاه كل صورة (الغالب)", options=dirs, index=_get_idx(dirs, _get_val("site_images_direction", dirs[0])), key="w_site_images_direction", on_change=_set_val, args=("site_images_direction",))
        st.text_area("وصف كل صورة", value=_get_val("site_images_desc"), key="w_site_images_desc", on_change=_set_val, args=("site_images_desc",))

    # 9. ملاحظات الزيارات الميدانية
    elif step == 9:
        st.markdown("#### 9. ملاحظات الزيارات الميدانية")
        st.text_input("تاريخ الزيارة الميدانية", value=_get_val("visit_date"), key="w_visit_date", on_change=_set_val, args=("visit_date",))
        st.text_area("أبرز الملاحظات المرصودة", value=_get_val("visit_observations"), key="w_visit_observations", on_change=_set_val, args=("visit_observations",))
        
        obs_types = ["حركة مرورية", "بنية تحتية", "مناسيب الأرض", "عوائق بالموقع", "لوحات إعلانية", "مبان مجاورة", "مداخل ومخارج", "ملاحظات بيئية"]
        st.selectbox("نوع الملاحظة الغالب", options=obs_types, index=_get_idx(obs_types, _get_val("visit_observation_type", obs_types[0])), key="w_visit_observation_type", on_change=_set_val, args=("visit_observation_type",))
        
        impacts = ["عالي", "متوسط", "منخفض"]
        st.selectbox("مستوى الأثر على المشروع", options=impacts, index=_get_idx(impacts, _get_val("visit_impact_level", impacts[0])), key="w_visit_impact_level", on_change=_set_val, args=("visit_impact_level",))

    # 10. أبرز العلامات التجارية بمنطقة العقار
    elif step == 10:
        st.markdown("#### 10. العلامات التجارية المحيطة")
        st.text_area("أسماء العلامات التجارية القريبة", value=_get_val("brands_names"), key="w_brands_names", on_change=_set_val, args=("brands_names",))
        
        brand_acts = ["معارض سيارات", "صيانة سيارات", "قطع غيار", "مطاعم ومقاهي", "بنوك", "مواد بناء", "أجهزة ومعدات", "ترفيه", "تجزئة"]
        st.multiselect("تصنيف الأنشطة الموجودة", options=brand_acts, default=_get_val("brands_activity", []), key="w_brands_activity", on_change=_set_val, args=("brands_activity",))
        
        st.text_area("ملاحظات على طبيعة النشاط التجاري المحيط", value=_get_val("brands_notes"), key="w_brands_notes", on_change=_set_val, args=("brands_notes",))

    # 11. بدائل التطوير
    elif step == 11:
        st.markdown("#### 11. بدائل التطوير")
        opt_counts = ["بديل واحد", "بديلين", "ثلاثة بدائل", "أربعة بدائل"]
        current_count = _get_val("dev_options_count", opt_counts[0])
        st.selectbox("كم عدد البدائل التي ترغب بدراستها؟", options=opt_counts, index=_get_idx(opt_counts, current_count), key="w_dev_options_count", on_change=_set_val, args=("dev_options_count",))
        
        # We need to get the latest value again in case the selectbox just changed it and re-ran
        # But wait, the `w_dev_options_count` goes to state, then `_set_val` copies it. 
        # Actually, Streamlit will rerun and `_get_val` will have the correct value.
        current_count = _get_val("dev_options_count", opt_counts[0])
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("اسم البديل الأول", value=_get_val("dev_opt1_name"), key="w_dev_opt1_name", on_change=_set_val, args=("dev_opt1_name",))
            st.text_area("وصف وعناصر البديل الأول", value=_get_val("dev_opt1_desc"), key="w_dev_opt1_desc", on_change=_set_val, args=("dev_opt1_desc",))
            
        if current_count in ["بديلين", "ثلاثة بدائل", "أربعة بدائل"]:
            with col2:
                st.text_input("اسم البديل الثاني", value=_get_val("dev_opt2_name"), key="w_dev_opt2_name", on_change=_set_val, args=("dev_opt2_name",))
                st.text_area("وصف وعناصر البديل الثاني", value=_get_val("dev_opt2_desc"), key="w_dev_opt2_desc", on_change=_set_val, args=("dev_opt2_desc",))
                
        if current_count in ["ثلاثة بدائل", "أربعة بدائل"]:
            col3, col4 = st.columns(2)
            with col3:
                st.text_input("اسم البديل الثالث", value=_get_val("dev_opt3_name"), key="w_dev_opt3_name", on_change=_set_val, args=("dev_opt3_name",))
                st.text_area("وصف وعناصر البديل الثالث", value=_get_val("dev_opt3_desc"), key="w_dev_opt3_desc", on_change=_set_val, args=("dev_opt3_desc",))
                
            if current_count == "أربعة بدائل":
                with col4:
                    st.text_input("اسم البديل الرابع", value=_get_val("dev_opt4_name"), key="w_dev_opt4_name", on_change=_set_val, args=("dev_opt4_name",))
                    st.text_area("وصف وعناصر البديل الرابع", value=_get_val("dev_opt4_desc"), key="w_dev_opt4_desc", on_change=_set_val, args=("dev_opt4_desc",))

        recs = ["البديل الأول", "البديل الثاني", "البديل الثالث", "البديل الرابع", "لم يتم التحديد بعد"]
        st.selectbox("البديل الموصى به", options=recs, index=_get_idx(recs, _get_val("dev_recommended", recs[0])), key="w_dev_recommended", on_change=_set_val, args=("dev_recommended",))
        
        reasons = ["أعلى عائد استثماري", "أفضل استغلال للموقع", "أقل تكلفة تطوير", "أسهل في التنفيذ", "أكثر ملاءمة للسوق", "أكثر مرونة في التأجير", "أخرى"]
        st.selectbox("سبب التوصية", options=reasons, index=_get_idx(reasons, _get_val("dev_recommendation_reason", reasons[0])), key="w_dev_recommendation_reason", on_change=_set_val, args=("dev_recommendation_reason",))
        st.text_input("سبب آخر (إن وجد)", value=_get_val("dev_recommendation_reason_custom"), key="w_dev_recommendation_reason_custom", on_change=_set_val, args=("dev_recommendation_reason_custom",))

    # 12. نماذج مشابهة
    elif step == 12:
        st.markdown("#### 12. نماذج مشابهة")
        st.text_area("أسماء مشاريع مشابهة ناجحة", value=_get_val("similar_proj_name"), key="w_similar_proj_name", on_change=_set_val, args=("similar_proj_name",))
        st.text_area("نبذة عن نجاحها", value=_get_val("similar_proj_desc"), key="w_similar_proj_desc", on_change=_set_val, args=("similar_proj_desc",))
        st.text_area("الدروس المستفادة لمشروعنا", value=_get_val("similar_proj_lessons"), key="w_similar_proj_lessons", on_change=_set_val, args=("similar_proj_lessons",))

    # 13. إضافات وملفات (Optional Chat)
    elif step == 13:
        if not st.session_state.get("show_chat"):
            st.markdown("#### 13. إضافات وملفات")
            st.info("هل لديك ملفات تود إرفاقها (مثل كراسة شروط أو دراسة جدوى) أو أية تفاصيل إضافية تود شرحها للذكاء الاصطناعي قبل المراجعة النهائية؟")

    if not st.session_state.get("show_chat"):
        st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Navigation Buttons
    if step < 13:
        col_prev, col_next = st.columns(2)
        with col_prev:
            if step > 1:
                if st.button("⬅️ السابق", use_container_width=True):
                    st.session_state["form_step"] = step - 1
                    st.rerun()
                    
        with col_next:
            if st.button("التالي ➡️", use_container_width=True, type="primary"):
                st.session_state["form_step"] = step + 1
                st.rerun()
    else:
        # Step 13 buttons
        if not st.session_state.get("show_chat"):
            col_no, col_yes = st.columns(2)
            with col_no:
                if st.button("لا، اكتفيت بالنموذج (انتقل للمراجعة)", use_container_width=True, type="primary"):
                    return True # Proceeds to generate
            with col_yes:
                if st.button("نعم، أريد التحدث أو إرفاق ملفات", use_container_width=True):
                    st.session_state["show_chat"] = True
                    st.rerun()
        else:
            return "SHOW_CHAT"
            
    return False
