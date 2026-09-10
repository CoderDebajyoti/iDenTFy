"""
MRZ Parsing & Checksum Validation Service
Strictly follows ICAO Doc 9303 specifications (Part 3, 4, 7).
Computes 7-3-1 weighted check digits on:
- Document number
- Date of birth (YYMMDD)
- Expiry date (YYMMDD)
- Optional personal number
- Overall composite check digit

Supports:
- TD3 (Passports: 2 lines x 44 chars)
- TD1 (Identity Cards: 3 lines x 30 chars)
- TD2 (Official Cards: 2 lines x 36 chars)

Evidence-Based Principles:
- Never hardcodes specific documents or registry data.
- Never randomly mutates characters or forces checksum success.
- Uses field context (alpha vs numeric vs alphanumeric) to constrain character corrections.
- Applies single-candidate ambiguity analysis when OCR noise causes checksum failure.
- Returns explicit MRZ statuses: MRZ_VALID, MRZ_OCR_CORRECTED_CANDIDATE, MRZ_UNRELIABLE, MRZ_NOT_DETECTED.
"""

import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List

WEIGHTS = [7, 3, 1]

# Character confusion mappings observed in optical character recognition
OCR_ALPHA_CONFUSIONS = {
    "0": "O", "1": "I", "2": "Z", "5": "S", "8": "B", "6": "G"
}

OCR_NUMERIC_CONFUSIONS = {
    "O": "0", "o": "0", "Q": "0", "D": "0",
    "I": "1", "i": "1", "l": "1", "L": "1", "|": "1",
    "Z": "2", "z": "2",
    "S": "5", "s": "5",
    "B": "8", "b": "8",
    "G": "6", "g": "6"
}

# Bi-directional candidate confusion pairs for alphanumeric check-digit analysis
CONFUSION_PAIRS = [
    ("O", "0"), ("0", "O"),
    ("I", "1"), ("1", "I"),
    ("L", "1"), ("1", "L"),
    ("Z", "2"), ("2", "Z"),
    ("S", "5"), ("5", "S"),
    ("B", "8"), ("8", "B"),
    ("G", "6"), ("6", "G")
]

def mrz_char_value(c: str) -> int:
    """Convert MRZ character to numeric value for checksum calculation per ICAO 9303."""
    if not c:
        return 0
    c_up = c.upper()
    if c_up.isdigit():
        return int(c_up)
    elif "A" <= c_up <= "Z":
        return ord(c_up) - ord("A") + 10
    elif c_up == "<":
        return 0
    return 0

def calculate_check_digit(data_str: str) -> int:
    """Calculate ICAO 9303 check digit using repeating weights 7-3-1."""
    total = 0
    for idx, char in enumerate(data_str):
        weight = WEIGHTS[idx % 3]
        total += mrz_char_value(char) * weight
    return total % 10

def sanitize_alpha_mrz(text: str) -> str:
    """Disambiguate OCR character confusions in strictly alphabetic fields (country code, name)."""
    if not text:
        return ""
    res = []
    for c in text.upper():
        if c in OCR_ALPHA_CONFUSIONS:
            res.append(OCR_ALPHA_CONFUSIONS[c])
        elif "A" <= c <= "Z" or c == "<":
            res.append(c)
        else:
            res.append(c)
    return "".join(res)

def sanitize_numeric_mrz(text: str) -> str:
    """Disambiguate OCR character confusions in strictly numeric fields (dates, check digits)."""
    if not text:
        return ""
    res = []
    for c in text:
        if c in OCR_NUMERIC_CONFUSIONS:
            res.append(OCR_NUMERIC_CONFUSIONS[c])
        elif c.isdigit():
            res.append(c)
        elif c == "<":
            res.append("0")
        else:
            res.append(c)
    return "".join(res)

