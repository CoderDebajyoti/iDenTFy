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
    enhance_contrast_clahe,
    detect_mrz_region,
    generate_mrz_preprocessed_variants
)
from app.services.mrz_service import parse_and_validate_mrz, normalize_mrz_line

# Initialize primary OCR Engine
_ocr_engine = None
_ocr_engine_name = "rapidocr"

try:
    from rapidocr_onnxruntime import RapidOCR
    _ocr_engine = RapidOCR()
    _ocr_engine_name = "rapidocr"
except Exception:
    try:
        from paddleocr import PaddleOCR
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        _ocr_engine_name = "paddleocr"
    except Exception:
        _ocr_engine = None
        _ocr_engine_name = "none"

def _run_single_engine_ocr(img_bgr: np.ndarray) -> Tuple[List[Dict[str, Any]], List[float]]:
    """
    Execute OCR using the initialized engine and return bounding boxes + confidences.
    """
    if img_bgr is None or img_bgr.size == 0 or _ocr_engine is None:
        return [], []

    lines: List[Dict[str, Any]] = []
    confidences: List[float] = []
    h_img, w_img = img_bgr.shape[:2]

    try:
        if _ocr_engine_name == "rapidocr":
            result, _ = _ocr_engine(img_bgr)
            if result:
                for item in result:
                    bbox, text, score = item[0], str(item[1]).strip(), float(item[2])
                    if not text:
                        continue
                    x_pts = [p[0] for p in bbox]
                    y_pts = [p[1] for p in bbox]
                    x_min, y_min = min(x_pts), min(y_pts)
                    bw, bh = max(x_pts) - x_min, max(y_pts) - y_min
                    norm_box = {
                        "x": round(float(x_min) / w_img * 100, 2),
                        "y": round(float(y_min) / h_img * 100, 2),
                        "w": round(float(bw) / w_img * 100, 2),
                        "h": round(float(bh) / h_img * 100, 2)
                    }
                    lines.append({
                        "text": text,
                        "confidence": round(score, 3),
                        "bbox": bbox,
                        "norm_box": norm_box
                    })
                    confidences.append(score)
        elif _ocr_engine_name == "paddleocr":
            result = _ocr_engine.ocr(img_bgr, cls=True)
            if result and result[0]:
                for line in result[0]:
                    bbox = line[0]
                    text = str(line[1][0]).strip()
                    score = float(line[1][1])
                    if not text:
                        continue
                    x_pts = [p[0] for p in bbox]
                    y_pts = [p[1] for p in bbox]
                    x_min, y_min = min(x_pts), min(y_pts)
                    bw, bh = max(x_pts) - x_min, max(y_pts) - y_min
                    norm_box = {
                        "x": round(float(x_min) / w_img * 100, 2),
                        "y": round(float(y_min) / h_img * 100, 2),
                        "w": round(float(bw) / w_img * 100, 2),
                        "h": round(float(bh) / h_img * 100, 2)
                    }
                    lines.append({
                        "text": text,
                        "confidence": round(score, 3),
                        "bbox": bbox,
                        "norm_box": norm_box
                    })
                    confidences.append(score)
    except Exception as e:
        print(f"Error during OCR execution: {e}")

    return lines, confidences

