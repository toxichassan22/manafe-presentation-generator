import logging

import streamlit as st

import utils.state_manager as sm
from ui import i18n
from prompts.content_prompts import generate_outline_prompt
from services.llm_service import generate_json
from ui.components import render_outline_editor

logger = logging.getLogger(__name__)


def _coerce_outline_count(slides: list[dict], num_expected: int | str, lang: str) -> list[dict]:
    """Keep the generated outline exactly aligned with the requested slide count."""
    if str(num_expected).lower() == "auto":
        return slides
    
    num_expected = int(num_expected)
    slides = list(slides or [])[:num_expected]
    cover_topic = "Project Cover" if lang == "en" else "غلاف المشروع"
    desc_topic = "Project Description" if lang == "en" else "وصف المشروع"
    closing_topic = "Conclusion" if lang == "en" else "خاتمة"

    fallback = [
        {"slide_type": "cover", "topic": cover_topic, "requires_image": True, "image_prompt": "", "bullets": ""},
        {"slide_type": "standard", "topic": desc_topic, "requires_image": True, "image_prompt": "", "bullets": ""},
        {"slide_type": "closing", "topic": closing_topic, "requires_image": False, "image_prompt": "", "bullets": ""},
    ]
    while len(slides) < num_expected:
        source = fallback[min(len(slides), len(fallback) - 1)].copy()
        if len(slides) >= len(fallback):
            source = {
                "slide_type": "standard",
                "topic": f"تفاصيل إضافية {len(slides) + 1}" if lang == "ar" else f"Additional Details {len(slides) + 1}",
                "requires_image": False,
                "image_prompt": "",
                "bullets": "",
            }
        slides.append(source)
    return slides


def _render_skeleton(placeholder):
    html = '<div style="max-width:600px;margin:0 auto;">'
    for _ in range(3):
        html += '<div class="surface-card" style="height: 80px; animation: pulse 1.5s infinite; background: var(--color-surface-raised);"></div>'
    html += "</div><style>@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }</style>"
    placeholder.markdown(html, unsafe_allow_html=True)


