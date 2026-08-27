"""
OCR Service.

Handles Optical Character Recognition (OCR) using PaddleOCR.
"""

import os
# Disable oneDNN/MKLDNN to prevent PIR executor crash on Windows CPU
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

import logging
import numpy as np
from paddleocr import PaddleOCR

logger = logging.getLogger("ocr_service")

class OCRService:
    _ocr_engine = None

    @classmethod
    def get_engine(cls) -> PaddleOCR:
        """
        Initializes and returns the PaddleOCR instance (singleton).
        """
        if cls._ocr_engine is None:
            logger.info("Initializing PaddleOCR engine (use_textline_orientation=True, lang='en')...")
            # use_textline_orientation=True detects oriented/rotated text
            cls._ocr_engine = PaddleOCR(use_textline_orientation=True, lang="en")
            logger.info("PaddleOCR engine initialized successfully.")
        return cls._ocr_engine

    @classmethod
    def run_ocr(cls, image: np.ndarray) -> dict:
        """
        Runs OCR on the given BGR image numpy array.
        
        Args:
            image (np.ndarray): Input BGR image numpy array.
            
        Returns:
            dict: Structured OCR results matching the OCRData schema.
        """
        # Ensure PaddleOCR engine is initialized
        engine = cls.get_engine()
        
        logger.info("Starting PaddleOCR prediction...")
        # Execute OCR prediction
        result = engine.predict(image)
        logger.info("PaddleOCR prediction complete.")
        
        text_items = []
        full_text_list = []
        total_confidence = 0.0
        count = 0
        
        if result and len(result) > 0:
            ocr_res = result[0]
            rec_texts = ocr_res.get("rec_texts", [])
            rec_scores = ocr_res.get("rec_scores", [])
            dt_polys = ocr_res.get("dt_polys", [])
            
            for text, score, poly in zip(rec_texts, rec_scores, dt_polys):
                # Normalize bounding box points to integer lists
                bounding_box = [[int(round(pt[0])), int(round(pt[1]))] for pt in poly]
                confidence_score = round(float(score), 4)
                
                text_items.append({
                    "text": text,
                    "confidence": confidence_score,
                    "bounding_box": bounding_box
                })
                
                full_text_list.append(text)
                total_confidence += confidence_score
                count += 1
                
        average_confidence = round(total_confidence / count, 4) if count > 0 else 0.0
        full_text = " ".join(full_text_list)
        
        return {
            "text": text_items,
            "full_text": full_text,
            "average_confidence": average_confidence
        }
