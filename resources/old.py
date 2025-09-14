import os
import random
from PIL import Image, ImageDraw, ImageFont

# Folder containing input images
input_folder = "photos"

# Ensure the folder exists
if not os.path.isdir(input_folder):
    raise FileNotFoundError(f"Folder '{input_folder}' does not exist.")

# Loop through files
for file_name in os.listdir(input_folder):
    if file_name.lower().endswith((".jpg", ".jpeg")):
        input_path = os.path.join(input_folder, file_name)

        # Open image
        image = Image.open(input_path).convert("RGBA")

        # Resize to longest edge = 1024
        width, height = image.size
        scale = 1024 / max(width, height)
        new_size = (int(width * scale), int(height * scale))
        image = image.resize(new_size, Image.LANCZOS)

        # Create a transparent overlay
        txt_overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_overlay)

        # Load a font (fall back to default if not available)
        font_size = int(min(image.size) / 10)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text = "example"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # Pick random position where text fully fits
        max_x = image.width - text_w
        max_y = image.height - text_h
        pos = (random.randint(0, max_x), random.randint(0, max_y))

        # Draw text with ~50% opacity
        draw.text(pos, text, fill=(255, 255, 255, 64), font=font)

        # Merge overlay with image
        watermarked = Image.alpha_composite(image, txt_overlay)

        # Convert back to JPEG (no alpha channel)
        watermarked = watermarked.convert("RGB")

        # Save with "output" appended
        base, ext = os.path.splitext(file_name)
        output_name = f"{base}_output.jpg"
        output_path = os.path.join(input_folder, output_name)
        watermarked.save(output_path, "JPEG", quality=95)

        print(f"Processed: {output_name}")
