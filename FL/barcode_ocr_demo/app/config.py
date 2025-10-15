# placeholder file
# app/config.py

from dataclasses import dataclass

# Which OCR engine to prefer ('easyocr' or 'tesseract')
PREFERRED_OCR = "easyocr"

# File types this app supports
SUPPORTED_EXTS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}

@dataclass
class LabelParams:
    # These help detect label-like regions (optional tuning)
    min_area: int = 1500        # Ignore tiny shapes
    max_area: int = 1_000_000   # Ignore huge boxes
    min_aspect: float = 0.3     # Minimum width/height ratio
    max_aspect: float = 5.0     # Maximum width/height ratio
    close_kernel: int = 9       # Morphology kernel for noise cleanup

LABEL_PARAMS = LabelParams()
