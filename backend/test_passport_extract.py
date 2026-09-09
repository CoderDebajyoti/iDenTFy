import re
import cv2
import numpy as np
from datetime import datetime
from rapidocr_onnxruntime import RapidOCR
from app.services.mrz_service import parse_and_validate_mrz

engine = RapidOCR()

def extract_fields(image_bgr):
    h_img, w_img = image_bgr.shape[:2]
    results, _ = engine(image_bgr)
    lines = []
    line_texts = []
    if results:
        for res in results:
            bbox, text, conf = res[0], res[1], res[2]
            cleaned = text.strip()
            if cleaned:
                lines.append({"text": cleaned, "conf": float(conf), "bbox": bbox})
                line_texts.append(cleaned)

    full_text = "\n".join(line_texts)

    # Find MRZ lines
    mrz_candidates = [
        t for t in line_texts
        if (len(t) >= 28 and sum(1 for c in t if c.isalnum() or c == '<') >= len(t) * 0.75 and '<' in t) or t.startswith('P<') or t.startswith('I<')
    ]
    mrz_raw = None
    if len(mrz_candidates) >= 2:
        p_lines = [l for l in mrz_candidates if l.startswith('P<') or l.startswith('I<')]
        other_lines = [l for l in mrz_candidates if not (l.startswith('P<') or l.startswith('I<'))]
        if p_lines and other_lines:
            mrz_raw = f"{p_lines[0]}\n{other_lines[0]}"
        else:
            mrz_raw = f"{mrz_candidates[0]}\n{mrz_candidates[1]}"
    elif len(mrz_candidates) == 1:
        mrz_raw = mrz_candidates[0]

    mrz_res = parse_and_validate_mrz(mrz_raw)
    mrz_f = mrz_res.get("fields", {})

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
        "mrz_raw": mrz_raw
    }

    # Extract Document Number
    for txt in line_texts:
        if '<' in txt:
            continue
        m = re.search(r"\b([A-Z][0-9]{7}|[A-Z]{2}[0-9]{7})\b", txt)
        if m:
            fields["document_number"] = m.group(1).upper()
            break

    # Extract Dates
    date_regex = re.compile(r"\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b")
    all_dates = []
    for idx, txt in enumerate(line_texts):
        if '<' in txt and len(txt) > 20:
            continue
        matches = date_regex.findall(txt)
        for d in matches:
            prev = line_texts[idx-1] if idx > 0 else ""
            ctx = f"{prev} {txt}".lower()
            if any(k in ctx for k in ["birth", "dob", "bith", "d.o.b"]):
                fields["date_of_birth"] = d
            elif any(k in ctx for k in ["expiry", "expir", "valid until"]):
                fields["expiry_date"] = d
            elif any(k in ctx for k in ["issue", "issued", "sue"]):
                fields["issue_date"] = d
            all_dates.append(d)

    # Name extraction
    for idx, txt in enumerate(line_texts):
        if '<' in txt or len(txt) < 3:
            continue
        if re.search(r"Given\s*Name|Surname|Name\(s\)", txt, re.IGNORECASE):
            if idx + 1 < len(line_texts):
                cand = line_texts[idx+1].strip()
                if not any(k in cand.upper() for k in ["REPUBLIC", "PASSPORT", "INDIA", "TYPE", "CODE", "SEX", "DATE"]):
                    fields["full_name"] = cand.title()
                    break

    # Supplement from MRZ
    for k in ["full_name", "document_number", "nationality", "gender", "sex", "date_of_birth", "expiry_date"]:
        if not fields[k] and mrz_f.get(k):
            fields[k] = mrz_f[k]

    return fields, mrz_res

for sample in ['../demo_samples/sample_valid_passport.jpg', '../demo_samples/Screenshot 2026-09-10 004248.png', '../demo_samples/Screenshot 2026-09-10 004414.png']:
    img = cv2.imread(sample)
    f, m = extract_fields(img)
    print(f"\n=== RESULT FOR {sample} ===")
    print("Full Name:", f["full_name"])
    print("Doc Number:", f["document_number"])
    print("DOB:", f["date_of_birth"])
    print("Nationality:", f["nationality"])
    print("Issue Date:", f["issue_date"])
    print("Expiry Date:", f["expiry_date"])
    print("MRZ Detected:", m.get("detected"))
    print("MRZ Status:", m.get("status"))
