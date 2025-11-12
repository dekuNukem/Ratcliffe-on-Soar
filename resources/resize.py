import os
import random
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageCms

TO_ADD = Path("to_add")
OUT_DIR = Path("resources/photos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_EDGE = 1024
WATERMARK_TEXT = "allen@500GX.com"
OPACITY = int(255 * 0.30)  # 25%

def ensure_srgb(img):
    """Convert to sRGB if the source has a non-sRGB ICC; return (img, icc_bytes)."""
    srgb_profile = ImageCms.createProfile("sRGB")
    icc_bytes = img.info.get("icc_profile")

    try:
        if icc_bytes:
            src = ImageCms.ImageCmsProfile(BytesIO(icc_bytes))
            # Convert only if not already sRGB
            # (name compare is a heuristic; if it fails, we’ll just convert anyway)
            try:
                src_name = ImageCms.getProfileName(src) or ""
            except Exception:
                src_name = ""
            if "srgb" not in src_name.lower():
                img = ImageCms.profileToProfile(img, src, srgb_profile, outputMode="RGB")
                icc_bytes = srgb_profile.tobytes()
            else:
                # Already sRGB; make sure mode is RGB for JPEG later
                if img.mode != "RGB":
                    img = img.convert("RGB")
                icc_bytes = icc_bytes  # keep original sRGB profile
        else:
            # No embedded profile. Assume current pixels are meant to be sRGB.
            if img.mode != "RGB":
                img = img.convert("RGB")
            icc_bytes = srgb_profile.tobytes()
    except Exception:
        # Fallback: at least ensure RGB; skip embedding profile if CMS fails
        img = img.convert("RGB")
        icc_bytes = None

    return img, icc_bytes

def resize_longest_edge(img, max_edge=MAX_EDGE):
    w, h = img.size
    longest = max(w, h)
    if longest <= max_edge:
        return img
    scale = max_edge / float(longest)
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.LANCZOS)

def add_watermark(img, text=WATERMARK_TEXT, opacity=OPACITY):
    # Work in RGBA for compositing
    base = img.convert("RGBA")
    w, h = base.size

    font_px = max(12, int(min(w, h) * 0.02))
    font = ImageFont.truetype("./resources/JetBrainsMono-Regular.ttf", font_px)

    # Measure
    dummy_draw = ImageDraw.Draw(base)
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    margin = max(2, font_px // 6)
    max_x = max(margin, w - tw - margin)
    max_y = max(margin, h - th - margin)
    # x = random.randint(margin, max_x)
    # y = random.randint(margin, max_y)
    x = 5
    y = 5

    # Pick white/black based on local brightness
    region = base.crop((x, y, x + tw, y + th)).convert("L")
    avg_brightness = sum(region.getdata()) / (tw * th)
    wm_color = (0, 0, 0, opacity) if avg_brightness > 128 else (255, 255, 255, opacity)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.text((x, y), text, font=font, fill=wm_color)

    out = Image.alpha_composite(base, overlay).convert("RGB")
    return out

def process_image(in_path: Path, out_path: Path):
    with Image.open(in_path) as im:
        exif = im.info.get("exif")  # keep EXIF if you want
        im = ImageOps.exif_transpose(im)

        # >>> Color management fix: normalize to sRGB and remember ICC
        im, icc_bytes = ensure_srgb(im)

        im = resize_longest_edge(im, MAX_EDGE)
        im = add_watermark(im, WATERMARK_TEXT, OPACITY)

        # Save as JPEG, embed profile, keep EXIF, and avoid heavy subsampling
        save_kwargs = {
            "format": "JPEG",
            "quality": 90,
            "optimize": True,
            "subsampling": 0,            # preserve chroma detail
        }
        if icc_bytes:
            save_kwargs["icc_profile"] = icc_bytes
        if exif:
            save_kwargs["exif"] = exif

        im.save(out_path, **save_kwargs)

def main():
    exts = {".jpg", ".jpeg"}
    for p in sorted(TO_ADD.iterdir()):
        if p.is_file() and p.suffix.lower() in exts:
            out_path = OUT_DIR / p.name
            if out_path.exists():
                print(f"Skipping (already exists): {out_path}")
                continue
            try:
                process_image(p, out_path)
                print(f"Saved: {out_path}")
            except Exception as e:
                print(f"Failed: {p} ({e})")

if __name__ == "__main__":
    main()
