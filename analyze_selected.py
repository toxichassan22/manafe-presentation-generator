import os
import sys
import time
from pathlib import Path
from PIL import Image
from google import genai

# Set output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# API Key
API_KEY = "AIzaSyA4-kAX7rTCfL4RXBtzP6f-zUvfZyQj7oo"
client = genai.Client(api_key=API_KEY)

IMAGE_DIR = Path(r"d:\workflow\pptx refrence")
OUTPUT_FILE = Path(__file__).parent / "design_analysis.md"

def analyze_image(img_path: Path) -> str:
    print(f"⏳ Analyzing Slide {img_path.name}...")
    try:
        img = Image.open(img_path)
        
        prompt = (
            "أنت خبير محترف في تصميم العروض التقديمية وتحليل تجربة المستخدم (UI/UX). "
            "قم بتحليل هذه الشريحة من عرض دراسة جدوى عقارية لشركة منافع الاقتصادية للعقار بالتفصيل الشديد. "
            "يرجى توفير:\n"
            "1. عنوان الشريحة وموضوعها الأساسي (Slide Title / Topic).\n"
            "2. الهيكل والتخطيط البصري (Layout & Structure): أين توجد النصوص والصور والجداول، وكيف يتم توزيع المساحة.\n"
            "3. الألوان والخطوط (Colors & Typography): الألوان المستخدمة للنصوص والخلفيات والعناصر بالتفصيل مع ذكر المسميات (مثل: أحمر داكن/عنابي، أبيض، ذهبي، رمادي)، وأحجام الخطوط وأنواعها.\n"
            "4. العناصر البصرية والتصميمية (Visual Design Elements): مثل الأيقونات، الأشكال الهندسية، شبكة الخلفية، الخطوط المتداخلة، الشعارات.\n"
            "5. نوع البيانات المعروضة (Content Summary): هل هي نقاط رئيسية، جداول مالية، رسم بياني، تحليل SWOT، إلخ.\n"
            "يرجى كتابة التحليل باللغة العربية بأسلوب احترافي وواضح وسريع التركيز."
        )
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[img, prompt]
        )
        print(f"✅ Successfully analyzed Slide {img_path.name}")
        return response.text
    except Exception as e:
        print(f"❌ Error analyzing Slide {img_path.name}: {e}")
        return f"Error: {e}"

def main():
    if not IMAGE_DIR.exists():
        print(f"❌ IMAGE_DIR not found: {IMAGE_DIR}")
        return
        
    # We analyze a representative set of key slides:
    # 1: Cover
    # 2: Executive Summary / Intro
    # 5: Project concept or general layout
    # 10: Section Divider / Transition slide
    # 15: Table / Analysis layout
    # 25: Financial / Excel Table layout
    # 30: Charts / Visualization layout
    # 41: Closing slide
    selected_slides = [1, 2, 5, 10, 15, 25, 30, 41]
    
    print(f"Starting sequential analysis of {len(selected_slides)} selected slides with 13s cooldown to respect API limits...")
    
    # Initialize output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# التفصيل الشامل لتصميم العرض العقاري لشركة منافع (Manafe)\n\n")
        f.write("هذا التحليل يستعرض الهوية البصرية والتخطيط للشرائح الرئيسية لإنتاج قالب PPTX فائق الجودة والجمال.\n\n")
        f.flush()

    for idx, slide_num in enumerate(selected_slides):
        filename = f"{slide_num}.png"
        img_path = IMAGE_DIR / filename
        
        if not img_path.exists():
            print(f"⚠️ Slide {filename} not found, skipping...")
            continue
            
        analysis = analyze_image(img_path)
        
        # Append immediately
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"## Slide {slide_num} ({filename})\n\n")
            f.write(analysis)
            f.write("\n\n---\n\n")
            f.flush()
            
        # If not the last slide, sleep for 13 seconds to stay under 5 RPM limit
        if idx < len(selected_slides) - 1:
            print("Cooldown for 13 seconds...")
            time.sleep(13)
            
    print(f"🎉 Complete! Analysis saved in: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