def _segment_and_order_mrz_lines(crop_lines: List[Dict[str, Any]], crop_h: int) -> List[str]:
    """
    Cluster detected OCR segments by vertical centroid to strictly isolate Line 1 and Line 2.
    Sorts boxes horizontally within each line to guarantee no character transposition.
    Filters out nearby non-MRZ visual text.
    """
    if not crop_lines:
        return []

    # First, expand any lines that contain newlines or concatenated MRZ lines
    expanded_lines = []
    for cl in crop_lines:
        txt = cl["text"].strip()
        if not txt:
            continue
        bbox = cl.get("bbox", [])
        if bbox and len(bbox) >= 4:
            y_pts = [p[1] for p in bbox]
            x_pts = [p[0] for p in bbox]
            y_mid = sum(y_pts) / len(y_pts)
            x_min = min(x_pts)
            h_box = max(y_pts) - min(y_pts)
        else:
            y_mid = crop_h / 2.0
            x_min = 0.0
            h_box = 15.0

        if "\n" in txt:
            for s_idx, sl in enumerate(txt.split("\n")):
                if sl.strip():
                    expanded_lines.append((y_mid + s_idx * h_box, x_min, sl.strip(), cl, h_box))
        elif len(txt) >= 60 and "<" in txt:
            # Check for embedded P< or I< line marker
            p_idx = txt.find("P<")
            if p_idx == -1:
                p_idx = txt.find("I<")
            if p_idx > 0:
                l_pre = txt[:p_idx]
                l_post = txt[p_idx:]
                expanded_lines.append((y_mid, x_min, l_post, cl, h_box))
                expanded_lines.append((y_mid + h_box, x_min, l_pre, cl, h_box))
            elif len(txt) >= 80:
                expanded_lines.append((y_mid, x_min, txt[:44], cl, h_box))
                expanded_lines.append((y_mid + h_box, x_min, txt[44:], cl, h_box))
            else:
                expanded_lines.append((y_mid, x_min, txt, cl, h_box))
        else:
            expanded_lines.append((y_mid, x_min, txt, cl, h_box))

    if not expanded_lines:
        return []

    # Sort boxes vertically
    expanded_lines.sort(key=lambda b: b[0])

    # Cluster into lines based on Y-proximity:
    # A box belongs to the same horizontal line only if vertical centroid difference is small
    line_clusters: List[List[Tuple[float, float, str, Dict[str, Any], float]]] = []

    for item in expanded_lines:
        y_mid = item[0]
        h_box = item[4]
        assigned = False
        threshold = max(6.0, min(14.0, h_box * 0.55))
        for cluster in line_clusters:
            cluster_avg_y = sum(b[0] for b in cluster) / len(cluster)
            if abs(y_mid - cluster_avg_y) <= threshold:
                cluster.append(item)
                assigned = True
                break
        if not assigned:
            line_clusters.append([item])

    # Sort clusters top-to-bottom
    line_clusters.sort(key=lambda cl: sum(b[0] for b in cl) / len(cl))

    # Within each cluster, sort left-to-right and merge
    ordered_lines = []
    for cluster in line_clusters:
        cluster.sort(key=lambda b: b[1])
        merged_line = "".join(b[2] for b in cluster)
        if len(merged_line) >= 12 or "<" in merged_line:
            ordered_lines.append(merged_line)

    # Unpack any horizontally concatenated lines
    unpacked_lines = []
    for l in ordered_lines:
        if len(l) >= 55 and "<" in l:
            p_idx = l.find("P<")
            if p_idx == -1:
                p_idx = l.find("I<")
            if p_idx > 0:
                unpacked_lines.append(l[p_idx:])
                unpacked_lines.append(l[:p_idx])
            else:
                unpacked_lines.append(l)
        else:
            unpacked_lines.append(l)

    # Strictly filter for MRZ candidate lines (must contain '<' or look like ICAO header/data)
    mrz_candidates = [
        l for l in unpacked_lines
        if "<" in l or l.startswith("P<") or l.startswith("I<")
    ]

    # If multiple candidate lines, find best pairing for Line 1 and Line 2
    if len(mrz_candidates) >= 2:
        p_lines = [l for l in mrz_candidates if l.startswith("P<") or l.startswith("P") or l.startswith("I<") or l.startswith("A<")]
        other_lines = [l for l in mrz_candidates if not (l.startswith("P<") or l.startswith("P") or l.startswith("I<") or l.startswith("A<"))]
        if p_lines and other_lines:
            return [p_lines[0], other_lines[-1]]
        elif len(p_lines) >= 2:
            return p_lines[:2]
        else:
            return mrz_candidates[:2]

    return unpacked_lines

