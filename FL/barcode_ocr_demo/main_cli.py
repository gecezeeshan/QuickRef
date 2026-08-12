import argparse, os, sys, glob
import cv2
import pandas as pd
from pyzbar.pyzbar import decode
import easyocr

def read_barcodes(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray)
    results = []
    for b in barcodes:
        (x, y, w, h) = b.rect
        barcode_data = b.data.decode("utf-8")
        barcode_type = b.type
        results.append({"data": barcode_data, "type": barcode_type, "bbox": [x, y, w, h]})
    return results

def ocr_text(image):
    reader = easyocr.Reader(['en', 'ar'], gpu=False)
    results = reader.readtext(image, detail=0, paragraph=True)
    return " ".join(results).strip()

def process_image(path):
    image = cv2.imread(path)
    if image is None:
        return {"path": path, "error": "cannot read image"}

    barcodes = read_barcodes(image)
    text = ocr_text(image)
    return {"path": path, "barcodes": barcodes, "text": text}

def main():
    parser = argparse.ArgumentParser(description="OCR + Barcode Reader CLI")
    parser.add_argument("--input", required=True, help="Input image or folder")
    parser.add_argument("--out", default="output", help="Output folder")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    inputs = []
    if os.path.isdir(args.input):
        for ext in (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"):
            inputs += glob.glob(os.path.join(args.input, f"**/*{ext}"), recursive=True)
    else:
        inputs = [args.input]

    results = []
    for path in inputs:
        res = process_image(path)
        results.append(res)
        print(f"[+] Processed: {path}")

    df = pd.DataFrame(results)
    df.to_csv(os.path.join(args.out, "results.csv"), index=False)
    print("\n✅ All done! Results saved in:", os.path.join(args.out, "results.csv"))

if __name__ == "__main__":
    main()
