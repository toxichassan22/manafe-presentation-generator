"""
State Manager – wraps st.session_state for typed access.
Keeps all app state in a single place so regeneration can be partial.
"""

from typing import Any, Optional
import json
from pathlib import Path
import streamlit as st

_PERSIST_FILE = Path(__file__).resolve().parent.parent / "outputs" / ".session_cache.json"
_PERSIST_KEYS = [
    "current_stage", "workspace_tab", "ui_language", "project_data", "docs_text", "outline",
    "theme", "density", "image_settings", "slide_contents", "pptx_path", "pdf_path",
    "clarifications",
]


# ── Session state keys ──────────────────────────────────────────────────
_KEYS = {
    "ui_language": "ar",             # "ar" | "en" — UI chrome language
    "workspace_tab": "home",        # top-level workspace navigation tab
    "current_stage": "prompt",       # "prompt" | "outline_review" | "settings" | "generating" | "preview"
    "project_data": None,            # dict with project form data
    "docs_text": "",                 # string extracted from uploaded context files
    "outline": None,                 # list[dict] the editable outline
    "theme": None,                   # dict with user selected fonts/colors
    "density": "Concise",            # string for text length
    "image_settings": None,          # dict with image gen preferences
    "land_image_bytes": None,        # bytes of uploaded land photo (legacy single image)
    "docs_images": None,             # list[dict] with base64 + mime_type for multiple land photos
    "land_analysis": None,           # dict from vision_service
    "slide_contents": None,          # list[dict] from content_generator
    "slide_images": None,            # dict[int, bytes] from image_generator
    "pptx_path": None,               # Path to generated .pptx
    "pdf_path": None,                # Path to exported .pdf
    "generation_progress": 0,        # 0-100 progress percentage
    "generation_status": "",         # Current status message
    "clarifications": {},            # Dictionary storing slide index to user answer mapping
}


def init_state():
    """Initialize all session state keys with defaults (if not already set)."""
    # Try to restore from disk first
    _load_persisted()
    for key, default in _KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = default


def _save_persisted():
    """Save key state to disk so it survives refresh."""
    try:
        data = {}
        for key in _PERSIST_KEYS:
            val = st.session_state.get(key)
            if val is not None:
                # Don't persist 'generating' — on refresh, go back to prompt
                if key == "current_stage" and val == "generating":
                    data[key] = "prompt"
                    continue
                if isinstance(val, Path):
                    data[key] = str(val)
                elif isinstance(val, (str, int, float, dict, list, bool)):
                    data[key] = val
        _PERSIST_FILE.parent.mkdir(parents=True, exist_ok=True)
        _PERSIST_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _load_persisted():
    """Load persisted state from disk."""
    try:
        if _PERSIST_FILE.exists():
            data = json.loads(_PERSIST_FILE.read_text(encoding="utf-8"))
            for key in _PERSIST_KEYS:
                if key in data and key not in st.session_state:
                    st.session_state[key] = data[key]
    except Exception:
        pass


def get(key: str) -> Any:
    """Get a value from session state."""
    return st.session_state.get(key, _KEYS.get(key))


def get_val(key: str) -> Any:
    """Alias for get() for backwards-compatibility."""
    return st.session_state.get(key, _KEYS.get(key))


def set_val(key: str, value: Any):
    """Set a value in session state."""
    st.session_state[key] = value


def get_stage() -> str:
    return get("current_stage")


def set_stage(stage: str):
    set_val("current_stage", stage)
    _save_persisted()


def get_workspace_tab() -> str:
    return get("workspace_tab") or "home"


def set_workspace_tab(tab: str):
    set_val("workspace_tab", tab or "home")
    _save_persisted()


def get_project_data() -> Optional[dict]:
    return get("project_data")


def set_project_data(data: dict):
    set_val("project_data", data)
    _save_persisted()


def get_land_image() -> Optional[bytes]:
    return get("land_image_bytes")


def set_land_image(img_bytes: bytes):
    set_val("land_image_bytes", img_bytes)


def get_docs_images() -> Optional[list]:
    """Get the list of land/site images uploaded by the user."""
    return get("docs_images")


def set_docs_images(images: list):
    """Store the list of land/site images (each a dict with base64 + mime_type)."""
    set_val("docs_images", images)


def get_land_analysis() -> Optional[dict]:
    return get("land_analysis")


def set_land_analysis(analysis: dict):
    set_val("land_analysis", analysis)


def get_slides() -> Optional[list[dict]]:
    return get("slide_contents")


def set_slides(slides: list[dict]):
    set_val("slide_contents", slides)
    _save_persisted()


def get_ui_language() -> str:
    return get("ui_language") or "ar"


def set_ui_language(lang: str):
    set_val("ui_language", lang if lang in ("ar", "en") else "ar")
    _save_persisted()


def update_slide(index: int, slide: dict):
    """Update a single slide (for partial regeneration)."""
    slides = get_slides()
    if slides and 0 <= index < len(slides):
        slides[index] = slide
        set_val("slide_contents", slides)
        _save_persisted()


def get_images() -> Optional[dict]:
    return get("slide_images")


def set_images(images: dict):
    set_val("slide_images", images)


def update_image(index: int, image_bytes: bytes):
    """Update a single slide's image."""
    images = get_images() or {}
    images[index] = image_bytes
    set_val("slide_images", images)


def get_pptx_path():
    return get("pptx_path")


def set_pptx_path(path):
    set_val("pptx_path", str(path) if path else None)
    _save_persisted()


def get_pdf_path():
    return get("pdf_path")


def set_pdf_path(path):
    set_val("pdf_path", path)


def set_progress(pct: int, status: str = ""):
    set_val("generation_progress", pct)
    if status:
        set_val("generation_status", status)


def reset():
    """Reset all state to defaults."""
    for key, default in _KEYS.items():
        st.session_state[key] = default
    try:
        if _PERSIST_FILE.exists():
            _PERSIST_FILE.unlink()
    except Exception:
        pass
