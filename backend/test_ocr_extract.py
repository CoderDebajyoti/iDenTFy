import re
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()

def test_extract(sample_path):
    img = cv2.imread(sample_path)
    if img is None:
        print(f"Cannot read {sample_path}")
        return
    h_img, w_img = img.shape[:2]
    result, elapse = engine(img)
    lines = []
    full_text_list = []
    confidences = []
    
    if result:
        for res in result:
            bbox, text, conf = res[0], res[1], res[2]
            cleaned_text = text.strip()
            if cleaned_text:
                x_pts = [p[0] for p in bbox]
                y_pts = [p[1] for p in bbox]
                x_min, x_max = min(x_pts), max(x_pts)
                y_min, y_max = min(y_pts), max(y_pts)
                norm_box = {
                    "x": round(float(x_min) / w_img * 100, 2),
                    "y": round(float(y_min) / h_img * 100, 2),
                    "w": round(float(x_max - x_min) / w_img * 100, 2),
                    "h": round(float(y_max - y_min) / h_img * 100, 2)
                }
                lines.append({
                    "text": cleaned_text,
                    "confidence": round(float(conf), 3),
                    "bbox": bbox,
                    "norm_box": norm_box
                })
                full_text_list.append(cleaned_text)
                confidences.append(float(conf))
                
    full_text = "\n".join(full_text_list)
    print(f"\n======================\nSAMPLE: {sample_path}\nLINES COUNT: {len(lines)}\n======================")
    
    # Check MRZ lines
    mrz_lines = [l["text"] for l in lines if l["text"].startswith("P<") or l["text"].startswith("I<") or (len(l["text"]) > 25 and "<" in l["text"])]
    print("Detected MRZ candidates:", mrz_lines)

test_extract('../demo_samples/sample_valid_passport.jpg')
test_extract('../demo_samples/Screenshot 2026-09-10 004248.png')
test_extract('../demo_samples/Screenshot 2026-09-10 004414.png')
