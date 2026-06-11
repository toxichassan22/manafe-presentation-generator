"""Branding module – company visual identity constants.
Centralizes colors, fonts, logo path, and company info for consistent PPTX output.

Values are loaded from config/branding.yaml when available, falling back to the
code defaults below. This allows non-developers to update brand assets by
editing the YAML file without touching Python code.
"""

from pathlib import Path

from pptx.util import Pt
from pptx.dml.color import RGBColor

from config.settings import PROJECT_ROOT
from ui.styles.tokens import tokens


def _hex_to_rgb(hex_str: str) -> RGBColor:
    """Convert '#RRGGBB' → RGBColor."""
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class CompanyBranding:
    """Company visual identity constants for presentations."""

    # ── Company Info ──
    COMPANY_NAME_AR: str = tokens.COMPANY_NAME_AR
    COMPANY_NAME_EN: str = tokens.COMPANY_NAME_EN
    COMPANY_TAGLINE_AR: str = tokens.COMPANY_TAGLINE_AR
    COMPANY_TAGLINE_EN: str = tokens.COMPANY_TAGLINE_EN

    # ── Logo ──
    LOGO_PATH: Path = PROJECT_ROOT / "assets" / "logo.png"

    # ── Color Palette ──
    PRIMARY_COLOR: RGBColor = _hex_to_rgb(tokens.PRIMARY)
    SECONDARY_COLOR: RGBColor = _hex_to_rgb(tokens.SECONDARY)
    ACCENT_COLOR: RGBColor = _hex_to_rgb(tokens.ACCENT)
    BACKGROUND_COLOR: RGBColor = _hex_to_rgb(tokens.SLIDE_BG)
    TEXT_COLOR_DARK: RGBColor = _hex_to_rgb(tokens.SLIDE_TEXT_DARK)
    TEXT_COLOR_LIGHT: RGBColor = _hex_to_rgb("#FFFFFF")
    TEXT_COLOR_MUTED: RGBColor = _hex_to_rgb(tokens.SLIDE_TEXT_MUTED)

    # Color HEX strings (for Streamlit CSS)
    PRIMARY_HEX: str = tokens.PRIMARY
    SECONDARY_HEX: str = tokens.SECONDARY
    ACCENT_HEX: str = tokens.ACCENT
    BACKGROUND_HEX: str = tokens.BG

    # ── Typography ──
    FONT_HEADING: str = tokens.FONT_HEADING
    FONT_BODY: str = tokens.FONT_BODY
    FONT_ENGLISH: str = tokens.FONT_ENGLISH
    FONT_SIZE_TITLE: Pt = Pt(tokens.FONT_SIZE_TITLE)
    FONT_SIZE_HEADING: Pt = Pt(tokens.FONT_SIZE_HEADING)
    FONT_SIZE_SUBHEADING: Pt = Pt(tokens.FONT_SIZE_SUBHEADING)
    FONT_SIZE_BODY: Pt = Pt(tokens.FONT_SIZE_BODY)
    FONT_SIZE_CAPTION: Pt = Pt(tokens.FONT_SIZE_CAPTION)

    # ── Slide Dimensions (Widescreen 16:9) ──
    SLIDE_WIDTH_INCHES: float = tokens.SLIDE_WIDTH_INCHES
    SLIDE_HEIGHT_INCHES: float = tokens.SLIDE_HEIGHT_INCHES

    # ── Footer ──
    FOOTER_TEXT_AR: str = tokens.FOOTER_TEXT_AR
    FOOTER_TEXT_EN: str = tokens.FOOTER_TEXT_EN


branding = CompanyBranding()