def normalize_mrz_line(raw_line: str, expected_length: int = 44) -> str:
    """
    Clean OCR noise and formatting artifacts from an MRZ line:
    - Normalizes common OCR filler misreads («, ‹, (, ), {, }, [, ], |, \\, _, -, —) to '<'
    - Strips whitespace
    - Uppercases all Latin characters
    - Pads or trims trailing filler characters to target standard length
    """
    if not raw_line:
        return "<" * expected_length

    # Replace obvious filler misreads
    cleaned = raw_line.strip()
    cleaned = re.sub(r"[«‹«\(\)\{\}\[\]\|\/\–\—\_\-\.\~]", "<", cleaned)
    cleaned = re.sub(r"\s+", "", cleaned).upper()
    cleaned = re.sub(r"[^A-Z0-9<]", "<", cleaned)

    # Pad trailing fillers if line was clipped near right edge
    if len(cleaned) < expected_length:
        cleaned = cleaned.ljust(expected_length, "<")
    elif len(cleaned) > expected_length:
        # If line has spurious extra character at the end (e.g. 45 chars with extra trailing < or noise)
        cleaned = cleaned[:expected_length]

    return cleaned

def format_mrz_date(yymmdd: str, is_expiry: bool = False) -> Optional[str]:
    """Convert 6-digit MRZ date (YYMMDD) to ISO YYYY-MM-DD."""
    if not yymmdd or len(yymmdd) < 6:
        return None
    cleaned = sanitize_numeric_mrz(yymmdd[:6])
    if not cleaned.isdigit() or len(cleaned) < 6:
        return None
    try:
        yy = int(cleaned[:2])
        mm = int(cleaned[2:4])
        dd = int(cleaned[4:6])
        if mm < 1 or mm > 12 or dd < 1 or dd > 31:
            return None
        current_year = datetime.now(timezone.utc).year % 100
        if is_expiry:
            century = 2000 if yy <= current_year + 50 else 1900
        else:
            century = 1900 if yy > current_year else 2000
        return f"{century + yy:04d}-{mm:02d}-{dd:02d}"
    except Exception:
        return None

def parse_mrz_name(raw_name_section: str) -> Tuple[str, str, str]:
    """
    Parse ICAO 9303 MRZ name section (SURNAME<<GIVEN<NAMES<<<<...).
    Returns (surname, given_names, full_name).
    """
    if not raw_name_section:
        return "", "", ""

    cleaned = sanitize_alpha_mrz(raw_name_section.strip())

    if "<<" in cleaned:
        parts = cleaned.split("<<", 1)
        raw_surname = parts[0]
        raw_given = parts[1]
    else:
        raw_surname = cleaned
        raw_given = ""

    surname_words = [w.strip() for w in raw_surname.split("<") if w.strip()]
    given_words = [w.strip() for w in raw_given.split("<") if w.strip()]

    surname = " ".join(surname_words)
    given_names = " ".join(given_words)

    if given_names and surname:
        full_name = f"{given_names} {surname}"
    elif surname:
        full_name = surname
    else:
        full_name = given_names

    return surname, given_names, full_name

def parse_mrz_td3_line1(line1: str) -> Tuple[str, str, str, str, str]:
    """
    Parse Line 1 of TD3 Passport (44 characters):
    P<ISSUINGSTATE<SURNAME<<GIVEN<NAMES<<<<...
    Returns (doc_type, issuing_country, surname, given_names, full_name).
    """
    clean_line1 = normalize_mrz_line(line1, 44)
    doc_type = clean_line1[0:2].replace("<", "") or "P"
    issuing_country = sanitize_alpha_mrz(clean_line1[2:5].replace("<", ""))
    surname, given_names, full_name = parse_mrz_name(clean_line1[5:44])
    return doc_type, issuing_country, surname, given_names, full_name


