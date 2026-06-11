"""HTML component renderers — generate iframe editors via Jinja2 templates."""

from pathlib import Path

import streamlit.components.v1 as components
from jinja2 import Template

from ui.styles.generator import generate_css_variables
from ui.styles.tokens import tokens

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_SHARED_DIR = _TEMPLATES_DIR / "shared"


def _load_shared(name: str) -> str:
    path = _SHARED_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _render_template(template_name: str, **kwargs) -> str:
    """Read a Jinja2 template, inject shared assets, and render."""
    template_path = _TEMPLATES_DIR / template_name
    template_text = template_path.read_text(encoding="utf-8")

    css_vars = generate_css_variables()
    component_css = _load_shared("component_base.css")
    icons_svg = _load_shared("icons.svg")
    utils_js = _load_shared("utils.js")

    tmpl = Template(template_text)
    return tmpl.render(
        css_vars=css_vars,
        component_css=component_css,
        icons_svg=icons_svg,
        utils_js=utils_js,
        **kwargs,
    )


def render_outline_editor(
    outline: list[dict],
    initial_density: str = "concise",
    initial_theme: str = "nebula",
    lang: str = "ar",
    key: str | None = None,
):
    """Render the outline editor HTML component."""
    i18n = {
        "ar": {
            "outline": "هيكل الشرائح",
            "addCard": "إضافة شريحة",
            "cardsTotal": "شريحة",
            "cardBreaks": "اكتب",
            "cardBreaksCode": "---",
            "cardBreaksEnd": "لفصل الشرائح",
            "customize": "تخصيص العرض",
            "textContent": "كمية النص",
            "textSub": "مقدار المحتوى لكل شريحة",
            "theme": "السمة",
            "themeSub": "اختر سمة ألوان العرض",
            "themeTitle": "العنوان",
            "themeBody": "النص",
            "back": "رجوع",
            "generate": "توليد العرض",
            "delete": "حذف",
            "moveUp": "أعلى",
            "moveDown": "أسفل",
            "bulletsPh": "أضف نقاطاً أو وصفاً...",
            "newSlide": "شريحة جديدة",
            "minimal": "مختصر",
            "concise": "موجز",
            "detailed": "تفصيلي",
            "extensive": "شامل",
            "requiresImage": "توليد صورة لهذه الشريحة",
            "imagePromptLabel": "وصف الصورة المطلوب توليدها بالذكاء الاصطناعي (اختياري):",
            "imagePromptPh": "اكتب وصفاً تفصيلياً بالإنجليزية أو العربية لتوجيه الذكاء الاصطناعي...",
        },
        "en": {
            "outline": "Slide outline",
            "addCard": "Add slide",
            "cardsTotal": "slides total",
            "cardBreaks": "Type",
            "cardBreaksCode": "---",
            "cardBreaksEnd": "for slide breaks",
            "customize": "Customize your presentation",
            "textContent": "Text amount",
            "textSub": "Amount of text per slide",
            "theme": "Theme",
            "themeSub": "Choose a color theme for your deck",
            "themeTitle": "Title",
            "themeBody": "Body text",
            "back": "Back",
            "generate": "Generate presentation",
            "delete": "Delete",
            "moveUp": "Up",
            "moveDown": "Down",
            "bulletsPh": "Add talking points or description...",
            "newSlide": "New slide",
            "minimal": "Minimal",
            "concise": "Concise",
            "detailed": "Detailed",
            "extensive": "Extensive",
            "requiresImage": "Generate image for this slide",
            "imagePromptLabel": "AI Image prompt description (optional):",
            "imagePromptPh": "Describe the scene details in English or Arabic to guide the AI...",
        },
    }

    themes = [
        {"id": "executive", "name": "Executive", "bg": tokens.BG, "title": tokens.TEXT_PRIMARY, "body": tokens.TEXT_SECONDARY, "accent": tokens.PRIMARY},
        {"id": "corporate", "name": "Corporate", "bg": tokens.SURFACE, "title": tokens.TEXT_PRIMARY, "body": tokens.TEXT_SECONDARY, "accent": tokens.SECONDARY},
        {"id": "minimal", "name": "Minimal", "bg": tokens.SURFACE_INSET, "title": tokens.TEXT_PRIMARY, "body": tokens.TEXT_SECONDARY, "accent": tokens.TEXT_PRIMARY},
        {"id": "warm", "name": "Warm", "bg": "#1A1A1A", "title": "#F1F5F9", "body": "#94A3B8", "accent": "#C9A87C"},
    ]

    html = _render_template(
        "outline_editor.html",
        lang=lang,
        i18n_json=i18n,
        themes_json=themes,
    )

    dist_dir = Path(__file__).resolve().parent / "outline_editor_dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / "index.html").write_text(html, encoding="utf-8")

    outline_editor = components.declare_component(
        "outline_editor",
        path=str(dist_dir)
    )

    return outline_editor(
        outline=outline,
        initial_density=initial_density,
        initial_theme=initial_theme,
        lang=lang,
        key=key,
    )


def render_slide_editor(
    slides: list[dict],
    project_name: str = "",
    lang: str = "ar",
    key: str | None = None,
    pptx_b64: str = "",
    pptx_filename: str = "",
):
    """Render the slide editor HTML component."""
    i18n = {
        "ar": {
            "editor": "محرر العرض",
            "download": "تحميل PPTX",
            "newPres": "عرض جديد",
            "regen": "إعادة توليد",
            "slide": "شريحة",
            "saved": "تم الحفظ",
            "untitled": "عرض بدون عنوان",
        },
        "en": {
            "editor": "Presentation editor",
            "download": "Download PPTX",
            "newPres": "New presentation",
            "regen": "Regenerate",
            "slide": "Slide",
            "saved": "Saved",
            "untitled": "Untitled presentation",
        },
    }

    html = _render_template(
        "slide_editor.html",
        lang=lang,
        i18n_json=i18n,
    )

    dist_dir = Path(__file__).resolve().parent / "slide_editor_dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / "index.html").write_text(html, encoding="utf-8")

    slide_editor = components.declare_component(
        "slide_editor",
        path=str(dist_dir)
    )

    return slide_editor(
        slides=slides,
        project_name=project_name,
        lang=lang,
        key=key,
        pptx_b64=pptx_b64,
        pptx_filename=pptx_filename,
    )

