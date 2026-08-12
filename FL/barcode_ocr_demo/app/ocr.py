# placeholder file
import cv2

def ocr_text(bgr):
    try:
        import easyocr
        reader = easyocr.Reader(['en','ar'], gpu=False)
        results = reader.readtext(bgr, detail=0, paragraph=True)
        return " ".join(results).strip()
    except Exception:
        import pytesseract
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text = pytesseract.image_to_string(gray, lang='eng', config='--psm 6')
        return text.strip()