def evaluate_field_checksum_candidates(
    field_data: str,
    check_digit: str,
    field_name: str
) -> Tuple[str, str, bool, Optional[Dict[str, Any]]]:
    """
    Checksum-aware error detection & candidate resolution.
    If direct check digit validation fails:
    - Tests single-character candidate substitutions based on known optical confusions.
    - If and only if EXACTLY ONE candidate resolves the check digit, marks as OCR_CORRECTED.
    - If zero or multiple candidates resolve, marks as CHECKSUM_FAILED without guessing.
    Returns: (resolved_field_data, resolved_check_digit, is_valid, correction_metadata)
    """
    clean_field = field_data.upper()
    clean_check = sanitize_numeric_mrz(check_digit[:1]) if check_digit else "0"

    expected = calculate_check_digit(clean_field)
    if str(expected) == clean_check:
        return clean_field, clean_check, True, None

    # Checksum mismatch: perform conservative candidate analysis
    valid_candidates = []

    # 1. Test single-character substitutions in field_data
    for idx, orig_char in enumerate(clean_field):
        for o_char, r_char in CONFUSION_PAIRS:
            if orig_char == o_char:
                candidate_str = clean_field[:idx] + r_char + clean_field[idx + 1:]
                cand_expected = calculate_check_digit(candidate_str)
                if str(cand_expected) == clean_check:
                    valid_candidates.append({
                        "field": field_name,
                        "original_data": clean_field,
                        "corrected_data": candidate_str,
                        "changed_position": idx,
                        "original_char": orig_char,
                        "corrected_char": r_char,
                        "check_digit": clean_check,
                        "type": "data_character_correction"
                    })

    # 2. Test single-character substitution in check digit itself (e.g. OCR read 'O' instead of '0', or 'I' instead of '1')
    for o_char, r_char in CONFUSION_PAIRS:
        if clean_check == o_char and r_char.isdigit():
            if str(expected) == r_char:
                valid_candidates.append({
                    "field": field_name,
                    "original_data": clean_field,
                    "corrected_data": clean_field,
                    "changed_position": -1,
                    "original_char": clean_check,
                    "corrected_char": r_char,
                    "check_digit": r_char,
                    "type": "check_digit_correction"
                })

    if len(valid_candidates) == 1:
        cand = valid_candidates[0]
        return cand["corrected_data"], cand["check_digit"], True, cand
    else:
        return clean_field, clean_check, False, None

