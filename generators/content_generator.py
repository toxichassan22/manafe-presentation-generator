"""
Content Generator – orchestrates the LLM to write slide text and image prompts.
Now uses a two-step process: Outline Generation -> Slide Content Generation.
"""

import logging
from typing import Callable, Any

from services.llm_service import generate_json
from prompts.content_prompts import generate_outline_prompt, generate_slide_content_prompt

logger = logging.getLogger(__name__)


def _fallback_outline(num_slides: int) -> list[dict]:
    """Fallback outline that still respects the user's requested slide count."""
    if num_slides == 3:
        return [
            {"slide_type": "cover", "topic": "مقدمة المشروع وتحليل الأرض", "requires_image": True},
            {"slide_type": "standard", "topic": "الدور الأول على الأرض", "requires_image": True},
            {"slide_type": "standard", "topic": "التصميم الداخلي للدور الأول", "requires_image": True},
        ]

    outline = [
        {"slide_type": "cover", "topic": "غلاف المشروع", "requires_image": True},
        {"slide_type": "standard", "topic": "وصف المشروع", "requires_image": False},
        {"slide_type": "closing", "topic": "خاتمة", "requires_image": False},
    ]
    while len(outline) < num_slides:
        idx = len(outline) - 1
        outline.insert(idx, {
            "slide_type": "standard",
            "topic": f"تفاصيل إضافية {len(outline) - 1}",
            "requires_image": False,
        })
    return outline[:num_slides]


def generate_all_content(
    project_data: dict,
    land_analysis: dict,
    update_callback: Callable[[int, int, str, dict, str], None] = None
) -> list[dict]:
    """Generate all presentation content dynamically.

    Args:
        project_data: User-provided project specifics.
        land_analysis: Vision-service analysis of the land photo.
        update_callback: Optional callback fn(slide_idx, total_slides, slide_topic) to update UI.

    Returns:
        A list of dicts, each containing 'slide_type' and the generated text content.
    """
    slides = []
    
    # Merge land analysis into project data for better context
    context_data = dict(project_data)
    if land_analysis and land_analysis.get("terrain_type") != "unknown":
        context_data["land_analysis"] = land_analysis

    num_slides = context_data.get("num_slides", 15)
    
    logger.info("Generating outline for %d slides...", num_slides)
    if update_callback:
        update_callback(0, num_slides, "تخطيط هيكل العرض التقديمي...", None, None)

    # Step 1: Generate Outline
    sys_prompt, user_prompt = generate_outline_prompt(context_data, num_slides)
    try:
        def outline_stream_cb(chunk):
            if update_callback:
                update_callback(0, num_slides, "تخطيط هيكل العرض التقديمي...", None, chunk)
                
        outline = generate_json(sys_prompt, user_prompt, stream_callback=outline_stream_cb)
        if not isinstance(outline, list):
            # Sometimes the LLM wraps the array in an object like {"slides": [...]}
            if isinstance(outline, dict) and "slides" in outline:
                outline = outline["slides"]
            else:
                raise ValueError("Outline is not a list")
                
        # Clip to exactly the requested number of slides
        outline = outline[:num_slides]
    except Exception as e:
        logger.error("Failed to generate outline: %s", e)
        outline = _fallback_outline(num_slides)

    total_slides = len(outline)
    logger.info("Outline generated with %d slides.", total_slides)

    # Step 2: Generate Content for each slide
    for idx, slide_spec in enumerate(outline):
        topic = slide_spec.get("topic", f"شريحة {idx + 1}")
        slide_type = slide_spec.get("slide_type", "standard")
        
        logger.info("Generating slide %d/%d: %s (%s)", idx + 1, total_slides, topic, slide_type)
        
        if update_callback:
            update_callback(idx + 1, total_slides, f"كتابة شريحة: {topic}", None, None)

        sys_p, user_p = generate_slide_content_prompt(slide_spec, context_data)
        
        try:
            def slide_stream_cb(chunk):
                if update_callback:
                    update_callback(idx + 1, total_slides, f"كتابة شريحة: {topic}", None, chunk)
                    
            content = generate_json(sys_p, user_p, stream_callback=slide_stream_cb)
        except Exception as e:
            logger.error("Failed to generate slide %d: %s", idx + 1, e)
            content = {"title": topic, "error": str(e)}

        content["slide_type"] = slide_type
        content["slide_index"] = idx
        content["requires_image"] = slide_spec.get("requires_image", False)
        
        slides.append(content)
        
        if update_callback:
            update_callback(idx + 1, total_slides, f"تم كتابة شريحة: {topic}", content, None)

    logger.info("Generated content for %d slides", len(slides))
    return slides
