# requirements: pip install pillow
import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

TO_ADD = Path("to_add")
OUT_DIR = Path("photos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_EDGE = 1024
WATERMARK_TEXT = "example"
OPACITY =  int(255 * 0.25)  # 25%

def resize_longest_edge(img, max_edge=MAX_EDGE):
    w, h = img.size
    longest = max(w, h)
    if longest <= max_edge:
        return img
    scale = max_edge / float(longest)
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.LANCZOS)

def add_watermark(img, text=WATERMARK_TEXT, opacity=OPACITY):
    # Ensure RGBA for alpha compositing
    base = img.convert("RGBA")
    w, h = base.size

    # Font size ~ 2.5% of the shortest edge, at least 12px
    font_px = max(12, int(min(w, h) * 0.025))
    font = ImageFont.truetype("./resources/JetBrainsMono-Regular.ttf", font_px)

    # Measure text box
    dummy_draw = ImageDraw.Draw(base)
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Random position (keep a tiny margin so it stays fully visible)
    margin = max(2, font_px // 6)
    max_x = max(margin, w - tw - margin)
    max_y = max(margin, h - th - margin)
    x = random.randint(margin, max_x)
    y = random.randint(margin, max_y)

    # ----
    region = base.crop((x, y, x + tw, y + th)).convert("L")  # grayscale
    avg_brightness = sum(region.getdata()) / (tw * th)
    if avg_brightness > 128:
        wm_color = (0, 0, 0, opacity)  # dark text on light bg
    else:
        wm_color = (255, 255, 255, opacity)  # light text on dark bg
    # ----

    # Draw text on its own transparent layer
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.text((x, y), text, font=font, fill=wm_color)

    # Composite and return back to RGB for JPEG
    watermarked = Image.alpha_composite(base, overlay).convert("RGB")
    return watermarked

def process_image(in_path: Path, out_path: Path):
    with Image.open(in_path) as im:
        # Fix orientation from EXIF if present
        im = ImageOps.exif_transpose(im)
        im = resize_longest_edge(im, MAX_EDGE)
        im = add_watermark(im, WATERMARK_TEXT, OPACITY)
        # Save with original file name in JPEG format
        im.save(out_path, format="JPEG", quality=90, optimize=True)

def main():
    exts = {".jpg", ".jpeg"}
    for p in sorted(TO_ADD.iterdir()):
        if p.is_file() and p.suffix.lower() in exts:
            out_path = OUT_DIR / p.name
            try:
                process_image(p, out_path)
                print(f"Saved: {out_path}")
            except Exception as e:
                print(f"Failed: {p} ({e})")

if __name__ == "__main__":
    main()
