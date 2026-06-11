import os
from PIL import Image, ImageDraw

os.makedirs('assets', exist_ok=True)

# 1. Create Gradient Overlay (Transparent to #670D0C)
width, height = 1920, 1080
gradient = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(gradient)

# Maroon color: #670D0C -> RGB(103, 13, 12)
for x in range(width):
    # Alpha goes from 0 on the left to 240 (out of 255) on the right
    alpha = int((x / width) * 240)
    draw.line([(x, 0), (x, height)], fill=(103, 13, 12, alpha))

gradient.save('assets/gradient_overlay.png')

# 2. Create Geometric Pattern Overlay
# A simple transparent image with some faint white/grey triangles
pattern = Image.new('RGBA', (width, height), (0, 0, 0, 0))
p_draw = ImageDraw.Draw(pattern, 'RGBA')

def draw_triangle(p1, p2, p3, fill):
    p_draw.polygon([p1, p2, p3], fill=fill)

# Draw some triangles in the corners (semi-transparent white)
fill_color = (255, 255, 255, 30)
draw_triangle((0, height), (400, height), (0, height-400), fill_color)
draw_triangle((0, height), (600, height), (0, height-600), (255, 255, 255, 15))

draw_triangle((width, 0), (width-500, 0), (width, 500), fill_color)
draw_triangle((width, 0), (width-700, 0), (width, 700), (255, 255, 255, 15))

pattern.save('assets/pattern.png')

print("Assets created successfully in assets/ folder.")
