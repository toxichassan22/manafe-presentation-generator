import os
from generators.pptx_builder import build_presentation

with open('assets/dummy_building.jpg', 'rb') as f:
    img_bytes = f.read()

slides_data = [
    {
        'slide_type': 'cover', 
        'content': {'title': 'دراسة الجدوى الأولية لمشروع تجاري اداري', 'subtitle': 'شركة منافع الاقتصادية للعقار'}
    },
    {
        'slide_type': 'section',
        'content': {'title': 'نظرة على اقتصاد المملكة'}
    },
    {
        'slide_type': 'standard',
        'content': {
            'title': 'القطاع غير النفطي والتنويع الاقتصادي', 
            'bullets': [
                'من المتوقع أن يسجل القطاع غير النفطي نموًا سنويًا',
                'الخدمات المالية والتقنية والسياحة تقود هذا النمو',
                'الاستثمارات الأجنبية المباشرة تجاوزت التوقعات',
            ]
        }
    }
]

images = {
    0: img_bytes,
    1: img_bytes
}

prs_path = build_presentation(slides_data, images)
print(f"Generated: {prs_path}")
os.system(f'start "" "{prs_path}"')
