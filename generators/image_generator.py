"""Image generator orchestration with project-level visual identity locking."""

from __future__ import annotations

import logging
from typing import Optional

from services.image_gen_service import (
    generate_image,
    get_project_image_key,
    get_project_reference_image,
    get_project_slide_image,
    set_project_reference_image,
    set_project_slide_image,
)

logger = logging.getLogger(__name__)


def generate_all_images(
    project_data: dict,
    land_image_bytes: Optional[bytes],
    slide_contents: list[dict],
    update_callback=None,
) -> dict[int, bytes]:
    """Generate images for slides that requested them.

    The first generated image becomes the project's master reference. Later
    images are edited/anchored from that reference where the provider supports
    image-to-image generation, and the final bytes are saved per slide so
    rebuilds do not change the pictures.
    """
    images: dict[int, bytes] = {}
    total_slides = len(slide_contents)
    project_image_key = get_project_image_key(project_data)
    project_reference_image = get_project_reference_image(project_image_key)

    if project_reference_image is None and land_image_bytes is not None:
        try:
            set_project_reference_image(project_image_key, land_image_bytes)
            project_reference_image = get_project_reference_image(project_image_key)
            logger.info("Project master reference image locked with land_image_bytes reference.")
        except Exception as ref_err:
            logger.error("Failed to set reference image in generate_all_images: %s", ref_err)

    import hashlib
    project_seed = int(hashlib.sha256(project_image_key.encode("utf-8")).hexdigest()[:8], 16) % 1000000000

    is_commercial = False
    for val in project_data.values():
        if isinstance(val, str) and any(kw in val.lower() for kw in [
            "تجاري", "إداري", "إداريه", "تجاريه", "مكتب", "برج", "عمارة", "مجمع", "مكاتب", "أبراج",
            "commercial", "office", "administrative", "tower", "complex", "building"
        ]):
            is_commercial = True
            break

    for slide in slide_contents:
        slide_idx = slide.get("slide_index", 0)
        topic = slide.get("title", f"Slide {slide_idx}")
        req_image = slide.get("requires_image", False)
        img_prompt = slide.get("image_prompt", "")

        if not req_image or not img_prompt:
            continue

        logger.info("Generating image for slide %d: %s", slide_idx, img_prompt[:80])

        if update_callback:
            update_callback(slide_idx, total_slides, f"رسم صورة لشريحة: {topic}")

        try:
            cached_img = get_project_slide_image(project_image_key, slide_idx)
            if cached_img:
                img_bytes = cached_img
                logger.info("Using locked project image for slide %d", slide_idx)
            else:
                slide_seed = (project_seed + slide_idx) % 1000000000
                img_bytes = generate_image(prompt=img_prompt, reference_image=project_reference_image, seed=slide_seed, is_commercial=is_commercial)
                set_project_slide_image(project_image_key, slide_idx, img_bytes)

            if project_reference_image is None:
                set_project_reference_image(project_image_key, img_bytes)
                project_reference_image = get_project_reference_image(project_image_key) or img_bytes

            images[slide_idx] = img_bytes
            logger.info("Image ready for slide %d: %d bytes", slide_idx, len(img_bytes))

            if update_callback:
                update_callback(slide_idx, total_slides, f"تم تجهيز الصورة لشريحة: {topic}", img_bytes)

        except Exception as e:
            logger.error("Failed to generate image for slide %d: %s", slide_idx, e)
            if update_callback:
                update_callback(slide_idx, total_slides, f"⚠️ فشل توليد صورة شريحة: {topic}")

    logger.info("Generated %d images total", len(images))
    return images


def _slide_text(slide: dict) -> str:
    content = slide.get("content") if isinstance(slide.get("content"), dict) else slide
    parts: list[str] = []
    for key in ("title", "description", "subtitle", "summary", "concept", "message", "vision"):
        if content.get(key):
            parts.append(str(content[key]))
    for key in ("bullets", "highlights", "key_features", "features", "materials"):
        items = content.get(key)
        if isinstance(items, list):
            parts.extend(str(item) for item in items[:6])
    return "\n".join(parts)


def regenerate_image(
    slide_idx: int,
    project_data: dict,
    land_image_bytes: Optional[bytes],
    slide_contents: list[dict],
    existing_images: Optional[dict[int, bytes]] = None,
) -> Optional[bytes]:
    """Regenerate one image as an edit of the saved project master reference."""
    if not slide_contents or slide_idx < 0 or slide_idx >= len(slide_contents):
        return None

    slide = slide_contents[slide_idx]
    img_prompt = slide.get("image_prompt") or _slide_text(slide)
    if not img_prompt:
        return None

    project_image_key = get_project_image_key(project_data)
    reference_image = get_project_reference_image(project_image_key)

    if reference_image is None and existing_images:
        first_key = sorted(existing_images.keys())[0]
        reference_image = existing_images[first_key]
        set_project_reference_image(project_image_key, reference_image)
        reference_image = get_project_reference_image(project_image_key) or reference_image

    if existing_images and slide_idx in existing_images:
        reference_image = reference_image or existing_images[slide_idx]

    import hashlib
    project_seed = int(hashlib.sha256(project_image_key.encode("utf-8")).hexdigest()[:8], 16) % 1000000000
    slide_seed = (project_seed + slide_idx) % 1000000000

    is_commercial = False
    for val in project_data.values():
        if isinstance(val, str) and any(kw in val.lower() for kw in [
            "تجاري", "إداري", "إداريه", "تجاريه", "مكتب", "برج", "عمارة", "مجمع", "مكاتب", "أبراج",
            "commercial", "office", "administrative", "tower", "complex", "building"
        ]):
            is_commercial = True
            break

    img_bytes = generate_image(prompt=img_prompt, reference_image=reference_image, seed=slide_seed, is_commercial=is_commercial)
    set_project_slide_image(project_image_key, slide_idx, img_bytes)

    if get_project_reference_image(project_image_key) is None:
        set_project_reference_image(project_image_key, img_bytes)

    logger.info("Regenerated locked-reference image for slide %d: %d bytes", slide_idx, len(img_bytes))
    return img_bytes
