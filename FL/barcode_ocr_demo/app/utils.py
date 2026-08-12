# placeholder file
import os
import json
import cv2
import numpy as np
from PIL import Image

def load_image(path: str):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        pil = Image.open(path).convert('RGB')
        img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    return img

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def dump_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