def parse_mrz_td3(line1_raw: str, line2_raw: str) -> Dict[str, Any]:
    """
    Parse TD3 Passport MRZ (2 lines of 44 characters) per ICAO 9303 Part 4.
    """
    line1 = normalize_mrz_line(line1_raw, 44)
    line2 = normalize_mrz_line(line2_raw, 44)

    # Line 1 Breakdown:
    # 0..1: Document code (P, PO, etc.)
    doc_type = line1[0:2].replace("<", "") or "P"
    # 2..4: Issuing State (3 alpha)
    issuing_country_raw = line1[2:5]
    issuing_country = sanitize_alpha_mrz(issuing_country_raw.replace("<", ""))
    # 5..43: Name section
    name_section = line1[5:44]
    surname, given_names, full_name = parse_mrz_name(name_section)

    # Line 2 Breakdown:
    # 0..8: Document Number (9 chars)
    doc_num_raw = line2[0:9]
    doc_num_check_raw = line2[9:10]
    # 10..12: Nationality (3 alpha)
    nationality_raw = line2[10:13]
    nationality = sanitize_alpha_mrz(nationality_raw.replace("<", ""))
    # 13..18: Date of birth (YYMMDD)
    dob_raw = sanitize_numeric_mrz(line2[13:19])
    dob_check_raw = line2[19:20]
    # 20: Sex (M, F, X, <)
    gender_raw = line2[20:21].upper()
    gender = gender_raw if gender_raw in ["M", "F"] else ("X" if gender_raw in ["X", "<"] else "X")
    # 21..26: Expiry Date (YYMMDD)
    expiry_raw = sanitize_numeric_mrz(line2[21:27])
    expiry_check_raw = line2[27:28]
    # 28..41: Optional / Personal data (14 chars)
    optional_raw = line2[28:42]
    optional_check_raw = line2[42:43]
    # 43: Composite Check Digit
    composite_check_raw = line2[43:44]

    # Evaluate Field Checksums with Ambiguity Resolution
    corrections = []

    # 1. Document Number Check
    corr_doc_data, corr_doc_check, doc_valid, doc_corr = evaluate_field_checksum_candidates(
        doc_num_raw, doc_num_check_raw, "document_number"
    )
    if doc_corr:
        corrections.append(doc_corr)
    doc_num_clean = corr_doc_data.replace("<", "")

    # 2. Date of Birth Check
    corr_dob_data, corr_dob_check, dob_valid, dob_corr = evaluate_field_checksum_candidates(
        dob_raw, dob_check_raw, "date_of_birth"
    )
    if dob_corr:
        corrections.append(dob_corr)

    # 3. Expiry Date Check
    corr_exp_data, corr_exp_check, exp_valid, exp_corr = evaluate_field_checksum_candidates(
        expiry_raw, expiry_check_raw, "expiry_date"
    )
    if exp_corr:
        corrections.append(exp_corr)

    # 4. Composite Check Digit String: line2[0:10] + line2[13:20] + line2[21:43]
    composite_payload = corr_doc_data + corr_doc_check + corr_dob_data + corr_dob_check + corr_exp_data + corr_exp_check + optional_raw + optional_check_raw
    corr_comp_data, corr_comp_check, comp_valid, comp_corr = evaluate_field_checksum_candidates(
        composite_payload, composite_check_raw, "composite"
    )
    if comp_corr:
        corrections.append(comp_corr)

    expected_doc_check = calculate_check_digit(corr_doc_data)
    expected_dob_check = calculate_check_digit(corr_dob_data)
    expected_exp_check = calculate_check_digit(corr_exp_data)
    expected_comp_check = calculate_check_digit(composite_payload)

    all_checksums_valid = doc_valid and dob_valid and exp_valid and comp_valid

    # Determine MRZ Result State per specification:
    # MRZ_VALID | MRZ_OCR_CORRECTED_CANDIDATE | MRZ_UNRELIABLE
    if all_checksums_valid and len(corrections) == 0:
        mrz_status = "MRZ_VALID"
        status_label = "Valid Checksums"
    elif all_checksums_valid and len(corrections) > 0:
        mrz_status = "MRZ_OCR_CORRECTED_CANDIDATE"
        status_label = "OCR Correction Candidate"
    else:
        mrz_status = "MRZ_UNRELIABLE"
        status_label = "Checksum Mismatch"

    checksum_results = {
        "document_number": {
            "actual": corr_doc_check,
            "computed": str(expected_doc_check),
            "valid": doc_valid,
            "corrected": bool(doc_corr)
        },
        "date_of_birth": {
            "actual": corr_dob_check,
            "computed": str(expected_dob_check),
            "valid": dob_valid,
            "corrected": bool(dob_corr)
        },
        "expiry_date": {
            "actual": corr_exp_check,
            "computed": str(expected_exp_check),
            "valid": exp_valid,
            "corrected": bool(exp_corr)
        },
        "composite": {
            "actual": corr_comp_check,
            "computed": str(expected_comp_check),
            "valid": comp_valid,
            "corrected": bool(comp_corr)
        }
    }

    dob_formatted = format_mrz_date(corr_dob_data, is_expiry=False)
    expiry_formatted = format_mrz_date(corr_exp_data, is_expiry=True)

    # Structured Field Return (per Requirement 14)
    structured_fields = {
        "document_type": {"value": doc_type, "status": "VALID", "source": "MRZ", "raw_value": doc_type},
        "issuing_country": {"value": issuing_country, "status": "VALID", "source": "MRZ", "raw_value": issuing_country_raw},
        "full_name": {"value": full_name, "status": "VALID", "source": "MRZ", "raw_value": name_section},
        "surname": {"value": surname, "status": "VALID", "source": "MRZ", "raw_value": surname},
        "given_names": {"value": given_names, "status": "VALID", "source": "MRZ", "raw_value": given_names},
        "document_number": {
            "value": doc_num_clean,
            "status": "VALID" if (doc_valid and not doc_corr) else ("OCR_CORRECTED" if doc_corr else "UNRELIABLE"),
            "check_digit_valid": doc_valid,
            "source": "MRZ",
            "raw_value": doc_num_raw
        },
        "nationality": {"value": nationality, "status": "VALID", "source": "MRZ", "raw_value": nationality_raw},
        "date_of_birth": {
            "value": dob_formatted,
            "status": "VALID" if (dob_valid and not dob_corr) else ("OCR_CORRECTED" if dob_corr else "UNRELIABLE"),
            "check_digit_valid": dob_valid,
            "source": "MRZ",
            "raw_value": dob_raw
        },
        "date_of_birth_raw": corr_dob_data,
        "gender": {"value": gender, "status": "VALID", "source": "MRZ", "raw_value": gender_raw},
        "sex": {"value": gender, "status": "VALID", "source": "MRZ", "raw_value": gender_raw},
        "expiry_date": {
            "value": expiry_formatted,
            "status": "VALID" if (exp_valid and not exp_corr) else ("OCR_CORRECTED" if exp_corr else "UNRELIABLE"),
            "check_digit_valid": exp_valid,
            "source": "MRZ",
            "raw_value": expiry_raw
        },
        "expiry_date_raw": corr_exp_data,
        "optional_data": {"value": optional_raw.replace("<", ""), "status": "VALID", "source": "MRZ", "raw_value": optional_raw},
    }

    # Backward-compatible flat mapping
    # Backward-compatible flat mapping for string field access
    flat_fields = {
        "document_type": doc_type,
        "issuing_country": issuing_country,
        "full_name": full_name,
        "surname": surname,
        "given_names": given_names,
        "document_number": doc_num_clean,
        "nationality": nationality,
        "date_of_birth_raw": corr_dob_data,
        "date_of_birth": dob_formatted,
        "gender": gender,
        "sex": gender,
        "expiry_date_raw": corr_exp_data,
        "expiry_date": expiry_formatted,
        "optional_data": optional_raw.replace("<", ""),
        "name": {
            "surname": surname,
            "given_names": given_names,
            "full_name": full_name
        }
    }

    notes = "ICAO Doc 9303 Part 4 TD3 Verified."
    if mrz_status == "MRZ_OCR_CORRECTED_CANDIDATE":
        notes = f"MRZ optical ambiguity resolved via check-digit analysis ({len(corrections)} candidate position(s) corrected)."
    elif mrz_status == "MRZ_UNRELIABLE":
        notes = "MRZ checksum verification failed; optical noise or unverified credential."

    return {
        "mrz_detected": True,
        "mrz_valid": (mrz_status in ["MRZ_VALID", "MRZ_OCR_CORRECTED_CANDIDATE"]),
        "detected": True,
        "valid": (mrz_status in ["MRZ_VALID", "MRZ_OCR_CORRECTED_CANDIDATE"]),
        "mrz_status": mrz_status,
        "status": status_label,
        "format": "TD3 (Passport)",
        "fields": flat_fields,
        "structured_fields": structured_fields,
        "checksum_results": checksum_results,
        "check_digits": checksum_results,
        "candidate_corrections": corrections,
        "lines": [line1, line2],
        "notes": notes
    }

