import os
import sys
from pathlib import Path
from PIL import Image
from google import genai

# Set output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

API_KEY = "AIzaSyA4-kAX7rTCfL4RXBtzP6f-zUvfZyQj7oo"
client = genai.Client(api_key=API_KEY)

IMAGE_DIR = Path(r"d:\workflow\pptx refrence")
OUTPUT_FILE = Path(__file__).parent / "first_few_analysis.txt"

def analyze_image(img_path: Path):
    print(f"\n--- Analyzing Slide {img_path.name} ---")
    try:
        img = Image.open(img_path)
        
        prompt = (
            "أنت خبير محترف في تصميم العروض التقديمية وتحليل تجربة المستخدم (UI/UX). "
            "قم بتحليل هذه الشريحة من عرض دراسة جدوى عقارية لشركة منافع الاقتصادية للعقار بالتفصيل. "
            "يرجى توفير:\n"
            "1. عنوان الشريحة وموضوعها الأساسي (Slide Title / Topic).\n"
            "2. الألوان المستخدمة للرموز والخلفية والنصوص بدقة (Hex codes if possible, or color names like Maroon, Gold, White, Dark Grey).\n"
            "3. الهيكل والتخطيط البصري (Layout & Structure): أين توجد النصوص والصور والجداول، وكيف يتم توزيع المساحة.\n"
            "4. العناصر البصرية والتصميمية (Visual Design Elements): مثل الأيقونات، الأشكال الهندسية، شبكة الخلفية، الخطوط المتداخلة، الشعارات.\n"
            "يرجى كتابة التحليل باللغة العربية باختصار وتركيز شديد."
        )
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[img, prompt]
        )
        
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n=========================================\n")
            f.write(f"Slide: {img_path.name}\n")
            f.write(response.text)
            f.write(f"\n=========================================\n")
            f.flush()
            
        print(f"✅ Slide {img_path.name} analysis appended to file.")
    except Exception as e:
        print(f"❌ Error analyzing {img_path.name}: {e}")

def main():
    # Clear output file first
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("Slide Analysis Output:\n")
        f.flush()
        
    slides_to_analyze = ["1.png", "2.png", "3.png", "5.png", "10.png"]
    for filename in slides_to_analyze:
        img_path = IMAGE_DIR / filename
        if img_path.exists():
            analyze_image(img_path)
        else:
            print(f"File {filename} not found in {IMAGE_DIR}")

if __name__ == "__main__":
    main()
