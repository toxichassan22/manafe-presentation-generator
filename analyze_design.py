import os
import json
import time
import sys
from pathlib import Path
from PIL import Image
from google import genai
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Verified API key from imagen_studio.py
API_KEY = "AIzaSyA4-kAX7rTCfL4RXBtzP6f-zUvfZyQj7oo"
client = genai.Client(api_key=API_KEY)

IMAGE_DIR = Path(r"d:\workflow\pptx refrence")
OUTPUT_FILE = Path(__file__).parent / "design_analysis.md"

def analyze_image(img_path: Path) -> dict:
    print(f"⏳ جاري تحليل الشريحة رقم {img_path.stem}...")
    try:
        img = Image.open(img_path)
        
        prompt = (
            "أنت خبير محترف في تصميم العروض التقديمية وتحليل تجربة المستخدم (UI/UX). "
            "قم بتحليل هذه الشريحة من عرض دراسة جدوى عقارية لشركة منافع الاقتصادية للعقار بالتفصيل الشديد. "
            "يرجى توفير:\n"
            "1. عنوان الشريحة وموضوعها الأساسي (Slide Title / Topic).\n"
            "2. الهيكل والتخطيط البصري (Layout & Structure): أين توجد النصوص والصور والجداول، وكيف يتم توزيع المساحة.\n"
            "3. الألوان والخطوط (Colors & Typography): الألوان المستخدمة للنصوص والخلفيات والعناصر (Maroon, White, Gold, etc.)، وأحجام الخطوط وأنواعها.\n"
            "4. العناصر البصرية والتصميمية (Visual Design Elements): مثل الأيقونات، الأشكال الهندسية، شبكة الخلفية، الخطوط المتداخلة، الشعارات.\n"
            "5. نوع البيانات المعروضة (Content Summary): هل هي نقاط رئيسية، جداول مالية، رسم بياني، تحليل SWOT، إلخ.\n"
            "يرجى كتابة التحليل باللغة العربية بأسلوب احترافي وواضح."
        )
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[img, prompt]
        )
        
        print(f"✅ تم الانتهاء من الشريحة رقم {img_path.stem}!")
        return {
            "file": img_path.name,
            "number": int(img_path.stem),
            "analysis": response.text
        }
    except Exception as e:
        print(f"❌ خطأ في تحليل الشريحة {img_path.name}: {e}")
        return {"file": img_path.name, "number": int(img_path.stem), "analysis": f"Error: {e}"}

def main():
    if not IMAGE_DIR.exists():
        print(f"❌ المجلد غير موجود: {IMAGE_DIR}")
        return

    images = list(IMAGE_DIR.glob("*.png"))
    images.sort(key=lambda p: int(p.stem))
    
    print(f"تم العثور على {len(images)} شريحة لتحليلها.")
    
    # Initialize the output file with headers
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# التفصيل الشامل لتصميم العرض العقاري (Manafe)\n\n")
        f.write("هذا التحليل يستعرض 41 شريحة بالتفصيل الممل لبناء نظام يولد عروضاً تتفوق عليها في الجودة.\n\n")
        f.flush()

    results = {}
    
    # 4 concurrent workers is optimal for gemini-2.5-flash
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(analyze_image, img): img for img in images}
        for future in as_completed(futures):
            res = future.result()
            results[res["number"]] = res
            
            # Write immediately to show progressive results
            print(f"✍️ حفظ نتيجة الشريحة {res['number']} في الملف...")
            
            # Re-write the whole file in order so it's always ordered
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("# التفصيل الشامل لتصميم العرض العقاري (Manafe)\n\n")
                f.write("هذا التحليل يستعرض 41 شريحة بالتفصيل الممل لبناء نظام يولد عروضاً تتفوق عليها في الجودة.\n\n")
                for i in sorted(results.keys()):
                    r = results[i]
                    f.write(f"## Slide {r['number']} ({r['file']})\n")
                    f.write(r["analysis"])
                    f.write("\n\n---\n\n")
                f.flush()
                
            time.sleep(0.2)
            
    print(f"✅ تم الانتهاء بالكامل وحفظ جميع النتائج بنجاح في: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