def _extract_mrz_with_consensus(
    image_bgr: np.ndarray,
    document_type: str = "passport",
    full_document_lines: Optional[List[Dict[str, Any]]] = None
) -> Tuple[Optional[str], Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Dedicated Multi-Pass MRZ Extraction Pipeline:
    1. Dedicated MRZ region detection with safety padding.
    2. Adaptive multi-pass OCR on standardized preprocessing variants.
    3. Spatial line clustering & character-level positional consensus.
    4. Comprehensive ICAO 9303 checksum validation.
    Returns: (mrz_raw, mrz_result_dict, mrz_ocr_lines, debug_meta)
    """
    h_img, w_img = image_bgr.shape[:2]
    mrz_crop, crop_meta = detect_mrz_region(image_bgr)
    variants = generate_mrz_preprocessed_variants(mrz_crop)

    # Also add bottom 35% full-width slice of original image as an additional fallback variant
    bottom_35_slice = image_bgr[max(0, int(h_img * 0.65)):h_img, 0:w_img]
    variants.append(("bottom_35_slice", bottom_35_slice))

    debug_meta = {
        "crop_method": crop_meta.get("method"),
        "crop_bbox": crop_meta.get("bbox"),
        "passes_executed": 0,
        "variant_results": []
    }

    pass_results = []
    best_candidate = None
    best_score = -1

    for pass_idx, (var_name, var_img) in enumerate(variants):
        debug_meta["passes_executed"] += 1
        crop_h, crop_w = var_img.shape[:2]
        crop_lines, crop_confs = _run_single_engine_ocr(var_img)
        segmented_lines = _segment_and_order_mrz_lines(crop_lines, crop_h)

        if len(segmented_lines) >= 2:
            raw_text = "\n".join(segmented_lines[:2])
            mrz_eval = parse_and_validate_mrz(raw_text)

            # Score candidate: Valid check digit count + status bonus
            check_results = mrz_eval.get("checksum_results", {})
            valid_count = sum(1 for v in check_results.values() if isinstance(v, dict) and v.get("valid"))
            status_bonus = 10 if mrz_eval.get("mrz_status") == "MRZ_VALID" else (5 if mrz_eval.get("mrz_status") == "MRZ_OCR_CORRECTED_CANDIDATE" else 0)
            score = valid_count * 2 + status_bonus

            pass_record = {
                "pass": pass_idx + 1,
                "variant": var_name,
                "lines": segmented_lines[:2],
                "mrz_status": mrz_eval.get("mrz_status"),
                "valid": mrz_eval.get("mrz_valid"),
                "score": score,
                "eval": mrz_eval
            }
            pass_results.append(pass_record)
            debug_meta["variant_results"].append({
                "pass": pass_idx + 1,
                "variant": var_name,
                "status": mrz_eval.get("mrz_status"),
                "lines": segmented_lines[:2]
            })

            if score > best_score:
                best_score = score
                best_candidate = (raw_text, mrz_eval, crop_lines)

            # Fast return on perfect first pass
            if pass_idx == 0 and mrz_eval.get("mrz_status") == "MRZ_VALID":
                break

    # If crop variants did not find a valid MRZ and full_document_lines are available, test full lines
    if (not best_candidate or not best_candidate[1].get("mrz_valid")) and full_document_lines:
        full_seg = _segment_and_order_mrz_lines(full_document_lines, h_img)
        if len(full_seg) >= 2:
            raw_full = "\n".join(full_seg[:2])
            eval_full = parse_and_validate_mrz(raw_full)
            if eval_full.get("detected"):
                check_res = eval_full.get("checksum_results", {})
                v_count = sum(1 for v in check_res.values() if isinstance(v, dict) and v.get("valid"))
                s_bonus = 10 if eval_full.get("mrz_status") == "MRZ_VALID" else (5 if eval_full.get("mrz_status") == "MRZ_OCR_CORRECTED_CANDIDATE" else 0)
                full_score = v_count * 2 + s_bonus
                if full_score > best_score:
                    best_score = full_score
                    best_candidate = (raw_full, eval_full, full_document_lines)

    # If multi-pass completed and we have multiple line candidates, apply positional character consensus
    if len(pass_results) >= 2 and (not best_candidate or best_candidate[1].get("mrz_status") not in ["MRZ_VALID", "MRZ_OCR_CORRECTED_CANDIDATE"]):
        # Collect line 1 and line 2 variants normalized to 44 chars
        l1_variants = [normalize_mrz_line(pr["lines"][0], 44) for pr in pass_results if len(pr["lines"]) >= 2]
        l2_variants = [normalize_mrz_line(pr["lines"][1], 44) for pr in pass_results if len(pr["lines"]) >= 2]

        if l1_variants and l2_variants:
            consensus_l1 = []
            for col in range(44):
                chars = [v[col] for v in l1_variants if col < len(v)]
                most_common = max(set(chars), key=chars.count) if chars else "<"
                consensus_l1.append(most_common)

            consensus_l2 = []
            for col in range(44):
                chars = [v[col] for v in l2_variants if col < len(v)]
                most_common = max(set(chars), key=chars.count) if chars else "<"
                consensus_l2.append(most_common)

            consensus_raw = "".join(consensus_l1) + "\n" + "".join(consensus_l2)
            consensus_eval = parse_and_validate_mrz(consensus_raw)
            check_results = consensus_eval.get("checksum_results", {})
            c_valid_count = sum(1 for v in check_results.values() if isinstance(v, dict) and v.get("valid"))
            c_status_bonus = 10 if consensus_eval.get("mrz_status") == "MRZ_VALID" else (5 if consensus_eval.get("mrz_status") == "MRZ_OCR_CORRECTED_CANDIDATE" else 0)
            c_score = c_valid_count * 2 + c_status_bonus

            debug_meta["consensus_attempted"] = True
            debug_meta["consensus_status"] = consensus_eval.get("mrz_status")

            if c_score >= best_score:
                best_candidate = (consensus_raw, consensus_eval, best_candidate[2] if best_candidate else [])

    if best_candidate:
        return best_candidate[0], best_candidate[1], best_candidate[2], debug_meta

    # Fallback to empty MRZ result
    empty_res = parse_and_validate_mrz(None)
    return None, empty_res, [], debug_meta

def run_ocr_on_image(image_bgr: np.ndarray, document_type: str = "passport") -> Dict[str, Any]:
    """
    Multi-pass optical character recognition and field extraction:
    Pass 1: Primary preprocessed & perspective-corrected document OCR.
    Pass 2: Dedicated MRZ region extraction with adaptive multi-pass consensus.
    Pass 3: Illumination-normalized pass if needed for low-contrast/glare documents.
    """
    t0 = time.time()
    h_img, w_img = image_bgr.shape[:2]

    # Pass 1: Primary Image Full Document OCR
    lines, confidences = _run_single_engine_ocr(image_bgr)

    # Pass 2: Dedicated MRZ Region Pipeline (for documents with MRZ: passports, identity cards, visas)
    is_mrz_doc = document_type.lower() in ["passport", "identity_card", "id_card", "visa", "unknown"]
    if is_mrz_doc:
        mrz_raw, mrz_res, mrz_crop_lines, mrz_debug = _extract_mrz_with_consensus(image_bgr, document_type, full_document_lines=lines)
    else:
        mrz_raw, mrz_res, mrz_crop_lines, mrz_debug = None, parse_and_validate_mrz(None), [], {"method": "none_for_doc_type"}

    # Integrate MRZ lines with normalized bounding boxes if dedicated pass extracted lines
    if mrz_res.get("detected") and mrz_res.get("lines"):
        crop_bbox = mrz_debug.get("crop_bbox") or [0, int(h_img * 0.65), w_img, int(h_img * 0.35)]
        bx, by, bw, bh = crop_bbox
        existing_texts = [l["text"] for l in lines]
        for idx, m_line in enumerate(mrz_res["lines"]):
            if m_line not in existing_texts:
                line_y = by + int(bh * (0.15 + idx * 0.40))
                line_h = int(bh * 0.35)
                norm_box = {
                    "x": round(float(bx) / w_img * 100, 2),
                    "y": round(float(line_y) / h_img * 100, 2),
                    "w": round(float(bw) / w_img * 100, 2),
                    "h": round(float(line_h) / h_img * 100, 2)
                }
                lines.append({
                    "text": m_line,
                    "confidence": 0.98,
                    "bbox": [[float(bx), float(line_y)], [float(bx + bw), float(line_y)], [float(bx + bw), float(line_y + line_h)], [float(bx), float(line_y + line_h)]],
                    "norm_box": norm_box
                })
                confidences.append(0.98)

    # Pass 3: Illumination normalization if full page had very low line detection
    avg_conf_p1 = float(np.mean(confidences)) if confidences else 0.0
    if len(lines) < 4 or avg_conf_p1 < 0.60:
        norm_variant = normalize_illumination(image_bgr)
        p3_lines, p3_confs = _run_single_engine_ocr(norm_variant)
        existing_texts = [l["text"] for l in lines]
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
    fields, field_confidences = extract_fields_and_confidences(full_text, document_type, lines, mrz_override=mrz_res)

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
        "mrz_result": mrz_res,
        "mrz_debug": mrz_debug,
        "fields": fields
    }


DOCUMENT_STOP_WORDS = {
    "REPUBLIC", "PASSPORT", "PASSEPORT", "INDIA", "FRANCE", "UNION", "EUROPEAN",
    "DEUTSCHLAND", "ESPANA", "KINGDOM", "OFFICIAL", "NATIONALITY", "COUNTRY",
    "DATE", "BIRTH", "PLACE", "ISSUE", "EXPIRY", "AUTHORITY", "SIGNATURE",
    "TYPE", "CODE", "SEX", "GENDER", "SPECIMEN", "SAMPLE", "THESE ARE",
    "BY ORDER", "GOVERNMENT", "MINISTRY", "EMBASSY", "IDENTITY", "CARD",
    "PERMIT", "LICENSE", "FEDERATION", "EXPEDITION", "VALIDITY", "EXPIRED",
    "POB", "POI", "DOB", "SURNAME", "GIVEN", "NAMES", "NOM", "PRENOM", "PRENOMS",
    "APELLIDOS", "NOMBRE", "NOMBRES", "NACHNAME", "VORNAMEN", "COGNOME", "NOME",
    "HOLALOLPALKE", "CZNY", "LIDK", "HG TURI", "UEUNS", "CNQ", "BITH", "SUE", "FRH",
    "THESE", "REQUEST", "REQUIRE", "PRESIDENT"
}

SURNAME_LABEL_REGEX = re.compile(
    r"\b(?:SURNAME|NOM(?:\s+D['’]USAGE)?|FAMILY\s*NAME|NACHNAME|APELLIDOS|COGNOME|SURNAM|F/SURI|SURI)\b",
    re.IGNORECASE
)

GIVEN_NAMES_LABEL_REGEX = re.compile(
    r"\b(?:GIVEN\s*NAME[S]?|PR[EÉ]NOM[S]?|FIRST\s*NAME|FORENAME[S]?|VORNAME[N]?|NOMBRES|GIVENNAME|GIV\s*NSME|GIV\s*NAME)\b",
    re.IGNORECASE
)

FULL_NAME_LABEL_REGEX = re.compile(
    r"\b(?:FULL\s*NAME|HOLDER['’]?S\s*NAME|NOM\s*COMPLET|NAME\s*/\s*NOM)\b",
    re.IGNORECASE
)

def normalize_name_string(name: Optional[str]) -> Optional[str]:
    """
    Clean and normalize human name strings without destructive character substitutions.
    """
    if not name:
        return None
    import unicodedata
    norm = unicodedata.normalize("NFKC", str(name))
    norm = norm.replace("<", " ")
    norm = re.sub(r"[^A-Za-zÀ-ÿ\s\'-]", " ", norm)
    norm = re.sub(r"\s+", " ", norm).strip()
    if len(norm) < 2:
        return None
    return norm.upper()

def is_valid_name_candidate(cand: Optional[str]) -> bool:
    """Validate that candidate string is a plausible person name component."""
    if not cand or len(cand) < 2 or len(cand) > 45:
        return False
    if SURNAME_LABEL_REGEX.search(cand) or GIVEN_NAMES_LABEL_REGEX.search(cand) or FULL_NAME_LABEL_REGEX.search(cand):
        return False
    clean = normalize_name_string(cand)
    if not clean:
        return False
    words = clean.split()
    if not words or any(w in DOCUMENT_STOP_WORDS for w in words):
        return False
    if any(c.isdigit() for c in cand):
        return False
    return True

def extract_visual_name(lines: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract person name from visual inspection zone using label proximity and layout structure.
    """
    visual_surname = None
    visual_given = None
    visual_full = None
    conf_list = []

    line_texts = [l.get("text", "").strip() for l in lines if l.get("text")]
    line_confs = {l.get("text", "").strip(): l.get("confidence", 0.8) for l in lines if l.get("text")}

    for idx, txt in enumerate(line_texts):
        if "<" in txt and len(txt) > 20:
            continue

        # 1. Check Surname Label
        if SURNAME_LABEL_REGEX.search(txt):
            after_match = SURNAME_LABEL_REGEX.split(txt, maxsplit=1)[-1].strip(" :/-")
            if is_valid_name_candidate(after_match):
                visual_surname = normalize_name_string(after_match)
                conf_list.append(line_confs.get(txt, 0.9))
            else:
                if idx + 1 < len(line_texts) and is_valid_name_candidate(line_texts[idx + 1]):
                    visual_surname = normalize_name_string(line_texts[idx + 1])
                    conf_list.append(line_confs.get(line_texts[idx + 1], 0.9))
                elif idx > 0 and is_valid_name_candidate(line_texts[idx - 1]):
                    visual_surname = normalize_name_string(line_texts[idx - 1])
                    conf_list.append(line_confs.get(line_texts[idx - 1], 0.9))

        # 2. Check Given Names Label
        if GIVEN_NAMES_LABEL_REGEX.search(txt):
            after_match = GIVEN_NAMES_LABEL_REGEX.split(txt, maxsplit=1)[-1].strip(" :/-")
            if is_valid_name_candidate(after_match):
                visual_given = normalize_name_string(after_match)
                conf_list.append(line_confs.get(txt, 0.9))
            else:
                if idx + 1 < len(line_texts) and is_valid_name_candidate(line_texts[idx + 1]):
                    visual_given = normalize_name_string(line_texts[idx + 1])
                    conf_list.append(line_confs.get(line_texts[idx + 1], 0.9))
                elif idx > 0 and is_valid_name_candidate(line_texts[idx - 1]):
                    visual_given = normalize_name_string(line_texts[idx - 1])
                    conf_list.append(line_confs.get(line_texts[idx - 1], 0.9))

        # 3. Check Full Name Label
        if FULL_NAME_LABEL_REGEX.search(txt):
            after_match = FULL_NAME_LABEL_REGEX.split(txt, maxsplit=1)[-1].strip(" :/-")
            if is_valid_name_candidate(after_match):
                visual_full = normalize_name_string(after_match)
                conf_list.append(line_confs.get(txt, 0.9))

    if visual_given and visual_surname:
        visual_full = f"{visual_given} {visual_surname}"
    elif visual_given:
        visual_full = visual_given
    elif visual_surname:
        visual_full = visual_surname

    # Fallback: Detect standalone high-confidence person name candidate line
    if not visual_full:
        for txt in line_texts:
            if "<" in txt or len(txt) < 3 or len(txt) > 40:
                continue
            if re.match(r"^[A-Za-z]{2,20}\s+[A-Za-z]{2,20}(?:\s+[A-Za-z]{2,20})?$", txt):
                if is_valid_name_candidate(txt):
                    visual_full = normalize_name_string(txt)
                    conf_list.append(line_confs.get(txt, 0.9))
                    break

    avg_c = round(float(sum(conf_list) / len(conf_list)), 3) if conf_list else None
    return {
        "full_name": visual_full,
        "surname": visual_surname,
        "given_names": visual_given,
        "confidence": avg_c,
        "source": "VISUAL_OCR",
        "status": "EXTRACTED" if visual_full else "NOT_DETECTED"
    }

def evaluate_name_consistency(visual_name_dict: Dict[str, Any], mrz_name_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cross-check visual OCR extracted name against ICAO MRZ name.
    """
    from app.services.matching_service import jaro_winkler_similarity

    vis_full = normalize_name_string(visual_name_dict.get("full_name"))
    mrz_full = normalize_name_string(mrz_name_dict.get("full_name"))

    if not vis_full and not mrz_full:
        return {
            "status": "NOT_AVAILABLE",
            "visual_name": None,
            "mrz_name": None,
            "similarity": 0.0,
            "details": "No person name could be extracted from either Visual OCR or MRZ."
        }

    if not vis_full:
        return {
            "status": "SINGLE_SOURCE_ONLY",
            "visual_name": None,
            "mrz_name": mrz_full,
            "similarity": 1.0,
            "source": "MRZ",
            "details": "Name extracted solely from MRZ; visual label was unreadable or absent."
        }

    if not mrz_full:
        return {
            "status": "SINGLE_SOURCE_ONLY",
            "visual_name": vis_full,
            "mrz_name": None,
            "similarity": 1.0,
            "source": "VISUAL_OCR",
            "details": "Name extracted solely from Visual OCR; MRZ was unreadable or absent."
        }

    if vis_full == mrz_full:
        return {
            "status": "CONSISTENT",
            "visual_name": vis_full,
            "mrz_name": mrz_full,
            "similarity": 1.0,
            "details": "Visual OCR name matches MRZ name."
        }

    vis_tokens = set(vis_full.split())
    mrz_tokens = set(mrz_full.split())
    if vis_tokens == mrz_tokens:
        return {
            "status": "CONSISTENT",
            "visual_name": vis_full,
            "mrz_name": mrz_full,
            "similarity": 1.0,
            "details": "Visual and MRZ names match with inverted component order."
        }

    sim = jaro_winkler_similarity(vis_full, mrz_full)
    if sim >= 0.75:
        return {
            "status": "POSSIBLE_OCR_VARIATION",
            "visual_name": vis_full,
            "mrz_name": mrz_full,
            "similarity": sim,
            "details": f"Minor optical character variation between Visual ({vis_full}) and MRZ ({mrz_full})."
        }
    else:
        return {
            "status": "INCONSISTENT",
            "visual_name": vis_full,
            "mrz_name": mrz_full,
            "similarity": sim,
            "details": f"Discrepancy between Visual OCR ({vis_full}) and MRZ ({mrz_full})."
        }

def extract_fields_and_confidences(
    full_text: str,
    document_type: str,
    lines: List[Dict[str, Any]],
    mrz_override: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], Dict[str, Optional[float]]]:
    """
    Extract document-specific fields with field-level OCR confidence calculation
    and cross-field validation between Visual Inspection Zone and MRZ.
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
        "mrz_raw": None,
        "mrz_status": "MRZ_NOT_DETECTED",
        "name": {},
        "visual_name": {},
        "mrz_name": {},
        "name_consistency": {},
        "field_cross_checks": {}
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

    line_texts = [l.get("text", "").strip() for l in lines if l.get("text")]
    line_confs = {l.get("text", "").strip(): l.get("confidence", 0.8) for l in lines if l.get("text")}

    # 1. MRZ Data Source Integration (from dedicated pipeline or candidate scan)
    mrz_parsed_info = {}
    mrz_eval = mrz_override

    if not mrz_eval or not mrz_eval.get("detected"):
        mrz_candidates = [
            t for t in line_texts
            if (len(t) >= 28 and sum(1 for c in t if c.isalnum() or c == '<') >= len(t) * 0.75 and '<' in t) or t.startswith('P<') or t.startswith('I<')
        ]
        mrz_candidates.sort(key=lambda t: (len(t) == 44 or len(t) == 30, len(t)), reverse=True)
        if len(mrz_candidates) >= 2:
            p_lines = [l for l in mrz_candidates if l.startswith("P<") or l.startswith("I<")]
            other_lines = [l for l in mrz_candidates if not (l.startswith("P<") or l.startswith("I<"))]
            if p_lines and other_lines:
                ordered_mrz = [p_lines[0], other_lines[0]]
            else:
                ordered_mrz = mrz_candidates[:2]
            raw_mrz_str = "\n".join(ordered_mrz)
            mrz_eval = parse_and_validate_mrz(raw_mrz_str)

    if mrz_eval and mrz_eval.get("detected"):
        mrz_parsed_info = mrz_eval.get("fields", {})
        if mrz_eval.get("lines"):
            fields["mrz_raw"] = "\n".join(mrz_eval["lines"])
        elif mrz_eval.get("raw_line1") and mrz_eval.get("raw_line2"):
            fields["mrz_raw"] = f"{mrz_eval['raw_line1']}\n{mrz_eval['raw_line2']}"
        fields["mrz_status"] = mrz_eval.get("mrz_status", "MRZ_VALID" if mrz_eval.get("valid") else "MRZ_UNRELIABLE")
        field_conf["mrz"] = 0.98 if fields["mrz_status"] == "MRZ_VALID" else 0.88

    # 2. Extract Visual Document Number
    vis_doc_num = None
    vis_doc_conf = None
    for txt in line_texts:
        if '<' in txt and len(txt) > 20:
            continue
        doc_match = re.search(r"\b([A-Z][0-9]{7}|[A-Z]{2}[0-9]{7}|[A-Z]{1,3}\d{6,9})\b", txt)
        if doc_match:
            vis_doc_num = doc_match.group(1).upper()
            vis_doc_conf = round(float(line_confs.get(txt, 0.9)), 3)
            break

    mrz_doc_num = mrz_parsed_info.get("document_number")
    if isinstance(mrz_doc_num, dict):
        mrz_doc_num = mrz_doc_num.get("value")

    # Resolve document number priority & cross-check
    fields["document_number"] = vis_doc_num or mrz_doc_num
    field_conf["document_number"] = vis_doc_conf or field_conf.get("mrz", 0.95)

    doc_consistency = "NOT_AVAILABLE"
    if vis_doc_num and mrz_doc_num:
        if vis_doc_num.upper() == mrz_doc_num.upper():
            doc_consistency = "CONSISTENT"
        else:
            doc_consistency = "INCONSISTENT"
    elif vis_doc_num or mrz_doc_num:
        doc_consistency = "SINGLE_SOURCE_ONLY"

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

    # Fallback to MRZ dates if visual was missing
    mrz_dob = mrz_parsed_info.get("date_of_birth")
    if isinstance(mrz_dob, dict):
        mrz_dob = mrz_dob.get("value")
    if not fields["date_of_birth"] and mrz_dob:
        fields["date_of_birth"] = mrz_dob
        field_conf["date_of_birth"] = field_conf.get("mrz", 0.95)

    mrz_expiry = mrz_parsed_info.get("expiry_date")
    if isinstance(mrz_expiry, dict):
        mrz_expiry = mrz_expiry.get("value")
    if not fields["expiry_date"] and mrz_expiry:
        fields["expiry_date"] = mrz_expiry
        field_conf["expiry_date"] = field_conf.get("mrz", 0.95)

    # 4. Nationality / Issuing Country
    mrz_nat = mrz_parsed_info.get("nationality")
    if isinstance(mrz_nat, dict):
        mrz_nat = mrz_nat.get("value")

    if mrz_nat:
        fields["nationality"] = mrz_nat
        field_conf["nationality"] = 0.98
    else:
        nat_match = re.search(r"\b(FRA|USA|GBR|CAN|DEU|SGP|MYS|SRB|IND|AUS|JPN|ESP|ITA|NLD|SWE|CHE|CHN|BRA|MEX|ZAF|INDIAN|FRENCH|AMERICAN|BRITISH|MALAYSIAN|GERMAN)\b", full_text, re.IGNORECASE)
        if nat_match:
            val = nat_match.group(1).upper()
            norm_map = {"INDIAN": "IND", "FRENCH": "FRA", "AMERICAN": "USA", "BRITISH": "GBR", "MALAYSIAN": "MYS", "GERMAN": "DEU"}
            fields["nationality"] = norm_map.get(val, val)
            field_conf["nationality"] = 0.95

    # 5. Visual Name Extraction & MRZ Name Cross-Check
    visual_name_res = extract_visual_name(lines)
    mrz_name_val = mrz_parsed_info.get("full_name")
    if isinstance(mrz_name_val, dict):
        mrz_name_val = mrz_name_val.get("value")
    mrz_surname_val = mrz_parsed_info.get("surname")
    if isinstance(mrz_surname_val, dict):
        mrz_surname_val = mrz_surname_val.get("value")
    mrz_given_val = mrz_parsed_info.get("given_names")
    if isinstance(mrz_given_val, dict):
        mrz_given_val = mrz_given_val.get("value")

    mrz_name_res = {
        "full_name": mrz_name_val,
        "surname": mrz_surname_val,
        "given_names": mrz_given_val,
        "confidence": field_conf.get("mrz"),
        "source": "MRZ",
        "status": "EXTRACTED" if mrz_name_val else "NOT_DETECTED"
    }

    consistency_res = evaluate_name_consistency(visual_name_res, mrz_name_res)

    fields["visual_name"] = visual_name_res
    fields["mrz_name"] = mrz_name_res
    fields["name_consistency"] = consistency_res

    # For Passports: MRZ name is primary authoritative source if valid, otherwise visual OCR
    primary_name = None
    primary_surname = None
    primary_given = None
    primary_conf = 0.0
    primary_source = "NONE"

    if mrz_name_res.get("full_name"):
        primary_name = mrz_name_res["full_name"]
        primary_surname = mrz_name_res.get("surname")
        primary_given = mrz_name_res.get("given_names")
        primary_conf = mrz_name_res.get("confidence") or 0.95
        primary_source = "MRZ"
        if visual_name_res.get("surname") and not primary_surname:
            primary_surname = visual_name_res["surname"]
    elif visual_name_res.get("full_name"):
        primary_name = visual_name_res["full_name"]
        primary_surname = visual_name_res.get("surname")
        primary_given = visual_name_res.get("given_names")
        primary_conf = visual_name_res.get("confidence") or 0.90
        primary_source = "VISUAL_OCR"

    fields["full_name"] = primary_name
    fields["surname"] = primary_surname
    fields["given_names"] = primary_given
    fields["name"] = {
        "full_name": primary_name,
        "surname": primary_surname,
        "given_names": primary_given,
        "source": primary_source,
        "confidence": primary_conf,
        "status": "EXTRACTED" if primary_name else "REQUIRES_REVIEW"
    }
    field_conf["full_name"] = primary_conf

    # 6. Sex / Gender
    mrz_gender = mrz_parsed_info.get("gender")
    if isinstance(mrz_gender, dict):
        mrz_gender = mrz_gender.get("value")
    if mrz_gender and mrz_gender in ["M", "F", "X"]:
        fields["gender"] = mrz_gender
        fields["sex"] = mrz_gender
        field_conf["gender"] = 0.98
    else:
        gender_match = re.search(r"\b(?:SEX|GENDER)[:\s/]*([MFX])\b", full_text, re.IGNORECASE)
        if gender_match:
            val = gender_match.group(1).upper()
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
                if not any(k in cand.upper() for k in DOCUMENT_STOP_WORDS) and cand != primary_name:
                    fields["place_of_birth"] = cand
        elif any(k in txt.lower() for k in ["place of issue", "poi"]):
            if idx + 1 < len(line_texts):
                cand = line_texts[idx + 1].strip()
                if not any(k in cand.upper() for k in DOCUMENT_STOP_WORDS) and cand != primary_name:
                    fields["place_of_issue"] = cand

    fields["field_cross_checks"] = {
        "document_number": {
            "status": doc_consistency,
            "visual_value": vis_doc_num,
            "mrz_value": mrz_doc_num
        },
        "name": consistency_res
    }

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
