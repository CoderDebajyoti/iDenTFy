"""
OCR & Document Field Extraction Service
Supports RapidOCR (PP-OCRv4 ONNX), PaddleOCR, multi-pass analysis, and optical contour extraction.
"""

import re
import time
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from app.services.image_preprocessing import (
    preprocess_document_for_ocr,
    normalize_illumination,
    enhance_contrast_clahe
)
from app.services.mrz_service import parse_and_validate_mrz

# Primary OCR Engine: RapidOCR (PP-OCRv4 ONNX), fallback PaddleOCR / Optical
_ocr_engine = None
_ocr_engine_name = "Optical-Detector"

try:
    from rapidocr_onnxruntime import RapidOCR
    _ocr_engine = RapidOCR()
    _ocr_engine_name = "RapidOCR-ONNX"
except Exception:
    try:
        from paddleocr import PaddleOCR
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        _ocr_engine_name = "PaddleOCR"
    except Exception:
        _ocr_engine = None
        _ocr_engine_name = "Optical-Detector"

def _run_single_engine_ocr(image_bgr: np.ndarray) -> Tuple[List[Dict[str, Any]], List[float]]:
    """Internal helper to execute one OCR pass on an image array."""
    lines = []
    confidences = []
    if _ocr_engine is None or image_bgr is None:
        return lines, confidences

    h_img, w_img = image_bgr.shape[:2]
    try:
        if _ocr_engine_name == "RapidOCR-ONNX":
            results, _ = _ocr_engine(image_bgr)
            if results:
                for res in results:
                    bbox, text, conf = res[0], res[1], res[2]
                    cleaned_text = text.strip()
                    if cleaned_text:
                        x_pts = [p[0] for p in bbox]
                        y_pts = [p[1] for p in bbox]
                        x_min, x_max = max(0, min(x_pts)), min(w_img, max(x_pts))
                        y_min, y_max = max(0, min(y_pts)), min(h_img, max(y_pts))
                        norm_box = {
                            "x": round(float(x_min) / w_img * 100, 2),
                            "y": round(float(y_min) / h_img * 100, 2),
                            "w": round(float(x_max - x_min) / w_img * 100, 2),
                            "h": round(float(y_max - y_min) / h_img * 100, 2)
                        }
                        lines.append({
                            "text": cleaned_text,
                            "confidence": round(float(conf), 3),
                            "bbox": [[float(p[0]), float(p[1])] for p in bbox],
                            "norm_box": norm_box
                        })
                        confidences.append(float(conf))
        elif _ocr_engine_name == "PaddleOCR":
            results = _ocr_engine.ocr(image_bgr, cls=True)
            if results and len(results) > 0 and results[0] is not None:
                for res in results[0]:
                    bbox, (text, conf) = res
                    cleaned_text = text.strip()
                    if cleaned_text:
                        x_pts = [p[0] for p in bbox]
                        y_pts = [p[1] for p in bbox]
                        x_min, x_max = max(0, min(x_pts)), min(w_img, max(x_pts))
                        y_min, y_max = max(0, min(y_pts)), min(h_img, max(y_pts))
                        norm_box = {
                            "x": round(float(x_min) / w_img * 100, 2),
                            "y": round(float(y_min) / h_img * 100, 2),
                            "w": round(float(x_max - x_min) / w_img * 100, 2),
                            "h": round(float(y_max - y_min) / h_img * 100, 2)
                        }
                        lines.append({
                            "text": cleaned_text,
                            "confidence": round(float(conf), 3),
                            "bbox": [[float(p[0]), float(p[1])] for p in bbox],
                            "norm_box": norm_box
                        })
                        confidences.append(float(conf))
    except Exception:
        pass

    return lines, confidences

