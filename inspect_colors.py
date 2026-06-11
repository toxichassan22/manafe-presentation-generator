import os
from pathlib import Path
from PIL import Image
import collections

IMAGE_DIR = Path(r"d:\workflow\pptx refrence")

def get_dominant_colors(img_path: Path, num_colors=5):
    try:
        img = Image.open(img_path)
        # Resize image to speed up color counting
        img = img.resize((150, 150))
        # Convert to RGB
        img = img.convert('RGB')
        
        pixels = list(img.getdata())
        # Count pixel occurrences
        counter = collections.Counter(pixels)
        most_common = counter.most_common(num_colors)
        
        print(f"\n--- Colors in {img_path.name} ---")
        for rgb, count in most_common:
            hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
            percentage = (count / len(pixels)) * 100
            print(f"  {hex_color} (RGB: {rgb}): {percentage:.1f}%")
            
    except Exception as e:
        print(f"Error reading {img_path.name}: {e}")

def main():
    if not IMAGE_DIR.exists():
        print(f"Directory not found: {IMAGE_DIR}")
        return
        
    slides = ["1.png", "2.png", "5.png", "10.png", "15.png", "41.png"]
    for s in slides:
        path = IMAGE_DIR / s
        if path.exists():
            get_dominant_colors(path)
        else:
            print(f"File not found: {s}")

if __name__ == "__main__":
    main()
