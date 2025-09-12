from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Tuple
import cv2
import numpy as np
import pytesseract
from pytesseract import Output

def _auto_canny(img: np.ndarray, sigma: float = 0.33) -> np.ndarray:
    v = np.median(img)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    return cv2.Canny(img, lower, upper)

def _deskew(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape)==3 else image
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1] if coords.size else 0
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def preprocess(path: Path) -> np.ndarray:
    img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        # fallback read
        img = cv2.imread(str(path))
    # resize if too small
    h, w = img.shape[:2]
    scale = 1.0
    if max(h, w) < 1200:
        scale = 1200 / max(h, w)
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_CUBIC)
    # deskew
    img = _deskew(img)
    # grayscale + adaptive threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 35, 11)
    return thr

def run_ocr(image_path: Path) -> Dict[str, Any]:
    thr = preprocess(image_path)
    config = "--oem 3 --psm 6 -l spa+eng"
    data = pytesseract.image_to_data(thr, output_type=Output.DICT, config=config)
    tokens: List[str] = []
    bboxes: List[Tuple[int,int,int,int]] = []
    confs: List[float] = []
    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        if not text:
            continue
        tokens.append(text)
        (x, y, w, h) = (data["left"][i], data["top"][i], data["width"][i], data["height"][i])
        bboxes.append((x, y, w, h))
        confs.append(float(data["conf"][i]) if data["conf"][i] != "-1" else 0.0)
    return {"tokens": tokens, "bboxes": bboxes, "confs": confs, "image_w": thr.shape[1], "image_h": thr.shape[0]}