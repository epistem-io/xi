import base64
import os

def image_to_base64(image_path):
    """Convert image to base64 string"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        print(f"Image not found: {image_path}")
        return None

# Convert banner to base64
banner_path = "logos/banner.png"
if os.path.exists(banner_path):
    base64_string = image_to_base64(banner_path)
    if base64_string:
        print("Base64 string for banner.png:")
        print(f"data:image/png;base64,{base64_string}")
    else:
        print("Failed to convert image")
else:
    print("Banner image not found")