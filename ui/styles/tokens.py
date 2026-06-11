"""Design tokens — single source of truth for UI styling values.

Reads from config/branding.yaml and exposes typed properties for colors,
spacing, typography, shadows, and breakpoints.
"""

from pathlib import Path
from typing import Any

import yaml

_YAML_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "branding.yaml"


def _load_yaml() -> dict[str, Any]:
    if _YAML_PATH.exists():
        with open(_YAML_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


_data = _load_yaml()
_colors = _data.get("colors", {})
_ui = _data.get("ui", {})
_fonts = _data.get("fonts", {})
_sizes = _data.get("sizes", {})
_company = _data.get("company", {})
_footer = _data.get("footer", {})
_slide = _data.get("slide", {})


class DesignTokens:
    """Centralized design tokens for the web application UI."""

    # ── Company ──
    COMPANY_NAME_AR: str = _company.get("name_ar", "شركة التطوير العقاري")
    COMPANY_NAME_EN: str = _company.get("name_en", "Real Estate Development Co.")
    COMPANY_TAGLINE_AR: str = _company.get("tagline_ar", "نبني المستقبل")
    COMPANY_TAGLINE_EN: str = _company.get("tagline_en", "Building the Future")

    # ── Corporate Color Palette ──
    PRIMARY: str = _colors.get("primary", "#D946EF")
    SECONDARY: str = _colors.get("secondary", "#8B5CF6")
    ACCENT: str = _colors.get("accent", "#F43F5E")

    BG: str = _colors.get("background", "#08020F")
    SURFACE: str = _ui.get("surface", "#11071F")
    SURFACE_RAISED: str = _ui.get("surface_raised", "#1B0D30")
    SURFACE_INSET: str = _ui.get("surface_inset", "#040108")

    TEXT_PRIMARY: str = _ui.get("text_primary", "#F8FAFC")
    TEXT_SECONDARY: str = _ui.get("text_secondary", "#CBD5E1")
    TEXT_TERTIARY: str = _ui.get("text_tertiary", "#94A3B8")

    BORDER: str = _ui.get("border", "#261142")
    BORDER_STRONG: str = _ui.get("border_strong", "#3B1E64")

    SUCCESS: str = _ui.get("success", "#10B981")
    WARNING: str = _ui.get("warning", "#F59E0B")
    ERROR: str = _ui.get("error", "#EF4444")

    # ── Typography ──
    FONT_HEADING: str = _fonts.get("heading", "Cairo")
    FONT_BODY: str = _fonts.get("body", "Cairo")
    FONT_ENGLISH: str = _fonts.get("english", "Inter")

    FONT_SIZE_TITLE: int = _sizes.get("title", 44)
    FONT_SIZE_HEADING: int = _sizes.get("heading", 28)
    FONT_SIZE_SUBHEADING: int = _sizes.get("subheading", 20)
    FONT_SIZE_BODY: int = _sizes.get("body", 16)
    FONT_SIZE_CAPTION: int = _sizes.get("caption", 12)

    # ── Spacing (px) ──
    SPACE_1: int = _ui.get("space_1", 4)
    SPACE_2: int = _ui.get("space_2", 8)
    SPACE_3: int = _ui.get("space_3", 12)
    SPACE_4: int = _ui.get("space_4", 16)
    SPACE_5: int = _ui.get("space_5", 24)
    SPACE_6: int = _ui.get("space_6", 32)
    SPACE_7: int = _ui.get("space_7", 48)
    SPACE_8: int = _ui.get("space_8", 64)

    # ── Radii ──
    RADIUS_SM: str = _ui.get("radius_sm", "6px")
    RADIUS_MD: str = _ui.get("radius_md", "8px")
    RADIUS_LG: str = _ui.get("radius_lg", "12px")
    RADIUS_XL: str = _ui.get("radius_xl", "16px")
    RADIUS_FULL: str = _ui.get("radius_full", "999px")

    # ── Shadows ──
    SHADOW_SM: str = _ui.get("shadow_sm", "0 1px 2px 0 rgba(0,0,0,0.20)")
    SHADOW_MD: str = _ui.get(
        "shadow_md",
        "0 4px 6px -1px rgba(0,0,0,0.20), 0 2px 4px -1px rgba(0,0,0,0.10)",
    )
    SHADOW_LG: str = _ui.get(
        "shadow_lg",
        "0 10px 15px -3px rgba(0,0,0,0.30), 0 4px 6px -2px rgba(0,0,0,0.20)",
    )

    # ── Breakpoints ──
    BP_MOBILE: int = _ui.get("bp_mobile", 640)
    BP_TABLET: int = _ui.get("bp_tablet", 768)
    BP_DESKTOP: int = _ui.get("bp_desktop", 1024)
    BP_WIDE: int = _ui.get("bp_wide", 1280)

    # ── Layout ──
    MAX_CONTENT_WIDTH: str = _ui.get("max_content_width", "1280px")
    PAGE_PADDING: str = _ui.get("page_padding", "24px")

    # ── Slide / PPTX ──
    SLIDE_WIDTH_INCHES: float = _slide.get("width_inches", 13.333)
    SLIDE_HEIGHT_INCHES: float = _slide.get("height_inches", 7.5)
    SLIDE_BG: str = _slide.get("background", "#FFFFFF")
    SLIDE_TEXT_DARK: str = _slide.get("text_dark", "#1E293B")
    SLIDE_TEXT_MUTED: str = _slide.get("text_muted", "#64748B")

    # ── Footer ──
    FOOTER_TEXT_AR: str = _footer.get("text_ar", "سري وخاص - جميع الحقوق محفوظة")
    FOOTER_TEXT_EN: str = _footer.get("text_en", "Confidential - All Rights Reserved")

    # ── Derived / Helpers ──
    @property
    def primary_dim(self) -> str:
        r, g, b = self._hex_to_rgb_tuple(self.PRIMARY)
        return f"rgba({r}, {g}, {b}, 0.12)"

    @property
    def secondary_dim(self) -> str:
        r, g, b = self._hex_to_rgb_tuple(self.SECONDARY)
        return f"rgba({r}, {g}, {b}, 0.12)"

    @staticmethod
    def _hex_to_rgb_tuple(hex_str: str) -> tuple[int, int, int]:
        h = hex_str.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


tokens = DesignTokens()
