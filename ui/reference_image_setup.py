"""Reference Image Setup Stage – Interactive Building Coherence Locked Setup Page"""

import base64
import hashlib
import logging
import os
import streamlit as st

from config.settings import settings
from ui import i18n
from utils import state_manager as sm
from services.image_gen_service import (
    generate_image,
    get_project_image_key,
    get_project_reference_image,
    set_project_reference_image,
    _cache_disabled,
)
from services.gemini_service import generate_consistent_image_prompt, generate_initial_reference_prompt

logger = logging.getLogger(__name__)


def render_reference_image_setup():
    """Renders the gorgeous interactive architectural master reference builder page."""
    lang = i18n.get_lang()
    project_data = sm.get_project_data() or {}
    is_commercial = False
    for val in project_data.values():
        if isinstance(val, str) and any(kw in val.lower() for kw in [
            "تجاري", "إداري", "إداريه", "تجاريه", "مكتب", "برج", "عمارة", "مجمع", "مكاتب", "أبراج",
            "commercial", "office", "administrative", "tower", "complex", "building"
        ]):
            is_commercial = True
            break
    
    if not project_data:
        sm.set_stage("prompt")
        st.rerun()
        return

    project_image_key = get_project_image_key(project_data)
    
    # 1. Page Header
    st.markdown(
        f"""
        <div class="surface-card" style="text-align: center; padding: 2.5rem 1rem 1.5rem 1rem; margin-bottom: 2rem;">
          <div style="display: inline-block; padding: 0.25rem 1.2rem; border-radius: 999px; background: var(--color-primary-dim); color: var(--color-primary); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.75rem;">
            {"الخطوة 3: الهوية المعمارية الموحدة" if lang == "ar" else "Step 3: Unified Architectural Coherence"}
          </div>
          <h1 style="font-size: 2.2rem; margin-bottom: 0.75rem;">
            {"تحديد وتأكيد الصورة المرجعية للمبنى" if lang == "ar" else "Lock Project Reference Image"}
          </h1>
          <p style="color: var(--color-text-secondary); font-size: 1.05rem; max-width: 700px; margin: 0 auto; line-height: 1.6;">
            {"سيقوم الذكاء الاصطناعي بتوليد صورة الغلاف والواجهة المعمارية المعتمدة للمبنى أولاً. يمكنك مراجعتها، وإدخال أي تعديلات مطلوبة عليها بشكل متكرر. بمجرد موافقتك، سيتم تثبيت التصميم والمادة والأبعاد لاستخدامها بدقة في جميع الشرائح والخرائط والتقسيمات الداخلية اللاحقة." 
            if lang == "ar" else 
            "The AI will generate the approved architectural cover image first. You can review, adjust, and describe changes to refine it. Once approved, the building's geometry and style will be locked as the style reference for all subsequent slides, plans, and interiors."}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Setup project seed & default prompts
    project_seed = int(hashlib.sha256(project_image_key.encode("utf-8")).hexdigest()[:8], 16) % 1000000000
    
    # Initialise session state variables if not set
    if "ref_image_bytes" not in st.session_state:
        st.session_state["ref_image_bytes"] = get_project_reference_image(project_image_key)
        
    if "ref_image_prompt" not in st.session_state or any(u'\u0600' <= char <= u'\u06FF' for char in st.session_state.get("ref_image_prompt", "")):
        # Dynamically formulate a 100% custom visual description matching the client's inputs in English
        with st.spinner("جاري صياغة وصف هندسي دقيق للمبنى..." if lang == "ar" else "Composing architectural description..."):
            initial_prompt = generate_initial_reference_prompt(project_data)
        st.session_state["ref_image_prompt"] = initial_prompt
        
    if "ref_generation_error" not in st.session_state:
        st.session_state["ref_generation_error"] = None
        
    # Check if API Key has credit or fell back to Flux
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    has_credits = True # We'll check based on generation results
    
    # 3. Main layout Columns
    col_preview, col_controls = st.columns([6, 5], gap="large")
    
    with col_preview:
        st.markdown(
            f"""
            <div style="margin-bottom: 0.8rem; font-weight: 700; color: var(--color-text-primary); font-size: 1.05rem;">
                {"🖼️ معاينة تصميم المبنى المعتمد" if lang == "ar" else "🖼️ Building Architecture Preview"}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        preview_container = st.empty()
        
        # Render image or error state
        if st.session_state["ref_generation_error"]:
            preview_container.markdown(
                f"""
                <div style="border: 1px dashed var(--color-error); border-radius: var(--radius-md); padding: 3rem 1.5rem; text-align: center; background: rgba(239, 68, 68, 0.02);">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚠️</div>
                    <h4 style="color: var(--color-error); margin: 0 0 0.5rem 0;">{"تعذر الاتصال بالمحرك الرئيسي" if lang == "ar" else "Engine Connection Failed"}</h4>
                    <p style="color: var(--color-text-secondary); font-size: 0.85rem; line-height: 1.5;">{st.session_state["ref_generation_error"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif st.session_state["ref_image_bytes"]:
            # Display image in widescreen beauty
            b64_data = base64.b64encode(st.session_state["ref_image_bytes"]).decode("utf-8")
            
            # Show smart credit notice if fallback was used
            notice_html = ""
            if "Insufficient credits" in str(st.session_state.get("ref_generation_error", "")) or not api_key:
                notice_html = f"""
                <div style="margin-top: 1rem; padding: 0.75rem 1rem; border-radius: 8px; background: rgba(16, 185, 129, 0.08); border: 1px solid var(--color-success); font-size: 0.82rem; color: var(--color-success); line-height: 1.4; display: flex; align-items: center; gap: 0.5rem;">
                    <span>✨</span>
                    <span>{"تم تفعيل محرك Flux البديل بنجاح لتوفير صور عالية الدقة بدون رصيد!" if lang == "ar" else "Flux engine activated successfully to generate high-res images for free!"}</span>
                </div>
                """
            else:
                notice_html = f"""
                <div style="margin-top: 1rem; padding: 0.75rem 1rem; border-radius: 8px; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.3); font-size: 0.82rem; color: #3b82f6; line-height: 1.4; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🤖</span>
                    <span>{"تم التوليد بنجاح باستخدام GPT-5.4 Image 2 عبر OpenRouter" if lang == "ar" else "Generated successfully using GPT-5.4 Image 2 via OpenRouter"}</span>
                </div>
                """
                
            preview_container.markdown(
                f"""
                <div class="surface-card" style="padding: 0.5rem; border: 1px solid var(--color-border); border-radius: var(--radius-lg); overflow: hidden;">
                    <img src="data:image/png;base64,{b64_data}" style="width: 100%; height: auto; border-radius: var(--radius-md); object-fit: cover; box-shadow: var(--shadow-sm);">
                    {notice_html}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Widescreen luxury placeholder card for visual pre-generation stage
            preview_container.markdown(
                f"""
                <div class="surface-card" style="border: 2px dashed var(--color-border); border-radius: var(--radius-lg); padding: 5rem 2rem; text-align: center; background: rgba(255, 255, 255, 0.02);">
                    <div style="font-size: 4rem; margin-bottom: 1.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">🏗️</div>
                    <h3 style="margin: 0 0 0.75rem 0; font-size: 1.4rem; font-weight: 700;">
                        {"جاهز لبدء التوليد البصري للمشروع" if lang == "ar" else "Ready to Generate Project Visuals"}
                    </h3>
                    <p style="color: var(--color-text-secondary); font-size: 0.95rem; max-width: 440px; margin: 0 auto 1.5rem auto; line-height: 1.6;">
                        {"تمت صياغة وصف هندسي دقيق لمشروعك بواسطة manaf3. يرجى مراجعة وتعديل الوصف في اللوحة الجانبية، ثم انقر على زر 'ابدأ توليد الهوية البصرية' للبدء!" 
                        if lang == "ar" else 
                        "An engineering prompt has been generated by manaf3. Review and refine it on the right, then click 'Start Visual Generation' to begin!"}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col_controls:
        st.markdown(
            f"""
            <div style="margin-bottom: 0.8rem; font-weight: 700; color: var(--color-text-primary); font-size: 1.05rem;">
                {"⚙️ تخصيص وتعديل واجهة المبنى" if lang == "ar" else "⚙️ Refine & Customize Architecture"}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        with st.container(border=True):
            # Welcome editing notice
            st.markdown(
                f"""
                <div style="padding: 0.75rem 1rem; border-radius: var(--radius-md); background: var(--color-primary-dim); border-left: 4px solid var(--color-primary); font-size: 0.9rem; font-weight: 500; margin-bottom: 1.2rem; color: var(--color-primary);">
                    {"✍️ هذا هو الوصف الهندسي المقترح.. هل تود إضافة أي لمسات أخيرة؟" 
                    if lang == "ar" else 
                    "✍️ This is the suggested engineering prompt.. would you like to add any final touches?"}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Direct prompt editor text area
            active_prompt = st.text_area(
                "📝 الوصف الفني النشط للصورة المرجعية (Active Technical Prompt):" if lang == "ar" else "📝 Active Technical Prompt for Reference Image:",
                value=st.session_state["ref_image_prompt"],
                height=200,
                key="active_ref_prompt_input",
                help="يمكنك تعديل هذا النص الفني مباشرة وتفصيله للحصول على النمط والتصميم الدقيق للمشروع." if lang == "ar" else "You can directly edit and detail this technical text to achieve the exact visual style and design."
            )
            
            st.caption(
                "💡 سيقوم المحرك بتوليد أو تعديل الصورة المعمارية بناءً على هذا الوصف الفني بدقة."
                if lang == "ar" else
                "💡 The engine will generate or modify the architectural image based precisely on this technical prompt."
            )
            
            st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)

            if st.session_state["ref_image_bytes"] is None:
                # Widescreen Single Large Primary Button for starting the visual rendering
                if st.button("🚀 ابدأ توليد الهوية البصرية" if lang == "ar" else "🚀 Start Visual Generation", type="primary", use_container_width=True):
                    new_prompt = st.session_state.get("active_ref_prompt_input", "").strip()
                    if new_prompt:
                        st.session_state["ref_image_prompt"] = new_prompt
                        
                        with st.spinner("جاري رسم الهوية البصرية الأولى للمبنى..." if lang == "ar" else "Generating initial building design with AI..."):
                            try:
                                # Determine vacant land visual context if uploaded in step 1
                                initial_ref_bytes = None
                                docs_imgs = sm.get_val("docs_images") or []
                                if docs_imgs and isinstance(docs_imgs, list):
                                    first_img = docs_imgs[0]
                                    if isinstance(first_img, dict) and "base64" in first_img:
                                        try:
                                            initial_ref_bytes = base64.b64decode(first_img["base64"])
                                            logger.info("Using first uploaded vacant land photo as visual context for rendering.")
                                        except Exception as decode_err:
                                            logger.error("Failed to decode uploaded docs_image base64: %s", decode_err)

                                img_bytes = generate_image(
                                    prompt=new_prompt,
                                    reference_image=initial_ref_bytes,
                                    seed=project_seed,
                                    is_commercial=is_commercial,
                                    is_land_reference=(initial_ref_bytes is not None)
                                )
                                st.session_state["ref_image_bytes"] = img_bytes
                                st.session_state["ref_generation_error"] = None
                                st.toast("تم توليد الهوية البصرية بنجاح!" if lang == "ar" else "Visual model generated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.session_state["ref_generation_error"] = str(e)
                                st.rerun()
                    else:
                        st.warning("الرجاء كتابة أو تأكيد الوصف الفني للمشروع أولاً!" if lang == "ar" else "Please write or confirm the technical prompt first!")
            else:
                # Splitted buttons when image is already rendered (Regenerate vs Approve)
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🔄 إعادة التوليد والتعديل" if lang == "ar" else "🔄 Regenerate & Edit", type="secondary", use_container_width=True):
                        new_prompt = st.session_state.get("active_ref_prompt_input", "").strip()
                        if new_prompt:
                            st.session_state["ref_image_prompt"] = new_prompt
                            
                            with st.spinner("جاري تعديل الرسم المعماري للمبنى..." if lang == "ar" else "Updating building architectural model..."):
                                try:
                                    img_bytes = generate_image(
                                        prompt=new_prompt,
                                        reference_image=st.session_state["ref_image_bytes"],
                                        seed=project_seed,
                                        is_commercial=is_commercial,
                                        is_land_reference=False  # Because ref_image_bytes already has the architectural model, not land plot!
                                    )
                                    st.session_state["ref_image_bytes"] = img_bytes
                                    st.session_state["ref_generation_error"] = None
                                    st.toast("تم تعديل الرسم المرجعي بنجاح!" if lang == "ar" else "Reference image updated successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.session_state["ref_generation_error"] = str(e)
                                    st.rerun()
                        else:
                            st.warning("الرجاء كتابة الوصف الفني للصورة أولاً!" if lang == "ar" else "Please write the technical prompt first!")
                            
                with col_btn2:
                    if st.button("🤝 اعتماد التصميم والمتابعة" if lang == "ar" else "🤝 Approve & Proceed", type="primary", use_container_width=True):
                        if st.session_state["ref_image_bytes"]:
                            set_project_reference_image(project_image_key, st.session_state["ref_image_bytes"])
                            
                            # Clear old generation artifacts to ensure clean slate
                            sm.set_slides(None)
                            sm.set_images(None)
                            sm.set_pptx_path(None)
                            sm.set_pdf_path(None)
                            sm.set_val("clarifications", {})
                            # Save the approved prompt as the style signature so that subsequent generations are perfectly aligned
                            approved_prompt = st.session_state.get("active_ref_prompt_input", "").strip()
                            sm.set_val("style_signature", approved_prompt)
                            
                            sm.set_stage("generating")
                            
                            if "ref_image_bytes" in st.session_state:
                                del st.session_state["ref_image_bytes"]
                            if "ref_image_prompt" in st.session_state:
                                del st.session_state["ref_image_prompt"]
                            if "ref_generation_error" in st.session_state:
                                del st.session_state["ref_generation_error"]
                                
                            st.toast("تم اعتماد التصميم المرجعي للمشروع!" if lang == "ar" else "Architectural style approved!")
                            st.rerun()
                        else:
                            st.error("الرجاء توليد الصورة أولاً قبل الاعتماد" if lang == "ar" else "Please generate the image before approving")

    st.markdown("<hr style='margin: 2.5rem 0;'>", unsafe_allow_html=True)
    
    # 4. Step Actions / Navigation Footer
    c_back, c_empty, c_skip = st.columns([2, 5, 2])
    with c_back:
        if st.button("⬅️ الرجوع لتعديل الهيكل" if lang == "ar" else "⬅️ Back to Outline", use_container_width=True):
            sm.set_stage("outline_review")
            st.rerun()
            
    with c_skip:
        if st.button("تخطي والمتابعة تلقائياً ➡️" if lang == "ar" else "Skip & Auto-Pilot ➡️", use_container_width=True):
            # Clear old generation artifacts to ensure clean slate
            sm.set_slides(None)
            sm.set_images(None)
            sm.set_pptx_path(None)
            sm.set_pdf_path(None)
            sm.set_val("clarifications", {})
            sm.set_val("style_signature", None)
            
            sm.set_stage("generating")
            st.rerun()