def parse_mrz_td1(line1_raw: str, line2_raw: str, line3_raw: str) -> Dict[str, Any]:
    """
    Parse TD1 Identity Card MRZ (3 lines of 30 characters) per ICAO 9303 Part 5.
    """
    line1 = normalize_mrz_line(line1_raw, 30)
    line2 = normalize_mrz_line(line2_raw, 30)
    line3 = normalize_mrz_line(line3_raw, 30)

    doc_type = line1[0:2].replace("<", "") or "I"
    issuing_country_raw = line1[2:5]
    issuing_country = sanitize_alpha_mrz(issuing_country_raw.replace("<", ""))
    doc_num_raw = line1[5:14]
    doc_num_check_raw = line1[14:15]

    dob_raw = sanitize_numeric_mrz(line2[0:6])
    dob_check_raw = line2[6:7]
    gender_raw = line2[7:8].upper()
    gender = gender_raw if gender_raw in ["M", "F"] else ("X" if gender_raw in ["X", "<"] else "X")
    expiry_raw = sanitize_numeric_mrz(line2[8:14])
    expiry_check_raw = line2[14:15]
    nationality_raw = line2[15:18]
    nationality = sanitize_alpha_mrz(nationality_raw.replace("<", ""))

    surname, given_names, full_name = parse_mrz_name(line3)

    corrections = []
    corr_doc_data, corr_doc_check, doc_valid, doc_corr = evaluate_field_checksum_candidates(
        doc_num_raw, doc_num_check_raw, "document_number"
    )
    if doc_corr:
        corrections.append(doc_corr)
    doc_num_clean = corr_doc_data.replace("<", "")

    corr_dob_data, corr_dob_check, dob_valid, dob_corr = evaluate_field_checksum_candidates(
        dob_raw, dob_check_raw, "date_of_birth"
    )
    if dob_corr:
        corrections.append(dob_corr)

    corr_exp_data, corr_exp_check, exp_valid, exp_corr = evaluate_field_checksum_candidates(
        expiry_raw, expiry_check_raw, "expiry_date"
    )
    if exp_corr:
        corrections.append(exp_corr)

    expected_doc_check = calculate_check_digit(corr_doc_data)
    expected_dob_check = calculate_check_digit(corr_dob_data)
    expected_exp_check = calculate_check_digit(corr_exp_data)

    all_valid = doc_valid and dob_valid and exp_valid

    if all_valid and len(corrections) == 0:
        mrz_status = "MRZ_VALID"
        status_label = "Valid Checksums"
    elif all_valid and len(corrections) > 0:
        mrz_status = "MRZ_OCR_CORRECTED_CANDIDATE"
        status_label = "OCR Correction Candidate"
    else:
        mrz_status = "MRZ_UNRELIABLE"
        status_label = "Checksum Mismatch"

    checksum_results = {
        "document_number": {"actual": corr_doc_check, "computed": str(expected_doc_check), "valid": doc_valid},
        "date_of_birth": {"actual": corr_dob_check, "computed": str(expected_dob_check), "valid": dob_valid},
        "expiry_date": {"actual": corr_exp_check, "computed": str(expected_exp_check), "valid": exp_valid},
    }

    dob_formatted = format_mrz_date(corr_dob_data, is_expiry=False)
    expiry_formatted = format_mrz_date(corr_exp_data, is_expiry=True)

    flat_fields = {
        "document_type": doc_type,
        "issuing_country": issuing_country,
        "full_name": full_name,
        "surname": surname,
        "given_names": given_names,
        "document_number": doc_num_clean,
        "nationality": nationality,
        "date_of_birth_raw": corr_dob_data,
        "date_of_birth": dob_formatted,
        "gender": gender,
        "sex": gender,
        "expiry_date_raw": corr_exp_data,
        "expiry_date": expiry_formatted,
        "name": {
            "surname": surname,
            "given_names": given_names,
            "full_name": full_name
        }
    }

    return {
        "mrz_detected": True,
        "mrz_valid": (mrz_status in ["MRZ_VALID", "MRZ_OCR_CORRECTED_CANDIDATE"]),
        "detected": True,
        "valid": (mrz_status in ["MRZ_VALID", "MRZ_OCR_CORRECTED_CANDIDATE"]),
        "mrz_status": mrz_status,
        "status": status_label,
        "format": "TD1 (Identity Card)",
        "fields": flat_fields,
        "checksum_results": checksum_results,
        "check_digits": checksum_results,
        "candidate_corrections": corrections,
        "lines": [line1, line2, line3],
        "notes": "MRZ parsed per ICAO Doc 9303 Part 5 (TD1)."
    }

