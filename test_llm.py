from services.llm_service import generate_json

result = generate_json(
    "You are a presentation expert. Output valid JSON only.",
    'Create a short slide. Return JSON: {"title": "Test", "description": "A test slide."}'
)
print("SUCCESS:", result)
