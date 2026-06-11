"""
PDF Exporter – converts PPTX to PDF via LibreOffice subprocess.
Falls back gracefully if LibreOffice is not installed.
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _find_libreoffice() -> Optional[str]:
    """Find the LibreOffice soffice executable."""
    # Check common paths
    candidates = [
        shutil.which("soffice"),
        shutil.which("libreoffice"),
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "/usr/bin/soffice",
        "/usr/bin/libreoffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def export_to_pdf(pptx_path: Path) -> Optional[Path]:
    """Convert a PPTX file to PDF using LibreOffice.

    Args:
        pptx_path: Path to the .pptx file.

    Returns:
        Path to the generated .pdf file, or None if conversion failed.

    Note:
        Requires LibreOffice to be installed on the system.
        Install on Windows: https://www.libreoffice.org/download/
        Install on Ubuntu: sudo apt install libreoffice
    """
    soffice = _find_libreoffice()
    if not soffice:
        logger.warning(
            "LibreOffice not found. PDF export requires LibreOffice. "
            "Install from https://www.libreoffice.org/download/"
        )
        return None

    output_dir = pptx_path.parent
    try:
        logger.info("Converting %s to PDF...", pptx_path.name)
        result = subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(output_dir),
                str(pptx_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            logger.error("LibreOffice conversion failed: %s", result.stderr)
            return None

        # Output PDF has same name but .pdf extension
        pdf_path = output_dir / f"{pptx_path.stem}.pdf"
        if pdf_path.exists():
            logger.info("PDF exported: %s", pdf_path)
            return pdf_path
        else:
            logger.error("PDF file not found after conversion")
            return None

    except subprocess.TimeoutExpired:
        logger.error("LibreOffice conversion timed out")
        return None
    except Exception as e:
        logger.error("PDF export error: %s", e)
        return None
