# app/label_detector.py

import cv2
import numpy as np
from typing import List, Tuple
from .config import LABEL_PARAMS

def propose_label_rois(bgr):
    """
    Propose rectangular label-like regions based on edges and morphology.
    Returns a list of (x, y, w, h) bounding boxes.
    """
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)  # smooth but keep edges
    grad = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=3)
    grad = cv2.convertScaleAbs(grad)

    _, th = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (LABEL_PARAMS.close_kernel, LABEL_PARAMS.close_kernel))
    closed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rois: List[Tuple[int, int, int, int]] = []

    h, w = gray.shape[:2]
    for c in contours:
        x, y, wc, hc = cv2.boundingRect(c)
        area = wc * hc
        if area < LABEL_PARAMS.min_area or area > LABEL_PARAMS.max_area:
            continue
        aspect = wc / max(hc, 1)
        if aspect < LABEL_PARAMS.min_aspect or aspect > LABEL_PARAMS.max_aspect:
            continue
        # small padding around ROI
        pad = 5
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(w, x + wc + pad)
        y1 = min(h, y + hc + pad)
        rois.append((x0, y0, x1 - x0, y1 - y0))

    # sort by area (largest first)
    rois = sorted(rois, key=lambda r: -(r[2] * r[3]))
    return rois[:5]  # return top 5 regions
