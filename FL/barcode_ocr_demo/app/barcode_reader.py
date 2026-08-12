# placeholder file
import cv2
from pyzbar.pyzbar import decode

def read_barcodes(bgr_image):
    gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    results = []
    barcodes = decode(gray)
    for b in barcodes:
        (x, y, w, h) = b.rect
        data = b.data.decode("utf-8", errors="ignore")
        results.append({
            "type": b.type,
            "data": data,
            "bbox": [x, y, w, h]
        })
    return results
