import streamlit as st
import utils.state_manager as sm
from services.llm_service import generate_json
from prompts.content_prompts import generate_smart_review_prompt

def render_smart_review():
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); padding: 2rem; border-radius: 12px; margin-bottom: 2rem; text-align: center; border: 1px solid #e0e0e0;">
            <h2 style="color: #670D0C; margin-bottom: 0.5rem;">🤖 المراجعة الذكية للمدخلات</h2>
            <p style="color: #475569; font-size: 1.1rem;">يقوم المساعد الذكي بمراجعة بياناتك لضمان أعلى جودة ممكنة للعرض التقديمي.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    struct_data = sm.get_val("structured_project_data") or {}
    extracted_facts = st.session_state.get("extracted_facts", {})
    
    # 1. Fetch questions if not already fetched
    questions = sm.get_val("smart_review_questions")
    
    if questions is None:
        with st.spinner("⏳ جاري تحليل المدخلات واكتشاف النواقص الهامة..."):
            sys_p, usr_p = generate_smart_review_prompt(struct_data, extracted_facts)
            try:
                response = generate_json(sys_p, usr_p)
                # Ensure we got a list
                if isinstance(response, list):
                    questions = response
                elif isinstance(response, dict) and "questions" in response:
                    questions = response["questions"]
                else:
                    questions = []
                sm.set_val("smart_review_questions", questions)
                st.rerun()
                return
            except Exception as e:
                st.error(f"❌ فشل الاتصال بـ DeepSeek لمراجعة البيانات: {str(e)}")
                if st.button("🔄 إعادة المحاولة", use_container_width=True):
                    st.rerun()
                return
            
    # 2. Render questions
    if not questions or len(questions) == 0:
        st.success("🎉 جميع البيانات الأساسية مكتملة وممتازة! ننتقل الآن لبناء الهيكل...")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 متابعة وتوليد الهيكل", use_container_width=True, type="primary"):
                sm.set_stage("outline_review")
                st.rerun()
        return
        
    st.info(f"💡 وجدنا {len(questions)} تفاصيل هامة لم يتم توضيحها بالكامل. استكمالها سيرفع من احترافية العرض النهائي.")
    
    # Render form for missing questions
    with st.container(border=True):
        responses = {}
        for idx, q in enumerate(questions):
            field_key = q.get("field_key")
            question_text = q.get("question")
            options = q.get("options", [])
            
            st.markdown(f"**{idx+1}. {question_text}**")
            
            # We add an "أخرى (كتابة يدوية)" option
            extended_options = options + ["أخرى (كتابة يدوية)"]
            
            choice = st.radio("اختر الإجابة:", options=extended_options, key=f"sr_radio_{field_key}", label_visibility="collapsed")
            
            if choice == "أخرى (كتابة يدوية)":
                custom_val = st.text_input("اكتب إجابتك هنا:", key=f"sr_text_{field_key}")
                responses[field_key] = custom_val
            else:
                responses[field_key] = choice
                
            st.divider()
            
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ تأكيد الإجابات ومتابعة", use_container_width=True, type="primary"):
                # Update struct_data with new responses
                for k, v in responses.items():
                    if v and str(v).strip():
                        struct_data[k] = v
                sm.set_val("structured_project_data", struct_data)
                sm.set_stage("outline_review")
                st.rerun()
                
        with col2:
            if st.button("⏭️ تخطي المراجعة والمتابعة", use_container_width=True):
                sm.set_stage("outline_review")
                st.rerun()