def run_ocr_on_image(image_bgr: np.ndarray, document_type: str = "passport") -> Dict[str, Any]:
    """
    Multi-pass optical character recognition and field extraction:
    Pass 1: Primary preprocessed & perspective-corrected document
    Pass 2: Targeted MRZ region crop (for passports & ID cards)
    Pass 3: Illumination-normalized pass if needed for low-contrast/glare documents
    """
    t0 = time.time()

    # Pass 1: Primary Image OCR
    lines, confidences = _run_single_engine_ocr(image_bgr)
    h_img, w_img = image_bgr.shape[:2]

    # Check if primary pass already found valid MRZ candidates
    has_primary_mrz = any((l["text"].startswith("P<") or l["text"].startswith("I<") or (len(l["text"]) >= 35 and "<" in l["text"])) for l in lines)

    # Pass 2: Targeted MRZ Crop only if primary pass missed MRZ
    if not has_primary_mrz and document_type in ["passport", "identity_card"]:
        mrz_top_y = int(h_img * 0.70)
        mrz_crop = image_bgr[mrz_top_y:h_img, 0:w_img]
        if mrz_crop.shape[0] > 20 and mrz_crop.shape[1] > 50:
            if mrz_crop.shape[0] < 150:
                scale_factor = 150.0 / mrz_crop.shape[0]
                mrz_crop_scaled = cv2.resize(mrz_crop, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
            else:
                mrz_crop_scaled = mrz_crop

            crop_lines, crop_confs = _run_single_engine_ocr(mrz_crop_scaled)
            existing_texts = [l["text"] for l in lines]
            for cl in crop_lines:
                if ("<" in cl["text"] or cl["text"].startswith("P<") or cl["text"].startswith("I<")) and cl["text"] not in existing_texts:
                    lines.append(cl)
                    confidences.append(cl["confidence"])

    # Pass 3: Illumination normalization if first pass had low detection or low confidence
    avg_conf_p1 = float(np.mean(confidences)) if confidences else 0.0
    if len(lines) < 4 or avg_conf_p1 < 0.65:
        norm_variant = normalize_illumination(image_bgr)
        p3_lines, p3_confs = _run_single_engine_ocr(norm_variant)
        for pl in p3_lines:
            if not any(pl["text"] in el for el in existing_texts):
                lines.append(pl)
                confidences.append(pl["confidence"])

    # Optical contour fallback if zero lines detected by model
    if not lines:
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                x, y, w, h = cv2.boundingRect(c)
                if 12 < h < 140 and 35 < w < w_img * 0.95:
                    lines.append({
                        "text": "[Text Segment]",
                        "confidence": 0.60,
                        "bbox": [[float(x), float(y)], [float(x + w), float(y)], [float(x + w), float(y + h)], [float(x), float(y + h)]],
                        "norm_box": {
                            "x": round(x / w_img * 100, 2),
                            "y": round(y / h_img * 100, 2),
                            "w": round(w / w_img * 100, 2),
                            "h": round(h / h_img * 100, 2)
                        }
                    })
        except Exception:
            pass

    full_text_list = [l["text"] for l in lines]
    full_text = "\n".join(full_text_list)
    avg_conf = round(float(np.mean(confidences)), 3) if confidences else 0.0

    # 4. Extract Structured Fields and Field-Level Confidences
    fields, field_confidences = extract_fields_and_confidences(full_text, document_type, lines)

    # 5. Evidence-based OCR Quality Assessment
    ocr_quality, quality_reason = evaluate_ocr_quality(fields, field_confidences, avg_conf, lines)

    total_time_ms = round((time.time() - t0) * 1000, 2)
    status_str = "success" if ocr_quality in ["GOOD", "FAIR"] else "failed"

    return {
        "status": status_str,
        "engine": _ocr_engine_name,
        "text": full_text,
        "full_text": full_text,
        "text_lines": lines,
        "confidence": avg_conf,
        "average_confidence": avg_conf,
        "field_confidence": field_confidences,
        "quality_score": ocr_quality,
        "quality_reason": quality_reason,
        "processing_time_ms": total_time_ms,
        "fields": fields
    }

def extract_fields_and_confidences(full_text: str, document_type: str, lines: List[Dict[str, Any]]) -> Tuple[Dict[str, Optional[str]], Dict[str, Optional[float]]]:
    """
    Extract document-specific fields with field-level OCR confidence calculation.
    """
    fields = {
        "full_name": None,
        "given_names": None,
        "surname": None,
        "document_number": None,
        "date_of_birth": None,
        "nationality": None,
        "gender": None,
        "sex": None,
        "issue_date": None,
        "expiry_date": None,
        "place_of_birth": None,
        "place_of_issue": None,
        "issuing_authority": None,
        "mrz_raw": None
    }

    field_conf = {
        "full_name": None,
        "document_number": None,
        "date_of_birth": None,
        "nationality": None,
        "gender": None,
        "issue_date": None,
        "expiry_date": None,
        "mrz": None
    }

    if not lines and not full_text:
        return fields, field_conf

    line_texts = [l.get("text", "").strip() for l in lines if l.get("text")]
    line_confs = {l.get("text", "").strip(): l.get("confidence", 0.8) for l in lines if l.get("text")}

    # 1. Search for MRZ lines (P<, I<, or long lines containing < delimiters)
    mrz_candidates = [
        t for t in line_texts
        if (len(t) >= 28 and sum(1 for c in t if c.isalnum() or c == '<') >= len(t) * 0.75 and '<' in t) or t.startswith('P<') or t.startswith('I<')
    ]
    # Prioritize standard 44-char (TD3) and 30-char (TD1) lines
    mrz_candidates.sort(key=lambda t: (len(t) == 44 or len(t) == 30, len(t)), reverse=True)

    if len(mrz_candidates) >= 2:
        p_lines = [l for l in mrz_candidates if l.startswith("P<") or l.startswith("I<")]
        other_lines = [l for l in mrz_candidates if not (l.startswith("P<") or l.startswith("I<"))]
        if p_lines and other_lines:
            ordered_mrz = [p_lines[0], other_lines[0]]
        else:
            ordered_mrz = mrz_candidates[:2]
        fields["mrz_raw"] = "\n".join(ordered_mrz)
        mrz_c1 = line_confs.get(ordered_mrz[0], 0.9)
        mrz_c2 = line_confs.get(ordered_mrz[1], 0.9)
        field_conf["mrz"] = round(float((mrz_c1 + mrz_c2) / 2.0), 3)
    elif len(mrz_candidates) == 1:
        fields["mrz_raw"] = mrz_candidates[0]
        field_conf["mrz"] = round(float(line_confs.get(mrz_candidates[0], 0.85)), 3)

    # 2. Extract Document Number
    for txt in line_texts:
        if '<' in txt:
            continue
        # Check standard passport number format: 1-2 letters + 7 digits (e.g. K9096335, X6338455, PA9821453)
        doc_match = re.search(r"\b([A-Z][0-9]{7}|[A-Z]{2}[0-9]{7}|[A-Z]{1,3}\d{6,9})\b", txt)
        if doc_match:
            fields["document_number"] = doc_match.group(1).upper()
            field_conf["document_number"] = round(float(line_confs.get(txt, 0.9)), 3)
            break

    # 3. Extract Dates (DOB, Issue Date, Expiry Date)
    date_regex = re.compile(
        r"\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2}|\d{2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[a-z]*\s+\d{4})\b",
        re.IGNORECASE
    )

    extracted_dates = []
    for idx, txt in enumerate(line_texts):
        if '<' in txt and len(txt) > 20:
            continue
        matches = date_regex.findall(txt)
        for m in matches:
            prev_txt = line_texts[idx - 1] if idx > 0 else ""
            next_txt = line_texts[idx + 1] if idx + 1 < len(line_texts) else ""
            context = f"{prev_txt} {txt} {next_txt}".lower()
            conf = line_confs.get(txt, 0.9)
            if any(w in context for w in ["birth", "dob", "bith", "bh", "date of birth", "d.o.b"]):
                fields["date_of_birth"] = m
                field_conf["date_of_birth"] = round(float(conf), 3)
            elif any(w in context for w in ["expiry", "expir", "valid until", "expiration"]):
                fields["expiry_date"] = m
                field_conf["expiry_date"] = round(float(conf), 3)
            elif any(w in context for w in ["issue", "issued", "date of issue", "sue"]):
                fields["issue_date"] = m
                field_conf["issue_date"] = round(float(conf), 3)
            extracted_dates.append((m, conf))

    # Sequence fallback for dates if contextual labels were fragmented
    if not fields["date_of_birth"] and len(extracted_dates) >= 1:
        fields["date_of_birth"] = extracted_dates[0][0]
        field_conf["date_of_birth"] = round(float(extracted_dates[0][1]), 3)
    if not fields["expiry_date"] and len(extracted_dates) >= 2:
        fields["expiry_date"] = extracted_dates[-1][0] if extracted_dates[-1][0] != fields["date_of_birth"] else (extracted_dates[1][0] if len(extracted_dates) > 1 else None)
        field_conf["expiry_date"] = round(float(extracted_dates[-1][1]), 3)
    if not fields["issue_date"] and len(extracted_dates) >= 3:
        fields["issue_date"] = extracted_dates[1][0]
        field_conf["issue_date"] = round(float(extracted_dates[1][1]), 3)

    # 4. Nationality / Issuing Country
    nat_match = re.search(r"\b(FRA|USA|GBR|CAN|DEU|SGP|MYS|ARE|SRB|IND|AUS|JPN|ESP|ITA|NLD|SWE|CHE|CHN|BRA|MEX|ZAF|INDIAN|FRENCH|AMERICAN|BRITISH)\b", full_text, re.IGNORECASE)
    if nat_match:
        val = nat_match.group(1).upper()
        norm_map = {"INDIAN": "IND", "FRENCH": "FRA", "AMERICAN": "USA", "BRITISH": "GBR"}
        fields["nationality"] = norm_map.get(val, val)
        field_conf["nationality"] = 0.95

    # 5. Full Name (Given Names / Surname)
    for idx, txt in enumerate(line_texts):
        if '<' in txt or len(txt) < 3:
            continue
        # Direct person name matching (2-3 words capitalized/uppercase)
        if re.match(r"^[A-Za-z]{2,20}\s+[A-Za-z]{2,20}(?:\s+[A-Za-z]{2,20})?$", txt):
            if not any(k in txt.upper() for k in ["REPUBLIC", "PASSPORT", "INDIA", "FRANCE", "UNION", "THESE ARE", "BY ORDER", "OF INDIA", "TYPE", "CODE"]):
                fields["full_name"] = txt.title()
                field_conf["full_name"] = round(float(line_confs.get(txt, 0.95)), 3)
                break

    # 6. Sex / Gender
    gender_match = re.search(r"\b(?:SEX|GENDER)[:\s/]*([MFX])\b|\b([MFX])\b", full_text, re.IGNORECASE)
    if gender_match:
        val = (gender_match.group(1) or gender_match.group(2)).upper()
        fields["gender"] = val
        fields["sex"] = val
        field_conf["gender"] = 0.95

    # 7. Place of Birth / Place of Issue
    for idx, txt in enumerate(line_texts):
        if "<" in txt:
            continue
        if any(k in txt.lower() for k in ["place of birth", "pob", "bith"]):
            if idx + 1 < len(line_texts):
                cand = line_texts[idx + 1].strip()
                if not any(k in cand.upper() for k in ["REPUBLIC", "PASSPORT", "INDIA", "TYPE"]):
                    fields["place_of_birth"] = cand
        elif any(k in txt.lower() for k in ["place of issue", "poi"]):
            if idx + 1 < len(line_texts):
                cand = line_texts[idx + 1].strip()
                if not any(k in cand.upper() for k in ["REPUBLIC", "PASSPORT", "INDIA", "TYPE"]):
                    fields["place_of_issue"] = cand

    return fields, field_conf

def extract_fields_by_type(full_text: str, document_type: str, lines: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
    """Backward-compatible extraction alias for test suites."""
    fields, _ = extract_fields_and_confidences(full_text, document_type, lines)
    return fields

def evaluate_ocr_quality(fields: Dict[str, Any], field_conf: Dict[str, Any], avg_conf: float, lines: List[Any]) -> Tuple[str, str]:
    """
    Evidence-based OCR quality assessment:
    - GOOD: Document number, Name, and DOB/Expiry extracted with confidence >= 0.75
    - FAIR: Partial required fields extracted or moderate confidence (0.50 - 0.74)
    - POOR: Insufficient fields extracted or confidence < 0.50
    """
    if not lines or len(lines) == 0:
        return "POOR", "No optical text lines detected on document."

    has_doc_num = bool(fields.get("document_number"))
    has_name = bool(fields.get("full_name"))
    has_dates = bool(fields.get("date_of_birth") or fields.get("expiry_date"))
    has_mrz = bool(fields.get("mrz_raw"))

    extracted_count = sum([has_doc_num, has_name, has_dates, has_mrz])

    if extracted_count >= 3 and avg_conf >= 0.75:
        return "GOOD", f"All critical identity fields and MRZ extracted with high confidence ({round(avg_conf * 100)}%)."
    elif extracted_count >= 2 and avg_conf >= 0.50:
        return "FAIR", f"Identity fields partially extracted with moderate optical confidence ({round(avg_conf * 100)}%)."
    else:
        return "POOR", "Low optical confidence or missing critical credential fields."