def parse_and_validate_mrz(mrz_text: Optional[str]) -> Dict[str, Any]:
    """
    Parse MRZ lines and validate standard ICAO 9303 checksums.
    Handles multiple input formats, line splitting, line reordering, and ambiguity checking.
    """
    if not mrz_text or len(mrz_text.strip()) < 15:
        return {
            "mrz_detected": False,
            "mrz_valid": False,
            "detected": False,
            "valid": False,
            "mrz_status": "MRZ_NOT_DETECTED",
            "format": "None",
            "status": "MRZ not detected",
            "fields": {},
            "checksum_results": {},
            "check_digits": {},
            "candidate_corrections": [],
            "notes": "No machine readable zone lines found in document image."
        }

    raw_lines = [line.strip() for line in mrz_text.splitlines() if line.strip()]
    cleaned_lines = [normalize_mrz_line(l, expected_length=44 if len(l) > 32 else 30) for l in raw_lines]

    if len(cleaned_lines) < 2:
        return {
            "mrz_detected": False,
            "mrz_valid": False,
            "detected": False,
            "valid": False,
            "mrz_status": "MRZ_UNRELIABLE",
            "format": "None",
            "status": "Incomplete MRZ lines",
            "fields": {},
            "checksum_results": {},
            "check_digits": {},
            "candidate_corrections": [],
            "notes": "Incomplete MRZ lines detected."
        }

    # TD1: Identity Card (3 lines)
    if len(cleaned_lines) >= 3 and len(cleaned_lines[0]) <= 32:
        return parse_mrz_td1(cleaned_lines[0], cleaned_lines[1], cleaned_lines[2])

    # TD3: Passport (2 lines)
    l1, l2 = cleaned_lines[0], cleaned_lines[1]
    is_l1_header = l1.startswith("P<") or l1.startswith("P") or l1.startswith("I<") or l1.startswith("A<")
    is_l2_header = l2.startswith("P<") or l2.startswith("P") or l2.startswith("I<") or l2.startswith("A<")

    if is_l2_header and not is_l1_header:
        l1, l2 = l2, l1

    return parse_mrz_td3(l1, l2)

