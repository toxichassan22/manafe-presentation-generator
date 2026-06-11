import os, sys
from config.settings import settings
from services.llm_service import generate_json
from prompts.content_prompts import generate_outline_prompt

project_data = {
    "project_name": "مشروع تجريبي",
    "description": "مبنى سكني 10 ادوار",
    "floor_distribution": "الدور الارضي محلات, الادوار 1-8 شقق, السطح مسبح",
    "language": "العربية",
    "num_slides": 8
}
docs_images = []

context_parts = []
if project_data.get("project_name"):
    context_parts.append("اسم المشروع: " + project_data["project_name"])
if project_data.get("description"):
    context_parts.append("الوصف: " + project_data["description"])
if project_data.get("floor_distribution"):
    context_parts.append("توزيع الأدوار: " + project_data["floor_distribution"])
if project_data.get("language"):
    context_parts.append("لغة العرض: " + project_data["language"])

import sys
sys.stdout.reconfigure(encoding='utf-8')

full_context = "\n".join(context_parts)
sys_p, usr_p = generate_outline_prompt(context_data=full_context, num_slides=8)

print("Context:", full_context[:300])
print("---")

_TYPE_ICONS = {
    "cover": "🏠", "section_header": "📌", "standard": "📄",
    "two_column": "⚖️", "timeline": "🗓️", "swot": "🔍",
    "map": "📍", "chart": "📊", "closing": "🎯",
}

chunks = []
def _outline_stream_cb(raw_text):
    chunks.append(len(raw_text))
    import re
    topics = re.findall(r'"topic"\s*:\s*"([^"]+)"', raw_text)
    types  = re.findall(r'"slide_type"\s*:\s*"([^"]+)"', raw_text)

    if not topics:
        return

    num_expected = project_data.get("num_slides", 8)
    progress_pct = min(100, int(len(topics) / num_expected * 100))

    rows_html = ""
    for i, topic in enumerate(topics):
        stype = types[i] if i < len(types) else "standard"
        icon  = _TYPE_ICONS.get(stype, "📄")
        is_last = (i == len(topics) - 1)

        cursor = (
            "|" if is_last else ""
        )

        rows_html += f"Slide {i+1}: {icon} {topic} {cursor}\n"

try:
    res = generate_json(sys_p, usr_p, stream_callback=_outline_stream_cb, images=None)
    print("Type:", type(res))
    if isinstance(res, dict) and "slides" in res:
        slides = res["slides"]
    elif isinstance(res, list):
        slides = res
    else:
        raise ValueError("Unexpected JSON: " + str(type(res)) + " -> " + str(res)[:200])
    print("SUCCESS:", len(slides), "slides,", len(chunks), "streaming chunks")
    for s in slides:
        print(" -", s.get("slide_type"), ":", s.get("topic"))
except Exception as e:
    print("ERROR:", e)
    import traceback
    traceback.print_exc()
