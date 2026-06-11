import base64
import logging
import os
import sys
import subprocess
import streamlit as st

logger = logging.getLogger(__name__)

# Dynamic check and auto-install for huggingface_hub
try:
    from huggingface_hub import HfApi
except ImportError:
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub"], capture_output=True, check=True)
        from huggingface_hub import HfApi
    except Exception as e:
        logger.error("Failed to install huggingface_hub: %s", e)

from ui import i18n
from utils import state_manager as sm

def render_deploy_page():
    """Renders the gorgeous interactive Hugging Face Space Deployer."""
    lang = i18n.get_lang()
    
    st.markdown(
        f"""
        <div class="surface-card" style="text-align: center; padding: 2.5rem 1rem 1.5rem 1rem; margin-bottom: 2rem;">
          <div style="display: inline-block; padding: 0.25rem 1.2rem; border-radius: 999px; background: var(--color-primary-dim); color: var(--color-primary); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.75rem;">
            {"الرفع والتشغيل أونلاين" if lang == "ar" else "Deploy Online"}
          </div>
          <h1 style="font-size: 2.2rem; margin-bottom: 0.75rem;">
            {"🚀 رافع المشروع إلى Hugging Face Spaces" if lang == "ar" else "🚀 Hugging Face Space Deployer"}
          </h1>
          <p style="color: var(--color-text-secondary); font-size: 1.05rem; max-width: 700px; margin: 0 auto; line-height: 1.6;">
            {"يمكنك الآن بنقرة واحدة رفع كامل كود التطبيق وتدشينه أونلاين على منصة Hugging Face. سيقوم المعالج التلقائي بإنشاء الـ Space ورفع الملفات وتفعيل الرابط المباشر في ثوانٍ معدودة!" 
            if lang == "ar" else 
            "Deploy your entire application online with a single click on Hugging Face Spaces. The deployer will create the space, upload your files, and prepare your live link in seconds!"}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Inputs Section
    st.markdown(
        f"""
        <div style="margin-bottom: 0.8rem; font-weight: 700; color: var(--color-text-primary); font-size: 1.05rem;">
            {"🔑 إعدادات حساب Hugging Face" if lang == "ar" else "🔑 Hugging Face Account Credentials"}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_inputs, col_info = st.columns([5, 4], gap="large")
    
    with col_inputs:
        with st.container(border=True):
            # Load default token from environment
            env_token = os.getenv("HF_TOKEN", "")
            
            hf_token = st.text_input(
                "🤗 رمز الوصول (Hugging Face Access Token - Write):" if lang == "ar" else "🤗 Hugging Face Write Access Token:",
                value=env_token,
                type="password",
                placeholder="hf_..."
            )
            
            st.caption(
                "💡 يُنصح باستخدام رمز وصول بصلاحية 'Write' لتمكين النظام من إنشاء الـ Space ورفع الملفات."
                if lang == "ar" else
                "💡 A Write token is required for the deployer to create repositories and upload files."
            )
            
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            
            repo_id = st.text_input(
                "📦 اسم المستودع المستهدف (Space Repository ID):" if lang == "ar" else "📦 Space Repository ID (username/space-name):",
                placeholder="e.g. username/real-estate-proposal-generator"
            )
            
            st.caption(
                "💡 مثال: `ahmed/proposal-generator` (تأكد من كتابة اسم حسابك أولاً يليه اسم المشروع)."
                if lang == "ar" else
                "💡 Format: `username/space-name` (use your actual HF username followed by the space name)."
            )
            
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            
            # Start Deployment Button
            if st.button("🚀 ابدأ الرفع والتدشين أونلاين" if lang == "ar" else "🚀 Start Online Deployment", type="primary", use_container_width=True):
                if not hf_token:
                    st.error("الرجاء إدخال رمز الوصول الخاص بـ Hugging Face أولاً!" if lang == "ar" else "Please enter your Hugging Face Token first!")
                elif not repo_id or "/" not in repo_id:
                    st.error("الرجاء إدخال اسم مستودع صحيح بالصيغة: username/space-name" if lang == "ar" else "Please enter a valid Repository ID formatted as username/space-name")
                else:
                    try:
                        # Ensure huggingface_hub is available
                        from huggingface_hub import HfApi
                        api = HfApi(token=hf_token)
                        
                        # 1. Create Space Repo if not exists
                        with st.spinner("جاري تهيئة وإنشاء مستودع الـ Space..." if lang == "ar" else "Creating space repository on Hugging Face..."):
                            try:
                                api.create_repo(
                                    repo_id=repo_id,
                                    repo_type="space",
                                    space_sdk="docker",
                                    private=False,
                                    exist_ok=True
                                )
                                logger.info("Hugging Face Space repository checked/created successfully with Docker SDK: %s", repo_id)
                            except Exception as repo_err:
                                st.warning(f"ملاحظة أثناء تهيئة المستودع: {repo_err}")

                        # 2. Upload entire folder excluding heavy items
                        with st.spinner("جاري رفع ملفات المشروع وهياكل الأكواد..." if lang == "ar" else "Uploading project files..."):
                            api.upload_folder(
                                folder_path=".",
                                repo_id=repo_id,
                                repo_type="space",
                                ignore_patterns=[
                                    ".git",
                                    ".git/**/*",
                                    "venv",
                                    "venv/**/*",
                                    "__pycache__",
                                    "__pycache__/**/*",
                                    "outputs",
                                    "outputs/**/*",
                                    ".env",
                                    "*.pyc",
                                    ".firebase",
                                    ".firebase/**/*",
                                    ".netlify",
                                    ".netlify/**/*",
                                    "dist",
                                    "dist/**/*",
                                    "check_git.py",
                                    "*.pptx",
                                    "*.pdf",
                                    "*.docx",
                                    "assets/*.pdf",
                                    "assets/*.pptx",
                                    "assets/*.docx"
                                ]
                            )
                            
                        # Success state
                        space_url = f"https://huggingface.co/spaces/{repo_id}"
                        
                        st.markdown(
                            f"""
                            <div style="padding: 1.5rem; border-radius: var(--radius-md); background: rgba(16, 185, 129, 0.06); border: 1px solid var(--color-success); margin-top: 1.5rem;">
                                <h3 style="color: var(--color-success); margin: 0 0 0.5rem 0; font-size: 1.3rem;">🎉 {"تم التدشين والرفع بنجاح!" if lang == "ar" else "Deployed Successfully!"}</h3>
                                <p style="color: var(--color-text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.2rem;">
                                    {"تهانينا! أصبح تطبيق مولد العروض العقارية نشطاً الآن أونلاين على Hugging Face Spaces. سيقوم الخادم بتثبيت الاعتمادات وبدء التشغيل خلال دقيقة واحدة." 
                                    if lang == "ar" else 
                                    "Congratulations! Your Real Estate Proposal Generator is now live on Hugging Face Spaces. The builder is currently setting up the environment and will boot up in about a minute."}
                                </p>
                                <a href="{space_url}" target="_blank" style="display: inline-block; padding: 0.6rem 1.5rem; border-radius: 8px; background: var(--color-primary); color: white; text-decoration: none; font-weight: 600;">
                                    {"🌐 اذهب لرابط الـ Space المباشر" if lang == "ar" else "🌐 Go to Live Space"}
                                </a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.balloons()
                        
                    except Exception as e:
                        logger.error("Deployment failed: %s", e)
                        st.error(f"فشلت عملية الرفع: {e}" if lang == "ar" else f"Deployment failed: {e}")

    with col_info:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="margin-bottom: 0.8rem; font-weight: 700; color: var(--color-primary); font-size: 1rem;">
                    {"ℹ️ معلومات ومعايير الرفع" if lang == "ar" else "ℹ️ Deployment Standards"}
                </div>
                <ul style="color: var(--color-text-secondary); font-size: 0.9rem; line-height: 1.6; padding-right: 1.2rem; margin: 0;">
                    <li><b>{"حماية البيانات والخصوصية:" if lang == "ar" else "Data Privacy:"}</b> {"يتم تلقائياً حظر واستبعاد ملفات الإعدادات والرموز السرية (.env) ومستودعات التخزين المحلية (.git) لضمان أمان مفاتيح البرمجة الخاصة بك." if lang == "ar" else "Secret configuration files (.env) and local storage (.git) are automatically ignored to ensure your API keys remain secure."}</li>
                    <li><b>{"الملفات المرفوعة:" if lang == "ar" else "Uploaded Files:"}</b> {"سيتم رفع كامل كود واجهات Streamlit، ومحركات بناء الباوربوينت، وملفات الترجمة (i18n) والتصميم." if lang == "ar" else "All Streamlit user interfaces, PPTX builders, and i18n configurations will be safely uploaded."}</li>
                    <li><b>{"التشغيل التلقائي:" if lang == "ar" else "Automated Run:"}</b> {"سيتعرف Hugging Face تلقائياً على ملف app.py ويبدأ تشغيله باستخدام مكتبة Streamlit المثبتة في requirements.txt." if lang == "ar" else "Hugging Face will automatically discover app.py and run it using the libraries specified in requirements.txt."}</li>
                </ul>
                """,
                unsafe_allow_html=True
            )