def _generate_outline():
    skeleton_placeholder = st.empty()
    stream_placeholder = st.empty()
    _render_skeleton(skeleton_placeholder)

    project_data = sm.get_project_data() or {}
    structured_data = project_data.get("structured_project_data")
    
    # HARDCODE OUTLINE FOR COMPREHENSIVE FORM TO PREVENT AI HALLUCINATION
    if structured_data:
        fixed_outline = [
            {"slide_type": "cover", "topic": "الغلاف", "requires_image": True, "section": "cover"},
            {"slide_type": "standard", "topic": "المقدمة وأهداف الدراسة", "requires_image": False, "section": "introduction"},
            {"slide_type": "two_column", "topic": "الملخص التنفيذي", "requires_image": False, "section": "executive_summary"},
            {"slide_type": "two_column", "topic": "تحليل الموقع", "requires_image": False, "section": "site_analysis"},
            {"slide_type": "standard", "topic": "المعالم المحيطة", "requires_image": False, "section": "surrounding_landmarks"},
            {"slide_type": "timeline", "topic": "المعالم القريبة", "requires_image": False, "section": "nearby_landmarks"},
            {"slide_type": "two_column", "topic": "خصائص الموقع", "requires_image": False, "section": "site_characteristics"},
            {"slide_type": "standard", "topic": "صور الموقع", "requires_image": True, "section": "site_images"},
            {"slide_type": "standard", "topic": "ملاحظات الزيارات الميدانية", "requires_image": False, "section": "site_visits"},
            {"slide_type": "two_column", "topic": "العلامات التجارية المحيطة", "requires_image": False, "section": "key_brands"},
            {"slide_type": "chart", "topic": "بدائل التطوير المتاحة", "requires_image": False, "section": "development_options"},
            {"slide_type": "two_column", "topic": "نماذج مشابهة", "requires_image": False, "section": "similar_projects"}
        ]
        for s in fixed_outline:
            s["image_prompt"] = ""
            s["bullets"] = ""
        
        skeleton_placeholder.empty()
        stream_placeholder.empty()
        sm.set_val("outline", fixed_outline)
        st.rerun()
        return

    docs_text = sm.get("docs_text")
    docs_images = sm.get_val("docs_images") or []

    # Build rich context string
    context_parts = []
    if project_data.get("project_name"):
        context_parts.append(f"اسم المشروع: {project_data['project_name']}")
    if project_data.get("description"):
        context_parts.append(f"الوصف: {project_data['description']}")
    if project_data.get("floor_distribution"):
        context_parts.append(f"توزيع الأدوار: {project_data['floor_distribution']}")
    if project_data.get("image_style_description"):
        context_parts.append(f"شرح ونمط الصور المطلوبة: {project_data['image_style_description']}")
    if project_data.get("language"):
        context_parts.append(f"لغة العرض: {project_data['language']}")
    if docs_images:
        context_parts.append(f"عدد صور الأرض المرفوعة: {len(docs_images)} صورة")

    full_context = "\n".join(context_parts)
    if docs_text:
        truncated_docs = docs_text if len(docs_text) <= 10000 else (docs_text[:10000] + "\n... [تم اختصار النص المرجعي الطويل]")
        full_context += f"\n\n--- Reference documents ---\n{truncated_docs}"

    if not full_context.strip():
        full_context = "مشروع عقاري جديد"

    sys_p, usr_p = generate_outline_prompt(
        context_data=full_context,
        num_slides=project_data.get("num_slides", "Auto"),
    )

    # Slide-type icon map
    _TYPE_ICONS = {
        "cover": "🏠", "section_header": "📌", "standard": "📄",
        "two_column": "⚖️", "timeline": "🗓️", "swot": "🔍",
        "map": "📍", "chart": "📊", "closing": "🎯",
    }

    def _outline_stream_cb(raw_text):
        import re
        topics = re.findall(r'"topic"\s*:\s*"([^"]+)"', raw_text)
        types  = re.findall(r'"slide_type"\s*:\s*"([^"]+)"', raw_text)

        if not topics:
            # Still waiting for first topic — show a gentle pulse
            stream_placeholder.markdown(
                """
                <div style="max-width:600px;margin:0 auto;padding:1.5rem 0;text-align:center;">
                  <div style="display:inline-block;width:32px;height:32px;border:3px solid var(--color-primary);
                              border-top-color:transparent;border-radius:50%;
                              animation:spin 0.9s linear infinite;"></div>
                  <p style="color:var(--color-text-tertiary);margin-top:0.75rem;font-size:0.9rem;">
                    جاري تحليل المشروع...
                  </p>
                  <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        num_expected = project_data.get("num_slides", "Auto")
        if str(num_expected).lower() == "auto":
            progress_pct = min(100, len(topics) * 8)
            expected_display = "?"
        else:
            progress_pct = min(100, int(len(topics) / int(num_expected) * 100))
            expected_display = str(num_expected)

        rows_html = ""
        for i, topic in enumerate(topics):
            stype = types[i] if i < len(types) else "standard"
            icon  = _TYPE_ICONS.get(stype, "📄")
            is_last = (i == len(topics) - 1)

            cursor = (
                '<span style="display:inline-block;width:2px;height:1em;background:var(--color-primary);'
                'vertical-align:text-bottom;animation:blink 0.8s step-end infinite;margin-right:2px;"></span>'
                if is_last else ""
            )

            rows_html += f"""<div style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem 1rem;border-radius:10px;background:{'var(--color-surface-raised)' if is_last else 'transparent'};border:{'1px solid var(--color-primary)' if is_last else '1px solid transparent'};transition:all 0.3s ease;margin-bottom:0.35rem;">
  <span style="font-size:1.15rem;flex-shrink:0;">{icon}</span>
  <div style="flex:1;min-width:0;">
    <span style="font-size:0.72rem;color:var(--color-text-tertiary);font-weight:600;letter-spacing:0.05em;display:block;">
      {i18n.t("outline.slide_n")} {i + 1}
    </span>
    <span style="color:{'var(--color-primary)' if is_last else 'var(--color-text-primary)'};font-weight:{'700' if is_last else '500'};font-size:0.95rem;">
      {cursor}{topic}
    </span>
  </div>
</div>
"""

        html = f"""<div style="max-width:620px;margin:0 auto;">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
    <span style="font-weight:700;font-size:1rem;color:var(--color-text-primary);">
      {i18n.t("outline.suggested")}
    </span>
    <span style="font-size:0.8rem;color:var(--color-text-tertiary);">
      {len(topics)} / {expected_display} شريحة
    </span>
  </div>
  <!-- Progress bar -->
  <div style="height:4px;background:var(--color-border);border-radius:99px;margin-bottom:1.2rem;overflow:hidden;">
    <div style="height:100%;width:{progress_pct}%;background:linear-gradient(90deg,var(--color-primary),#e06060);border-radius:99px;transition:width 0.4s ease;"></div>
  </div>
  {rows_html}
  <style>
    @keyframes blink {{
      0%,100%{{opacity:1}} 50%{{opacity:0}}
    }}
  </style>
</div>"""
        stream_placeholder.markdown(html, unsafe_allow_html=True)

    try:
        # Pass images=None to avoid 400 Bad Request on text-only model moonshotai/Kimi-K2.6
        outline_res = generate_json(sys_p, usr_p, stream_callback=_outline_stream_cb, images=None)
        skeleton_placeholder.empty()
        stream_placeholder.empty()

        if isinstance(outline_res, dict) and "slides" in outline_res:
            slides = outline_res["slides"]
        elif isinstance(outline_res, list):
            slides = outline_res
        else:
            raise ValueError("Unexpected JSON format")

        if not slides:
            raise ValueError("No slides in outline")

        slides = _coerce_outline_count(slides, project_data.get("num_slides", "Auto"), i18n.get_lang())

        for s in slides:
            if "bullets" not in s:
                s["bullets"] = ""
            if "image_prompt" not in s:
                s["image_prompt"] = ""

        sm.set_val("outline", slides)
        st.rerun()
    except Exception as e:
        logger.error("Outline generation failed: %s", e, exc_info=True)
        skeleton_placeholder.empty()
        stream_placeholder.empty()
        st.session_state["outline_error"] = str(e)
        st.rerun()


def render_outline_stage():
    # Initialize session state error if not present
    if "outline_error" not in st.session_state:
        st.session_state["outline_error"] = None

    lang = i18n.get_lang()

    # If there is a pending error, display it with clean options
    if st.session_state["outline_error"]:
        error_msg = st.session_state["outline_error"]
        
        st.markdown(
            f"""
            <div class="surface-card" style="max-width: 650px; margin: 2rem auto; padding: 2.5rem 1.5rem; border: 1px solid var(--color-error); border-radius: var(--radius-md); text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                <h2 style="margin: 0 0 0.50rem 0; color: var(--color-error); font-size: 1.50rem; line-height: 1.5;">
                    {i18n.t("outline.error")}
                </h2>
                <p style="color: var(--color-text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem; max-width: 500px; margin-left: auto; margin-right: auto;">
                    {"يرجى التحقق من تفاصيل الخطأ أدناه وإعادة المحاولة، أو الانتقال مباشرة لتعديل الهيكل الافتراضي وبناء العرض يدوياً." 
                    if lang == "ar" else 
                    "Please check the error details below and retry, or directly edit the default structure to build your presentation manually."}
                </p>
                <div style="padding: 1rem; border-radius: 8px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.15); margin-bottom: 2rem; text-align: left; font-family: monospace; font-size: 0.85rem; color: var(--color-text-secondary); max-width: 100%; overflow-x: auto; direction: ltr;">
                    <strong>Error details:</strong> {error_msg}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            if st.button(i18n.t("outline.retry") or "إعادة المحاولة", type="primary", use_container_width=True):
                st.session_state["outline_error"] = None
                st.rerun()
                
            btn_text = "تعديل الهيكل الافتراضي / Edit Default Outline"
            if st.button(btn_text, type="secondary", use_container_width=True):
                st.session_state["outline_error"] = None
                cover_topic = "Project Cover" if lang == "en" else "غلاف المشروع"
                desc_topic = "Project Description" if lang == "en" else "وصف المشروع"
                closing_topic = "Conclusion" if lang == "en" else "خاتمة"
                sm.set_val(
                    "outline",
                    [
                        {"slide_type": "cover", "topic": cover_topic, "requires_image": True, "image_prompt": "", "bullets": ""},
                        {"slide_type": "standard", "topic": desc_topic, "requires_image": False, "image_prompt": "", "bullets": ""},
                        {"slide_type": "closing", "topic": closing_topic, "requires_image": False, "image_prompt": "", "bullets": ""},
                    ],
                )
                st.rerun()
        return

    # If outline is not yet generated, trigger generation after choosing the mode
    if not sm.get("outline"):
        if "outline_mode_chosen" not in st.session_state or st.session_state["outline_mode_chosen"] not in ["auto"]:
            st.session_state["outline_mode_chosen"] = None

        if st.session_state["outline_mode_chosen"] is None:
            st.markdown(
                f"""
                <div class="surface-card" style="text-align: center; padding: 2.5rem 1.5rem; margin-bottom: 2rem; border: 1px solid var(--color-border); border-radius: var(--radius-md);">
                  <span style="font-size: 3rem; display: block; margin-bottom: 0.75rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">📋</span>
                  <h2 style="font-size: 1.8rem; margin: 0 0 0.5rem 0; color: var(--color-text-primary);">
                    {"تخصيص هيكل العرض التقديمي" if lang == "ar" else "Customize Presentation Outline"}
                  </h2>
                  <p style="color: var(--color-text-secondary); font-size: 1rem; max-width: 600px; margin: 0 auto; line-height: 1.6;">
                    {"قبل البدء في بناء وتصميم العرض، يرجى تحديد نمط وهيكل الشرائح الذي تفضله لمشروعك:" 
                    if lang == "ar" else 
                    "Before building the presentation, please select the preferred slide structure pattern for your project:"}
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Two beautiful option columns
            col_auto, col_standard = st.columns(2, gap="large")

            with col_auto:
                st.markdown(
                    f"""
                    <div class="surface-card" style="text-align: center; height: 100%; border: 1px solid var(--color-border); padding: 2rem 1.5rem; border-radius: var(--radius-lg); transition: all 0.3s ease; box-shadow: var(--shadow-sm);">
                        <span style="font-size: 2.5rem; display: block; margin-bottom: 0.75rem;">🤖</span>
                        <h4 style="margin: 0 0 0.75rem 0; font-size: 1.2rem; color: var(--color-primary); font-weight: 700;">
                            {"توليد تلقائي ذكي بالذكاء الاصطناعي" if lang == "ar" else "Flexible AI Auto-Pilot"}
                        </h4>
                        <p style="font-size: 0.88rem; color: var(--color-text-secondary); line-height: 1.6; min-height: 90px; margin: 0 0 1.5rem 0;">
                            {"سيقوم الذكاء الاصطناعي بتحليل البيانات المستخلصة من المحادثة وصياغة هيكل وعدد شرائح مرن ومخصص يناسب مشروعك العقاري بالتفصيل."
                            if lang == "ar" else
                            "The AI analyzes gathered facts and designs a flexible, project-specific custom outline with slides matching your unique proposal details."}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("✨ تشغيل التوليد الذكي (AI Auto-Pilot)" if lang == "ar" else "✨ Run AI Auto-Pilot", use_container_width=True, type="primary", key="choose_auto_outline"):
                    st.session_state["outline_mode_chosen"] = "auto"
                    st.rerun()

            with col_standard:
                st.markdown(
                    f"""
                    <div class="surface-card" style="text-align: center; height: 100%; border: 1px solid var(--color-border); padding: 2rem 1.5rem; border-radius: var(--radius-lg); transition: all 0.3s ease; box-shadow: var(--shadow-sm);">
                        <span style="font-size: 2.5rem; display: block; margin-bottom: 0.75rem;">🏢</span>
                        <h4 style="margin: 0 0 0.75rem 0; font-size: 1.2rem; color: #c2a176; font-weight: 700;">
                            {"نموذج شركة منافع القياسي" if lang == "ar" else "Manafea Standard 12 Slides"}
                        </h4>
                        <p style="font-size: 0.88rem; color: var(--color-text-secondary); line-height: 1.6; min-height: 90px; margin: 0 0 1.5rem 0;">
                            {"التزام تام ودقيق بـ 12 شريحة احترافية مرتبة حسب الدليل القياسي لشركة منافع (غلاف، مقدمة، تحليل موقع، معالم، زيارات، بدائل، ومشاريع شبيهة)."
                            if lang == "ar" else
                            "Strictly adhere to the professional 12-slide layout defined by Manafea guidelines (Cover, Intro, Site Analysis, Landmarks, Visits, Alternatives, etc.)"}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("🏢 تطبيق النموذج القياسي (Manafea 12)" if lang == "ar" else "🏢 Apply Standard Model", use_container_width=True, type="secondary", key="choose_standard_outline"):
                    st.session_state["outline_mode_chosen"] = "standard"
                    # Populate the standard outline!
                    project_data = sm.get_project_data() or {}
                    project_name = project_data.get("project_name") or "مول منافع التجاري"
                    location = project_data.get("location") or "الرياض"
                    
                    if lang == "ar":
                        outline_slides = [
                            {"section": "cover", "slide_type": "cover", "topic": f"دراسة مقترح تطوير {project_name}", "requires_image": True, "image_prompt": f"Luxurious modern exterior architectural rendering of {project_name} at {location}, photorealistic, daytime, 8k", "bullets": f"{project_name}\nدراسة مقترح تطوير العقار\nالموقع: {location}\nتاريخ المقترح: مايو 2026"},
                            {"section": "introduction", "slide_type": "standard", "topic": "المقدمة والتمهيد الاستثماري", "requires_image": False, "image_prompt": "", "bullets": f"الهدف الرئيسي من دراسة تطوير الموقع\nسياق الفرصة العقارية في السوق لـ {project_name}\nالرؤية الاستثمارية والجمهور المستهدف"},
                            {"section": "executive_summary", "slide_type": "standard", "topic": "الملخص التنفيذي للمقترح العقاري", "requires_image": True, "image_prompt": "Beautiful sleek professional interior building lobby with gold accents, 8k architectural view", "bullets": f"المساحات التأجيرية والمبنية المستهدفة\nالمكونات الرئيسية المقترحة للتطوير لـ {project_name}\nمؤشرات الجدوى والأداء المالي الأولية للمستثمرين"},
                            {"section": "site_analysis", "slide_type": "standard", "topic": "تحليل الموقع الميداني وإمكانية الوصول", "requires_image": False, "image_prompt": "", "bullets": f"الشوارع المحيطة وواجهة الأرض الأساسية\nسهولة الوصول ومداخل ومخارج الموقع بـ {location}\nمستوى الحركة المرورية ومواقف السيارات"},
                            {"section": "surrounding_landmarks", "slide_type": "standard", "topic": "دراسة المعالم والأنشطة المحيطة بالأرض", "requires_image": False, "image_prompt": "", "bullets": "أبرز المعالم التجارية والخدمية المجاورة بالأحياء المحيطة\nالمشروعات الكبرى الجاري تطويرها بالمنطقة\nتأثير الجذب الجغرافي للمعالم على العقار"},
                            {"section": "nearby_landmarks", "slide_type": "standard", "topic": "المعالم الرئيسية للمدينة ومسافات الوصول", "requires_image": False, "image_prompt": "", "bullets": f"أهم معالم الجذب بالمدينة (مطار، مركز مالي، طرق محورية)\nأوقات ومسافات الوصول بالسيارة من موقع {project_name}\nالربط اللوجستي مع شبكة النقل العام"},
                            {"section": "site_characteristics", "slide_type": "standard", "topic": "خصائص الموقع الجغرافية ونظام البناء البلدية", "requires_image": False, "image_prompt": "", "bullets": "مساحة الأرض الرسمية والمخطط والقطع\nأنظمة البناء البلدية المعتمدة (الارتفاعات والنسب)\nطبيعة مناسيب الأرض وشكلها الجغرافي الميداني"},
                            {"section": "site_images", "slide_type": "standard", "topic": "صور ولقطات حية من الموقع الميداني", "requires_image": True, "image_prompt": "Real estate plot land in Riyadh, daytime sky, empty commercial construction site", "bullets": "لقطات توثيقية للأرض والواجهات المفتوحة\nاتجاهات التصوير المرصودة ميدانياً\nخلو الموقع من العوائق المادية القائمة"},
                            {"section": "site_visits", "slide_type": "standard", "topic": "ملاحظات وتوصيات الزيارة الميدانية", "requires_image": False, "image_prompt": "", "bullets": "تاريخ وأهداف الزيارة التفقدية للموقع الميداني\nالملاحظات والمؤشرات المرصودة على الطبيعة\nمدى تأثير نتائج المعاينة على خطة التطوير"},
                            {"section": "key_brands", "slide_type": "standard", "topic": "العلامات التجارية القائمة بمنطقة العقار", "requires_image": False, "image_prompt": "", "bullets": "البراندات والمتاجر والأنشطة المحيطة النشطة\nتقييم الجاذبية الاستثمارية للمنطقة التجارية\nتحديد فئات المستأجرين المستهدفين للمشروع"},
                            {"section": "development_options", "slide_type": "standard", "topic": "بدائل التطوير والمقترحات الاستثمارية", "requires_image": True, "image_prompt": f"Beautiful modern office building combined with retail stores, outdoor seating, daytime", "bullets": "عرض ومقارنة البدائل التقديرية لاستغلال الأرض\nتفاصيل البديل المعماري والاستثماري الموصى به\nمبررات التوصية وعوامل نجاح البديل المختار"},
                            {"section": "similar_projects", "slide_type": "closing", "topic": "النماذج المقارنة ودراسة الحالات المشابهة", "requires_image": False, "image_prompt": "", "bullets": f"أمثلة لمشروعات قائمة ناجحة مطبقة ذات الفكرة\nالدروس والفرص المستفادة من نماذج المقارنة لمشروع {project_name}\nأفضل الممارسات الموصى باتباعها بالتطوير"}
                        ]
                    else:
                        outline_slides = [
                            {"section": "cover", "slide_type": "cover", "topic": f"Development Proposal for {project_name}", "requires_image": True, "image_prompt": f"Luxurious modern exterior architectural rendering of {project_name} at {location}, photorealistic, daytime, 8k", "bullets": f"{project_name}\nDevelopment Proposal Study\nLocation: {location}\nProposal Date: May 2026"},
                            {"section": "introduction", "slide_type": "standard", "topic": "Introduction & Investment Context", "requires_image": False, "image_prompt": "", "bullets": f"Main objective of the site development study\nReal estate opportunity market context for {project_name}\nInvestment vision and target audience"},
                            {"section": "executive_summary", "slide_type": "standard", "topic": "Executive Summary & Major Components", "requires_image": True, "image_prompt": "Beautiful sleek professional interior building lobby with gold accents, 8k architectural view", "bullets": "Target gross leasable and built-up areas\nProposed core components for development\nPreliminary financial feasibility and performance indicators"},
                            {"section": "site_analysis", "slide_type": "standard", "topic": "Site Analysis & Accessibility", "requires_image": False, "image_prompt": "", "bullets": f"Surrounding streets and primary property facade\nEase of access, site entrances and exits at {location}\nTraffic levels and parking facilities"},
                            {"section": "surrounding_landmarks", "slide_type": "standard", "topic": "Surrounding Landmarks & Activities", "requires_image": False, "image_prompt": "", "bullets": "Key nearby commercial and service landmarks\nMajor development projects in the neighborhood\nInfluence of geographical landmarks on property attraction"},
                            {"section": "nearby_landmarks", "slide_type": "standard", "topic": "Key City Landmarks & Drive Times", "requires_image": False, "image_prompt": "", "bullets": f"Major city attractions (airport, KAFD, highways)\nDrive times and distances from {project_name} by car\nLogistic connectivity with the public transit network"},
                            {"section": "site_characteristics", "slide_type": "standard", "topic": "Site Characteristics & Zoning Regulations", "requires_image": False, "image_prompt": "", "bullets": "Official land area, block, and plot numbers\nApproved municipal zoning regulations (heights and ratios)\nNature of land levels and geographical shape"},
                            {"section": "site_images", "slide_type": "standard", "topic": "Site Images & Facade Layouts", "requires_image": True, "image_prompt": "Real estate plot land in Riyadh, daytime sky, empty commercial construction site", "bullets": "Documentary shots of the land and open facades\nField photography directions\nAbsence of existing physical obstacles on site"},
                            {"section": "site_visits", "slide_type": "standard", "topic": "Site Visit notes & Field Observations", "requires_image": False, "image_prompt": "", "bullets": "Date and objectives of the land inspection visit\nObservations and indicators noticed on site\nImpact of visit findings on the development plan"},
                            {"section": "key_brands", "slide_type": "standard", "topic": "Existing Brands in the Property Zone", "requires_image": False, "image_prompt": "", "bullets": "Nearby active brands, shops, and businesses\nAssessment of the commercial area's investment appeal\nTarget tenant profiles identified for the project"},
                            {"section": "development_options", "slide_type": "standard", "topic": "Development Alternatives & Recommendations", "requires_image": True, "image_prompt": "Beautiful modern office building combined with retail stores, outdoor seating, daytime", "bullets": "Presentation and comparison of land use options\nDetails of the recommended architectural and investment alternative\nRationales and key success factors of the chosen option"},
                            {"section": "similar_projects", "slide_type": "closing", "topic": "Comparative Case Studies & Benchmarks", "requires_image": False, "image_prompt": "", "bullets": f"Examples of successful operational projects of the same concept\nLessons and opportunities learned from case studies for {project_name}\nBest practices recommended for development execution"}
                        ]
                    sm.set_val("outline", outline_slides)
                    st.rerun()

            # Back button to return to prompt stage
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            if st.button("⬅️ العودة إلى المستشار الذكي (Back to Chat)" if lang == "ar" else "⬅️ Back to Chat Consultant", use_container_width=True):
                st.session_state["outline_mode_chosen"] = None
                sm.set_stage("prompt")
                st.rerun()
            return

        if st.session_state["outline_mode_chosen"] == "auto":
            st.markdown(
                f"""
                <div class="surface-card" style="text-align: center; padding:36px 24px; margin-bottom: 2rem;">
                  <h1 style="font-size:1.8rem; margin-bottom: 0.5rem;">{i18n.t("outline.generating_title")}</h1>
                  <p style="color: var(--color-text-secondary); font-size: 1.1rem;">{i18n.t("outline.generating_sub")}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.session_state["outline_mode_chosen"] = None
            _generate_outline()
            return

    outline = sm.get("outline")
    for card in outline:
        if "bullets" not in card:
            card["bullets"] = ""

    st.markdown(
        f"""
        <div style="max-width:720px;margin:0 auto 16px;">
          <p style="font-size:1.1rem;font-weight:700;color:var(--color-text-primary);margin:0;">{i18n.t("outline.card_title")}</p>
          <p style="font-size:0.88rem;color:var(--color-text-secondary);margin:6px 0 0;">{i18n.t("outline.card_desc")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    result = render_outline_editor(
        outline=outline,
        initial_density="concise",
        initial_theme="executive",
        lang=i18n.get_lang(),
        key=f"outline_editor_{i18n.get_lang()}",
    )

    if result is not None:
        action = result.get("action")
        if action == "generate":
            sm.set_val("outline", result["outline"])
            sm.set_val("density", result["density"])
            sm.set_val("theme", result["theme"])
            sm.set_val("image_settings", {"generate_images": True, "prompts": {}})
            # Clear previous slide contents and presentation paths for a fresh run
            sm.set_slides(None)
            sm.set_images(None)
            sm.set_val("clarifications", {})
            sm.set_pptx_path(None)
            sm.set_pdf_path(None)
            sm.set_stage("reference_image_setup")
            st.rerun()
        elif action == "back":
            sm.set_val("outline", None)
            sm.set_stage("prompt")
            st.rerun()
