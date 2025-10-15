# sample generator placeholder
# samples/generate_sample.py
"""
Generates simple synthetic sample images with product labels and Code128 barcodes.
Perfect for testing OCR + barcode extraction without real product photos.
"""

import os
import io
from PIL import Image, ImageDraw, ImageFont
from barcode import Code128
from barcode.writer import ImageWriter
import argparse


def make_barcode_png(data: str):
    """Generate a Code128 barcode as a PIL image."""
    code = Code128(data, writer=ImageWriter())
    buf = io.BytesIO()
    code.write(buf, options={"module_height": 15, "module_width": 0.5, "quiet_zone": 2})
    buf.seek(0)
    return Image.open(buf).convert("RGBA")


def make_sample(product_text: str, barcode_text: str, W=800, H=600):
    """Generate a synthetic 'cart image' with a product label and barcode."""
    bg = Image.new("RGBA", (W, H), (240, 242, 245, 255))
    draw = ImageDraw.Draw(bg)

    # Draw a 'cart box' rectangle
    draw.rounded_rectangle([50, 150, W - 50, H - 80],
                           radius=30, outline=(80, 80, 80, 255), width=4, fill=(255, 255, 255, 255))

    # Product label rectangle
    label_w, label_h = 400, 140
    label_x, label_y = 100, 200
    draw.rounded_rectangle([label_x, label_y, label_x + label_w, label_y + label_h],
                           radius=20, fill=(250, 250, 250, 255), outline=(200, 200, 200, 255))

    # Product text
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
    draw.text((label_x + 20, label_y + 20), product_text, fill=(20, 20, 20, 255), font=font)

    # Generate and paste barcode
    bc = make_barcode_png(barcode_text).resize((320, 80))
    bg.alpha_composite(bc, (label_x + 40, label_y + 60))

    return bg.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description="Generate synthetic product sample images")
    ap.add_argument("--outdir", default="samples/generated", help="Output folder")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    samples = [
        ("Organic Milk 1L", "LOC-ABU-00123"),
        ("Brown Bread 400g", "LOC-ABU-00456"),
        ("Premium Basmati Rice 2kg", "LOC-ABU-00789"),
        ("Butter Cookies", "LOC-ABU-01010"),
    ]

    for i, (product, code) in enumerate(samples, start=1):
        img = make_sample(product, code)
        path = os.path.join(args.outdir, f"sample_cart_{i}.png")
        img.save(path, format="PNG")
        print(f"✅ Saved: {path}")


if __name__ == "__main__":
    main()
