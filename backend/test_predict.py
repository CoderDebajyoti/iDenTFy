import os
# Disable oneDNN/MKLDNN to prevent PIR executor crash on Windows CPU
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

import cv2
from app.services.ocr_service import OCRService

image = cv2.imread("test_documents/clear.jpg")
engine = OCRService.get_engine()
result = engine.predict(image)

print("RESULT TYPE:", type(result))
for idx, res in enumerate(result):
    print(f"--- Result {idx} ---")
    print("Type:", type(res))
    print("Keys/Attributes:", dir(res))
    # Standard PaddleX result usually has dict representation or attributes
    if hasattr(res, "str"):
        print("Str representation:", str(res))
    if hasattr(res, "json"):
        print("JSON representation:", res.json)
