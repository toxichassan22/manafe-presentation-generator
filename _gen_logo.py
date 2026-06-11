"""Generate base64 logo module."""
import base64
import os

logo_path = r"D:\workflow\real-estate-proposal-generator\assets\logo.webp"
output_path = r"D:\workflow\real-estate-proposal-generator\assets\__init__.py"

os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(logo_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

with open(output_path, "w", encoding="utf-8") as f:
    f.write(f'"""Company logo as base64 data URI."""\n')
    f.write(f'LOGO_B64 = "data:image/webp;base64,{b64}"\n')

print(f"Done! Base64 length: {len(b64)} chars")
print(f"Output: {output_path}")
