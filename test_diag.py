"""Quick diagnostic — test outline + single slide generation."""
import json
import logging
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from services.llm_service import generate_json

logging.basicConfig(level=logging.INFO)

# Test 1: Outline
print("=== TEST 1: Outline ===")
project_data = {
    "project_name": "Test Commercial",
    "location": "Jeddah",
    "building_description": "Commercial complex",
    "building_style": "modern",
    "floors": 10,
    "budget": "50M SAR",
    "num_slides": 5,
}

from prompts.content_prompts import generate_outline_prompt, generate_slide_content_prompt

sys_p, usr_p = generate_outline_prompt(project_data, 5)

try:
    outline = generate_json(sys_p, usr_p)
    print("Outline type:", type(outline))
    if isinstance(outline, list):
        print("Outline length:", len(outline))
        for i, item in enumerate(outline):
            print(f"  [{i}] type={item.get('slide_type')}, topic={item.get('topic')}, img={item.get('requires_image')}")
    elif isinstance(outline, dict):
        print("Keys:", list(outline.keys()))
        if "slides" in outline:
            print("Has 'slides' key, length:", len(outline["slides"]))
        print(json.dumps(outline, ensure_ascii=False, indent=2)[:600])
except Exception as e:
    print("ERROR:", type(e).__name__, e)

# Test 2: Single slide
print("\n=== TEST 2: Single Slide ===")
slide_spec = {"slide_type": "standard", "topic": "Project Description", "requires_image": False}
sys_p2, usr_p2 = generate_slide_content_prompt(slide_spec, project_data)

try:
    slide = generate_json(sys_p2, usr_p2)
    print("Slide type:", type(slide))
    print("Keys:", list(slide.keys()))
    print(json.dumps(slide, ensure_ascii=False, indent=2)[:400])
except Exception as e:
    print("ERROR:", type(e).__name__, e)
