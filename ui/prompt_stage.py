import streamlit as st

import utils.state_manager as sm
from ui import i18n
from utils.document_parser import process_uploaded_files
from ui.comprehensive_form import render_comprehensive_form

def handle_ignore_file(filename):
    if "ignored_files" not in st.session_state:
        st.session_state["ignored_files"] = []
    if filename not in st.session_state["ignored_files"]:
        st.session_state["ignored_files"].append(filename)


def render_prompt_stage():
    """Professional presentation-only create screen with centered layout and optional chat."""

    existing_data = sm.get_project_data() or {}
    sm.set_val("generation_mode", "auto")

    # Inject CSS
    st.markdown(
        """
        <style>
        /* ── Unified Light Theme Sidebar (No Outlines) ── */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 0 !important;
            margin-bottom: 0.6rem !important;
            box-shadow: none !important;
        }

        /* ── Unified Chat Viewport (Borderless & Seamless) ── */
        div:has(> div.chat-viewport-marker),
        div:has(> div > div.chat-viewport-marker),
        div[data-testid="stVerticalBlock"]:has(div.chat-viewport-marker),
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.chat-viewport-marker) {
            border: none !important;
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
            border-radius: 0 !important;
            padding: 0.5rem 0 !important;
        }

        /* ── Chat Messages (Gemini Style - No bubble borders) ── */
        div[data-testid="stChatMessage"] {
            background-color: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 0.5rem 0 !important;
            margin-bottom: 1rem !important;
            box-shadow: none !important;
            transition: none !important;
        }

        /* User Message bubble - soft warm rose/burgundy elegant pill floated opposite avatar */
        div[data-testid="stChatMessage"]:has(div.chat-msg-user) {
            background-color: #f5eae8 !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 0.75rem 1.25rem !important;
            margin-bottom: 1.2rem !important;
            max-width: 80% !important;
            margin-right: auto !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
        }
        div[data-testid="stChatMessage"]:has(div.chat-msg-user) div[data-testid="stMarkdownContainer"] {
            color: #5a1110 !important;
            font-size: 0.98rem !important;
        }

        /* Assistant Message bubble - completely transparent text flow */
        div[data-testid="stChatMessage"]:has(div.chat-msg-assistant) {
            background-color: transparent !important;
            border: none !important;
            padding: 0.5rem 0 !important;
            margin-bottom: 1.2rem !important;
        }
        div[data-testid="stChatMessage"]:has(div.chat-msg-assistant) div[data-testid="stMarkdownContainer"] {
            color: var(--color-text-primary) !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }

        /* Keep chat content bounded in RTL so long Arabic text wraps instead of clipping. */
        div[data-testid="stVerticalBlock"]:has(div.chat-viewport-marker),
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.chat-viewport-marker) {
            max-width: 100% !important;
            overflow-x: hidden !important;
        }
        div[data-testid="stVerticalBlock"]:has(div.chat-viewport-marker) div[data-testid="stChatMessage"] {
            max-width: 100% !important;
            min-width: 0 !important;
        }
        div[data-testid="stVerticalBlock"]:has(div.chat-viewport-marker) div[data-testid="stMarkdownContainer"],
        div[data-testid="stVerticalBlock"]:has(div.chat-viewport-marker) div[data-testid="stMarkdownContainer"] * {
            max-width: 100% !important;
            white-space: normal !important;
            overflow-wrap: anywhere !important;
            word-break: normal !important;
        }

        /* Avatar styling */
        div[data-testid="stChatMessage"] div[data-testid="stChatMessageAvatar"] {
            border-radius: 50% !important;
            background-color: #ffffff !important;
            border: 1px solid #eef2f6 !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
        }

        /* ── Unified Pill-Shape Chat Input Capsule ── */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) {
            border-radius: 32px !important;
            background-color: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
            padding: 0.2rem 1rem !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
            transition: border-color 0.3s, box-shadow 0.3s !important;
            margin-top: 0.3rem !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker):focus-within {
            border-color: var(--color-primary) !important;
            box-shadow: 0 0 0 3px rgba(103, 13, 12, 0.1), 0 4px 16px rgba(0, 0, 0, 0.08) !important;
        }

        /* Outer horizontal block (contains uploader on the right, form on the left) */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFileUploader"]) {
            align-items: center !important;
            display: flex !important;
            gap: 8px !important;
            direction: rtl !important;
            width: 100% !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFileUploader"]) > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        /* Uploader column: fixed small width */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFileUploader"]) > div:nth-child(1) {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex: 0 0 36px !important;
            width: 36px !important;
            min-width: 36px !important;
            max-width: 36px !important;
        }
        /* Form column: stretch to fill all remaining width */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFileUploader"]) > div:nth-child(2) {
            display: flex !important;
            align-items: center !important;
            flex: 1 1 auto !important;
            min-width: 0 !important;
            width: 100% !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFileUploader"]) > div:nth-child(2) > div {
            width: 100% !important;
        }

        /* Inner horizontal block inside form (contains textarea on the right, submit button on the left) */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFormSubmitButton"]) {
            align-items: center !important;
            display: flex !important;
            gap: 8px !important;
            direction: rtl !important;
            width: 100% !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFormSubmitButton"]) > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        /* Textarea column: stretch to fill all remaining width */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFormSubmitButton"]) > div:nth-child(1) {
            display: flex !important;
            align-items: center !important;
            flex: 1 1 auto !important;
            min-width: 0 !important;
            width: 100% !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFormSubmitButton"]) > div:nth-child(1) > div {
            width: 100% !important;
        }
        /* Submit button column: fixed small width */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFormSubmitButton"]) > div:nth-child(2) {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex: 0 0 36px !important;
            width: 36px !important;
            min-width: 36px !important;
            max-width: 36px !important;
        }

        /* Remove default borders and backgrounds of the nested text area */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stTextArea"] > div {
            border: none !important;
            background-color: transparent !important;
            background: transparent !important;
            box-shadow: none !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) .stTextArea textarea {
            border: none !important;
            background-color: transparent !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: 0.5rem 0 !important;
            font-size: 0.95rem !important;
            color: var(--color-text-primary) !important;
            height: 38px !important;
            min-height: 38px !important;
            resize: none !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) .stTextArea textarea::placeholder {
            color: #999999 !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) .stTextArea textarea:focus {
            transform: none !important;
        }

        /* Hide all default Streamlit input/textarea helper instructions (Press Ctrl+Enter to apply) */
        div[data-testid="InputInstructions"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ── File Uploader '+' Circle Button ── */
        div[data-testid="stFileUploader"] {
            min-height: unset !important;
            height: 36px !important;
            width: 36px !important;
            max-width: 36px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            overflow: visible !important;
            position: relative !important;
        }

        /* Hide the file uploader label */
        div[data-testid="stFileUploader"] > label {
            display: none !important;
        }

        /* Hide the file item container once the upload is completed (it contains the chip) */
        div[data-testid="stFileUploaderFile"]:has(div[data-testid="stFileChips"]) {
            display: none !important;
        }
        /* Hide Streamlit's built-in file chips */
        div[data-testid="stFileChips"] {
            display: none !important;
        }
        /* Hide the built-in add-files button that appears after upload */
        div[data-testid="stFileUploader"] button[data-testid="stBaseButton-borderlessIcon"] {
            display: none !important;
        }

        /* Style the dropzone section as a 36px circle */
        section[data-testid="stFileUploaderDropzone"] {
            border: none !important;
            background: transparent !important;
            background-color: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            min-height: unset !important;
            box-shadow: none !important;
            width: 36px !important;
            height: 36px !important;
            max-width: 36px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 50% !important;
            cursor: pointer !important;
            position: relative !important;
            overflow: hidden !important;
            transition: background-color 0.2s ease !important;
        }

        /* Hide Upload button span */
        section[data-testid="stFileUploaderDropzone"] > span {
            display: none !important;
        }

        /* Hide file type instructions */
        div[data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
        }

        /* Make hidden input cover the entire circle */
        input[data-testid="stFileUploaderDropzoneInput"] {
            display: block !important;
            width: 36px !important;
            height: 36px !important;
            opacity: 0 !important;
            cursor: pointer !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            z-index: 5 !important;
            clip: auto !important;
            clip-path: none !important;
            margin: 0 !important;
            padding: 0 !important;
            white-space: normal !important;
            overflow: visible !important;
        }

        /* Inject "+" icon */
        section[data-testid="stFileUploaderDropzone"]::before {
            content: "+";
            font-size: 1.4rem !important;
            font-weight: 300 !important;
            color: #999999 !important;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 1;
            line-height: 1;
            transition: color 0.2s ease;
        }

        section[data-testid="stFileUploaderDropzone"]:hover {
            background-color: #f5f5f5 !important;
        }
        section[data-testid="stFileUploaderDropzone"]:hover::before {
            color: var(--color-primary) !important;
        }

        /* Floating uploaded files popup above tray */
        div[data-testid="stFileUploader"] [data-testid="stUploadedFileData"] {
            position: absolute;
            bottom: 60px;
            right: 10px;
            z-index: 99;
            background-color: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            padding: 0.4rem 0.8rem !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08) !important;
        }

        /* ── Circular Send Button (↑) ── */
        form[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button {
            width: 36px !important;
            height: 36px !important;
            min-width: 36px !important;
            max-width: 36px !important;
            border-radius: 50% !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 1.2rem !important;
            font-weight: bold !important;
            background-color: var(--color-primary) !important;
            color: #ffffff !important;
            border: none !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
        }
        form[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button:hover {
            background-color: #8F1D1B !important;
            transform: scale(1.05) !important;
            box-shadow: 0 4px 12px rgba(103, 13, 12, 0.2) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) .stTextArea textarea {
            direction: rtl !important;
            text-align: right !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 1. Initialize chat state & facts
    if "consultant_chat_history" not in st.session_state:
        st.session_state["consultant_chat_history"] = [
            {
                "role": "assistant",
                "content": (
                    "مرحباً بك مجدداً! يمكنك إرفاق دراسة الجدوى أو أي ملفات أخرى هنا. "
                    "كما يمكنك إضافة أية تفاصيل نصية دقيقة تود من الذكاء الاصطناعي أخذها في الاعتبار."
                )
            }
        ]
        st.session_state["extracted_facts"] = {
            "project_name": "",
            "num_slides": "12",
            "description": "",
            "floor_distribution": "",
            "image_style_description": "",
            "location": "",
            "financial_details": "",
            "language": "العربية",
            "all_essential_facts_gathered": False
        }
        st.session_state["processed_files_cache"] = []
    if "chat_uploader_counter" not in st.session_state:
        st.session_state["chat_uploader_counter"] = 0

    from services.llm_service import generate_json
    from prompts.content_prompts import generate_consultant_chat_prompt

    if "ignored_files" not in st.session_state:
        st.session_state["ignored_files"] = []

    def render_uploaded_files_previews(active_files):
        st.markdown(
            """
            <style>
            div[data-testid="stHorizontalBlock"]:has(.file-preview-card):not(:has(div[data-testid="stHorizontalBlock"])) {
                display: flex !important;
                flex-wrap: wrap !important;
                justify-content: flex-end !important;
                gap: 15px !important;
                padding: 10px 5px !important;
                direction: rtl !important;
                max-width: 100% !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.file-preview-card):not(:has(div[data-testid="stHorizontalBlock"])) > div[data-testid="stColumn"] {
                position: relative !important;
                width: auto !important;
                flex: 0 0 auto !important;
                padding: 0 !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.file-preview-card):not(:has(div[data-testid="stHorizontalBlock"])) > div[data-testid="stColumn"] div.stElementContainer:has(div[data-testid="stButton"]) {
                position: static !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.file-preview-card):not(:has(div[data-testid="stHorizontalBlock"])) > div[data-testid="stColumn"] div[data-testid="stButton"] {
                position: absolute !important;
                top: -5px !important;
                right: -5px !important;
                left: auto !important;
                z-index: 9999 !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.file-preview-card):not(:has(div[data-testid="stHorizontalBlock"])) > div[data-testid="stColumn"] button {
                width: 18px !important;
                height: 18px !important;
                min-width: 18px !important;
                min-height: 18px !important;
                max-width: 18px !important;
                max-height: 18px !important;
                border-radius: 50% !important;
                padding: 0 !important;
                font-size: 9px !important;
                line-height: 18px !important;
                background: #ffffff !important;
                color: #000000 !important;
                border: 1px solid #dddddd !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.file-preview-card):not(:has(div[data-testid="stHorizontalBlock"])) > div[data-testid="stColumn"] button:hover {
                background: #ff4d4d !important;
                color: #ffffff !important;
                border-color: #ff4d4d !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        widths = []
        for file in active_files:
            ext = file.name.lower().split('.')[-1]
            if ext in ['png', 'jpg', 'jpeg']:
                widths.append(1)
            else:
                widths.append(4)
                
        cols = st.columns(widths)
        for idx, file in enumerate(active_files):
            with cols[idx]:
                ext = file.name.lower().split('.')[-1]
                
                if ext in ['png', 'jpg', 'jpeg']:
                    try:
                        file_bytes = file.getvalue()
                        from PIL import Image
                        import io
                        import base64
                        img = Image.open(io.BytesIO(file_bytes))
                        img.thumbnail((80, 80))
                        out_buf = io.BytesIO()
                        img.save(out_buf, format="JPEG")
                        b64 = base64.b64encode(out_buf.getvalue()).decode('utf-8')
                        card_html = f"""
                        <div class="file-preview-card" style="width: 38px; height: 38px; border-radius: var(--radius-md); border: 1px solid var(--color-border-strong); overflow: hidden; display: flex; align-items: center; justify-content: center; box-shadow: var(--shadow-sm); background: var(--color-surface); box-sizing: border-box;">
                            <img src="data:image/jpeg;base64,{b64}" style="width:100%; height:100%; object-fit:cover;">
                        </div>
                        """
                    except Exception:
                        card_html = """
                        <div class="file-preview-card" style="width: 38px; height: 38px; border-radius: var(--radius-md); border: 1px solid var(--color-border-strong); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; background: var(--color-surface); box-sizing: border-box;">
                            🖼️
                        </div>
                        """
                else:
                    bg_color = "rgba(var(--color-primary-rgb), 0.1)"
                    color = "var(--color-primary)"
                    if ext == 'pdf':
                        icon_html = "📕"
                        bg_color = "rgba(239, 68, 68, 0.1)"
                        color = "#EF4444"
                    elif ext in ['doc', 'docx']:
                        icon_html = "📄"
                        bg_color = "rgba(59, 130, 246, 0.1)"
                        color = "#3B82F6"
                    elif ext == 'pptx':
                        icon_html = "📊"
                        bg_color = "rgba(249, 115, 22, 0.1)"
                        color = "#F97316"
                    else:
                        icon_html = "📝"
                        bg_color = "rgba(107, 114, 128, 0.1)"
                        color = "#6B7280"
                        
                    card_html = f"""
                    <div class="file-preview-card" style="display: flex; align-items: center; background: var(--color-surface); border: 1px solid var(--color-border-strong); border-radius: var(--radius-md); padding: 4px 8px; gap: 6px; width: 160px; box-shadow: var(--shadow-sm); box-sizing: border-box; height: 38px;">
                        <div style="width: 24px; height: 24px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; background: {bg_color}; color: {color}; flex-shrink: 0; font-size: 0.95rem;">
                            {icon_html}
                        </div>
                        <div style="display: flex; flex-direction: column; overflow: hidden; flex-grow: 1; padding-right: 5px;">
                            <div style="font-size: 0.72rem; font-weight: 600; color: var(--color-text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; direction: ltr; text-align: left;">{file.name}</div>
                        </div>
                    </div>
                    """
                st.markdown(card_html, unsafe_allow_html=True)
                st.button(
                    "✕",
                    key=f"del_file_{idx}_{file.name}",
                    help="حذف الملف",
                    on_click=handle_ignore_file,
                    args=(file.name,)
                )

    def handle_text_submit():
        text_val = st.session_state.get("chat_text", "")
        
        uploader_key = f"chat_uploader_{st.session_state.get('chat_uploader_counter', 0)}"
        uploaded_files = st.session_state.get(uploader_key, [])
        ignored_files = st.session_state.get("ignored_files", [])
        active_files = [f for f in uploaded_files if f.name not in ignored_files]
        
        new_docs_text = ""
        new_docs_images = []
        
        if active_files:
            with st.spinner("جاري قراءة واستخراج البيانات من المستندات المرفقة..."):
                parsed_text, parsed_images = process_uploaded_files(active_files)
                sm.set_val("docs_text", parsed_text)
                sm.set_val("docs_images", parsed_images)
                new_docs_text = parsed_text
                new_docs_images = parsed_images
                
        if (text_val and text_val.strip()) or active_files:
            display_msg = ""
            if text_val and text_val.strip():
                display_msg += text_val.strip()
            
            if active_files:
                file_names_str = ", ".join([f.name for f in active_files])
                if display_msg:
                    display_msg += f"\n\n📎 *[ملفات مرفقة: {file_names_str}]*"
                else:
                    display_msg += f"📎 *[ملفات مرفقة: {file_names_str}]*"
            
            st.session_state["consultant_chat_history"].append({"role": "user", "content": display_msg})
            st.session_state["pending_ai_run"] = {
                "new_docs_text": new_docs_text,
                "images": new_docs_images
            }
            st.session_state["ignored_files"] = []
            st.session_state["chat_uploader_counter"] = st.session_state.get("chat_uploader_counter", 0) + 1
            st.session_state["run_ai_now"] = True

    # Premium Centered Layout
    col_empty1, col_center, col_empty2 = st.columns([1, 6, 1], gap="large")

    with col_center:
        # Top toolbar
        col_space, col_clear = st.columns([4, 2])
        with col_clear:
            if st.button("🧹 مشروع جديد ومسح البيانات", use_container_width=True, key="clear_chat_session"):
                keys_to_delete = ["consultant_chat_history", "extracted_facts", "processed_files_cache", "structured_project_data", "form_step", "show_chat"]
                for k in keys_to_delete:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        # The Form Wizard
        with st.container(border=True):
            form_status = render_comprehensive_form()
            
            if st.session_state.get("force_generation"):
                form_status = True
                st.session_state["force_generation"] = False
            
            # If the user clicked "نعم أريد محادثة أو رفع ملفات", form_status will be "SHOW_CHAT"
            if form_status == "SHOW_CHAT":
                st.markdown(
                    """
                    <style>
                    /* Reduce spacing in the main page content */
                    .block-container {
                        padding-top: 0.5rem !important;
                        padding-bottom: 0.5rem !important;
                    }
                    /* Only shrink the CHAT outer bordered container, not every wrapper */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.chat-viewport-marker) {
                        padding: 10px 15px !important;
                        margin-bottom: 0 !important;
                    }
                    /* Shrink header margins */
                    .stApp h4 {
                        margin-top: 0 !important;
                        margin-bottom: 4px !important;
                    }
                    
                    /* The uploader styling is handled by the global circular upload button style */
                    
                    /* Float the default files list (for upload progress tracking) above the input tray */
                    div[data-testid="stFileUploaderFiles"] {
                        position: absolute !important;
                        bottom: 55px !important;
                        right: 10px !important;
                        width: 280px !important;
                        z-index: 999999 !important;
                        background: transparent !important;
                        border: none !important;
                        box-shadow: none !important;
                        padding: 0 !important;
                        display: block !important;
                    }
                    /* Style the active uploading file container as a card */
                    div[data-testid="stFileUploaderFile"] {
                        background: #ffffff !important;
                        border: 1px solid #e0e0e0 !important;
                        border-radius: 8px !important;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
                        padding: 10px !important;
                        margin-bottom: 8px !important;
                        display: block !important;
                    }
                    /* Premium styling for Streamlit progress bar inside it */
                    div[data-testid="stFileUploaderFiles"] div[data-testid="stProgressBar"] > div {
                        background-color: #f0f2f6 !important;
                        height: 6px !important;
                        border-radius: 3px !important;
                    }
                    div[data-testid="stFileUploaderFiles"] div[data-testid="stProgressBar"] div[role="progressbar"] {
                        background-color: var(--color-primary) !important;
                    }

                    /* ── File preview row: keep inside container bounds ── */
                    div[data-testid="stHorizontalBlock"]:has(.file-preview-card) {
                        max-width: 100% !important;
                        overflow-x: auto !important;
                        box-sizing: border-box !important;
                    }

                    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) {
                        padding: 0.35rem 0.75rem !important;
                        overflow: visible !important;
                    }

                    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextArea"]) {
                        display: grid !important;
                        grid-template-columns: 42px minmax(0, 1fr) 42px !important;
                        gap: 8px !important;
                        direction: rtl !important;
                        align-items: center !important;
                        width: 100% !important;
                    }

                    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextArea"]) > div {
                        min-width: 0 !important;
                        width: 100% !important;
                        padding: 0 !important;
                    }

                    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextArea"]) > div:nth-child(1),
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextArea"]) > div:nth-child(3) {
                        width: 42px !important;
                        min-width: 42px !important;
                        max-width: 42px !important;
                    }

                    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.unified-input-tray-marker) .stTextArea textarea {
                        direction: rtl !important;
                        text-align: right !important;
                    }

                    /* ── Action buttons row: prevent overflow ── */
                    div[data-testid="stHorizontalBlock"]:has(div.chat-actions-spacer) {
                        width: 100% !important;
                        max-width: 100% !important;
                        box-sizing: border-box !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(div.chat-actions-spacer) > div[data-testid="stColumn"] {
                        min-width: 0 !important;
                        box-sizing: border-box !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown("#### 🤖 المستشار العقاري الذكي")
                
                # Previews of uploaded files using the dynamic uploader key
                uploader_key = f"chat_uploader_{st.session_state.get('chat_uploader_counter', 0)}"
                uploaded_files = st.session_state.get(uploader_key, [])
                ignored_files = st.session_state.get("ignored_files", [])
                active_files = [f for f in uploaded_files if f.name not in ignored_files]
                
                # Dynamically set chat history height to prevent content push-down
                chat_height = 140 if active_files else 215
                
                # Chat History
                spinner_placeholder = None
                with st.container(height=chat_height):
                    st.markdown('<div class="chat-viewport-marker"></div>', unsafe_allow_html=True)
                    for msg in st.session_state["consultant_chat_history"]:
                        if msg["role"] == "assistant":
                            with st.chat_message("assistant", avatar="🏢"):
                                st.markdown(f'<div class="chat-msg-assistant"></div>{msg["content"]}', unsafe_allow_html=True)
                        else:
                            with st.chat_message("user", avatar="👤"):
                                st.markdown(f'<div class="chat-msg-user"></div>{msg["content"]}', unsafe_allow_html=True)
                    spinner_placeholder = st.empty()

                # Placeholder for File Previews (rendered ABOVE the input capsule)
                preview_placeholder = st.container()

                # Chat Input Tray (container is outside form, uploader outside form)
                with st.container(border=True):
                    st.markdown('<div class="unified-input-tray-marker"></div>', unsafe_allow_html=True)
                    
                    col_upload, col_form = st.columns([1, 10], gap="small")

                    with col_upload:
                        uploaded_files = st.file_uploader(
                            "رفع ملفات",
                            type=["pdf", "docx", "doc", "txt", "pptx", "png", "jpg", "jpeg"],
                            accept_multiple_files=True,
                            label_visibility="collapsed",
                            key=uploader_key,
                        )

                    # Compute current active files based on direct return value
                    ignored_files = st.session_state.get("ignored_files", [])
                    active_files = [f for f in (uploaded_files or []) if f.name not in ignored_files]

                    # Populate placeholder if there are active files
                    if active_files:
                        with preview_placeholder:
                            render_uploaded_files_previews(active_files)

                    with col_form:
                        with st.form("chat_form", clear_on_submit=True, border=False):
                            col_text, col_submit = st.columns([10, 1], gap="small")
                            with col_text:
                                st.text_area(
                                    "Write a message...",
                                    placeholder="اكتب رسالة للمستشار العقاري أو ارفع ملفك من زر الزائد...",
                                    label_visibility="collapsed",
                                    key="chat_text",
                                    height=38,
                                )
                            with col_submit:
                                submitted = st.form_submit_button("↑", use_container_width=True, type="primary")

                if submitted:
                    handle_text_submit()
                    st.rerun()

                # AI Processing block
                if st.session_state.get("run_ai_now"):
                    ai_run = st.session_state.pop("pending_ai_run", None)
                    if ai_run and spinner_placeholder:
                        with spinner_placeholder:
                            with st.spinner("جاري تفكير وتحليل المستشار العقاري..."):
                                try:
                                    sys_p, usr_p = generate_consultant_chat_prompt(
                                        chat_history=st.session_state["consultant_chat_history"],
                                        uploaded_docs_text=ai_run["new_docs_text"],
                                        structured_data=st.session_state.get("structured_project_data", {})
                                    )
                                    response_json = generate_json(sys_p, usr_p, images=ai_run.get("images"), use_chat_model=True)
                                    
                                    chat_reply = response_json.get("chat_response", "تم استلام التفاصيل، يمكنك الإنهاء والمتابعة.")
                                    fact_sheet = response_json.get("fact_sheet", {})
                                    st.session_state["extracted_facts"].update(fact_sheet)
                                    st.session_state["consultant_chat_history"].append({"role": "assistant", "content": chat_reply})
                                except Exception as e:
                                    st.session_state["consultant_chat_history"].append({
                                        "role": "assistant",
                                        "content": f"تم استقبال البيانات. (ملاحظة تقنية: {str(e)})"
                                    })
                    st.session_state["run_ai_now"] = False
                    st.rerun()



                st.markdown(
                    """
                    <style>
                    div[data-testid="stHorizontalBlock"]:has(div.chat-actions-spacer) {
                        align-items: stretch !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(div.chat-actions-spacer) .stButton > button {
                        height: auto !important;
                        min-height: 44px !important;
                        white-space: normal !important;
                        overflow: visible !important;
                        line-height: 1.35 !important;
                        padding: 0.55rem 0.75rem !important;
                        text-align: center !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(div.chat-actions-spacer) .stButton > button * {
                        white-space: normal !important;
                        overflow-wrap: anywhere !important;
                        word-break: normal !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                col_prev, col_done = st.columns(2)
                with col_prev:
                    st.markdown('<div class="chat-actions-spacer"></div>', unsafe_allow_html=True)
                    if st.button("⬅️ تراجع", use_container_width=True):
                        st.session_state["show_chat"] = False
                        st.session_state["form_step"] = 12
                        st.rerun()
                with col_done:
                    if st.button("✅ إنهاء المحادثة والانتقال للمراجعة", use_container_width=True, type="primary"):
                        st.session_state["force_generation"] = True
                        st.rerun()

            elif form_status is True:
                # Trigger actual generation stage
                with st.spinner("جاري جمع البيانات وصياغة هيكل المقترح..."):
                    facts = st.session_state.get("extracted_facts", {})
                    struct_data = st.session_state.get("structured_project_data", {})

                    lang_extracted = facts.get("language") or "العربية"
                    lang_norm = "English" if "en" in str(lang_extracted).lower() or "انجليز" in str(lang_extracted).lower() or "eng" in str(lang_extracted).lower() else "Arabic"

                    project_data = {
                        "project_name": struct_data.get("cover_project_name") or facts.get("project_name") or "مشروع عقاري",
                        "description": struct_data.get("intro_brief_desc") or facts.get("description") or f"مشروع عقاري تجاري بموقع مميز {struct_data.get('cover_location', '')}.",
                        "floor_distribution": facts.get("floor_distribution") or "أدوار تجارية وتأجيرية متعددة.",
                        "image_style_description": facts.get("image_style_description") or "Luxurious modern exterior architectural rendering, high-end materials, photorealistic, 8k.",
                        "num_slides": "12",
                        "language": lang_norm,
                        "structured_project_data": struct_data
                    }
                    sm.set_project_data(project_data)
                    sm.set_val("outline", None)
                    sm.set_val("smart_review_questions", None)
                    sm.set_stage("smart_review")
                    st.rerun()

    # Textarea auto-resize (one-time setup, no interval — form handles Enter+submit)
    js_autoresize = """
    <script>
    (function() {
        const parentDoc = window.parent.document;
        const textareas = parentDoc.querySelectorAll("textarea");
        textareas.forEach(textarea => {
            if (textarea.dataset.autoResizeSetup === "true") return;
            textarea.dataset.autoResizeSetup = "true";
            textarea.style.height = "38px";
            textarea.style.minHeight = "38px";
            textarea.style.maxHeight = "150px";
            textarea.style.resize = "none";
            textarea.style.overflowY = "hidden";
            textarea.addEventListener("input", function() {
                this.style.height = "auto";
                this.style.height = Math.min(150, this.scrollHeight) + "px";
                this.style.overflowY = this.scrollHeight > 150 ? "auto" : "hidden";
            });
        });
    })();
    </script>
    """
    import streamlit.components.v1 as components
    components.html(js_autoresize, height=0, width=0)
