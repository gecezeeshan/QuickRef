import os
import cv2
import pandas as pd
from .utils import load_image, ensure_dir, dump_json
from .barcode_reader import read_barcodes
from .ocr import ocr_text
from .config import SUPPORTED_EXTS

def expand_bbox(bbox, img_shape, pad=40):
    """Expand a barcode bounding box slightly for OCR."""
    x, y, w, h = bbox
    H, W = img_shape[:2]
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(W, x + w + pad)
    y2 = min(H, y + h + pad)
    return x1, y1, x2 - x1, y2 - y1


def process_image(path: str, out_dir: str):
    img = load_image(path)
    if img is None:
        return {"path": path, "error": "failed_to_load"}

    # Step 1: Convert to grayscale for better detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 2: Read barcodes from grayscale image
    barcodes = read_barcodes(img)

    texts = []
    crops = []

    # Step 3: For each barcode, crop region and OCR
    for b in barcodes:
        bbox = b.get("bbox")
        if bbox:
            x, y, w, h = expand_bbox(bbox, img.shape)
            crop = img[y:y + h, x:x + w]
            if crop.size > 0:
                text = ocr_text(crop)
                if text:
                    texts.append(text)
                crops.append({"bbox": bbox, "text": text})

    # Step 4: Fallback if no barcode or no readable text
    if not texts:
        text_full = ocr_text(img)
        if text_full:
            texts.append(text_full)

    combined_text = " | ".join([t for t in texts if t])

    result = {
        "path": path,
        "product_name": combined_text,
        "barcodes": barcodes,
        "crops": crops
    }

    # Step 5: Save detailed JSON result
    json_dir = os.path.join(out_dir, "json")
    ensure_dir(json_dir)
    base = os.path.splitext(os.path.basename(path))[0]
    dump_json(result, os.path.join(json_dir, f"{base}.json"))
    return result


def process_many(inputs, out_dir):
    ensure_dir(out_dir)
    rows = []
    for p in inputs:
        res = process_image(p, out_dir)
        if "error" in res:
            rows.append({"path": p, "error": res["error"]})
        else:
            row = {
                "path": p,
                "product_name": res["product_name"],
                "barcodes": ";".join([b['data'] for b in res['barcodes']]) if res["barcodes"] else ""
            }
            rows.append(row)
            print(f"[+] Processed: {p}")
    df = pd.DataFrame(rows)
    csv_path = os.path.join(out_dir, "results.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    return csv_path
