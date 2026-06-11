"""Full pipeline test — outline + slides + pptx build."""
import json
import logging
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)

from generators.content_generator import generate_all_content
from generators.pptx_builder import build_presentation

project_data = {
    "project_name": "مشروع منافع التجاري",
    "location": "جدة",
    "building_description": "مجمع تجاري وإداري متكامل",
    "building_style": "modern",
    "floors": 10,
    "budget": "50 مليون ريال",
    "num_slides": 8,
}

land_analysis = {"terrain_type": "flat", "surroundings": "urban"}

def progress(idx, total, msg, data=None, stream=None):
    print(f"  [{idx}/{total}] {msg}")

print("=== Step 1: Generating content ===")
slides = generate_all_content(project_data, land_analysis, update_callback=progress)
print(f"Generated {len(slides)} slides")

for s in slides:
    title = s.get("title", "?")
    stype = s.get("slide_type", "?")
    has_img_prompt = bool(s.get("image_prompt"))
    print(f"  Slide {s.get('slide_index')}: [{stype}] {title} (img_prompt: {has_img_prompt})")

with open("test_slides.json", "w", encoding="utf-8") as f:
    json.dump(slides, f, ensure_ascii=False, indent=2)

print("\n=== Step 2: Building PPTX ===")
out_path = build_presentation(slides, {}, "Test_Project")
print(f"SUCCESS! File saved: {out_path}")
