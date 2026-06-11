"""
File Handler – upload/save helpers for images and output files.
"""

import logging
from pathlib import Path
from typing import Optional

from config.settings import settings

logger = logging.getLogger(__name__)


def save_upload(uploaded_file, filename: Optional[str] = None) -> Path:
    """Save a Streamlit UploadedFile to the outputs directory.

    Args:
        uploaded_file: Streamlit UploadedFile object.
        filename: Optional override filename.

    Returns:
        Path to the saved file.
    """
    name = filename or uploaded_file.name
    save_path = settings.OUTPUT_DIR / "uploads" / name
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    logger.info("Saved upload: %s (%d bytes)", save_path, save_path.stat().st_size)
    return save_path


def save_image(image_bytes: bytes, name: str) -> Path:
    """Save image bytes to the outputs/images directory.

    Args:
        image_bytes: Raw image bytes.
        name: Filename (e.g., 'slide_03.png').

    Returns:
        Path to the saved image.
    """
    save_path = settings.OUTPUT_DIR / "images" / name
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(image_bytes)

    logger.info("Saved image: %s (%d bytes)", save_path, len(image_bytes))
    return save_path


def get_output_path(project_name: str, ext: str = ".pptx") -> Path:
    """Generate a unique output file path.

    Args:
        project_name: Project name for the filename.
        ext: File extension (e.g., '.pptx', '.pdf').

    Returns:
        Path in the outputs directory.
    """
    from datetime import datetime

    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in project_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return settings.OUTPUT_DIR / f"{safe_name}_{timestamp}{ext}"


def read_file_bytes(path: Path) -> Optional[bytes]:
    """Read file bytes, returning None if file doesn't exist."""
    if path.exists():
        return path.read_bytes()
    return None
