import cv2
import json
from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()
for sample in ['../demo_samples/Screenshot 2026-09-10 004248.png', '../demo_samples/Screenshot 2026-09-10 004414.png']:
    img = cv2.imread(sample)
    if img is not None:
        result, elapse = engine(img)
        print(f"=== SAMPLE: {sample} (took {elapse}) ===")
        if result:
            for r in result:
                bbox, text, conf = r[0], r[1], r[2]
                print(f"{text} | conf: {conf:.3f} | box: {bbox}")
        else:
            print("No text detected")
