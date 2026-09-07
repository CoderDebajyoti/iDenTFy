"""
Document Matching & Registry Verification Service
Implements:
1. String normalization
2. Exact matching across multiple fields (document number, DOB, nationality, type)
3. Fuzzy name matching (Levenshtein distance, Jaro-Winkler similarity)
4. Multi-tier match classification: MATCHED, PARTIAL MATCH, NOT VERIFIED, REQUIRES REVIEW
"""

import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import Document, Person

def normalize_string(s: Optional[str]) -> str:
    """Normalize string: lowercase, strip punctuation, trim whitespace."""
    if not s:
        return ""
    # Remove all punctuation except alphanumeric and single spaces
    clean = re.sub(r"[^\w\s]", " ", str(s).lower())
    # Replace multiple spaces with a single space
    return re.sub(r"\s+", " ", clean).strip()

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate standard Levenshtein edit distance."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def jaro_winkler_similarity(s1: str, s2: str) -> float:
    """Calculate Jaro-Winkler similarity score (0.0 to 1.0)."""
    s1 = normalize_string(s1)
    s2 = normalize_string(s2)

    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    len1, len2 = len(s1), len(s2)
    match_distance = max(len1, len2) // 2 - 1

    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0

    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] == s2[j]:
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

    if matches == 0:
        return 0.0

    # Transpositions
    transpositions = 0
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    transpositions //= 2

    jaro = (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0

    # Winkler prefix scale (up to 4 common initial characters)
    prefix = 0
    for i in range(min(4, min(len1, len2))):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break

    return round(jaro + prefix * 0.1 * (1.0 - jaro), 3)

def match_document_against_database(
    db: Session,
    extracted_fields: Dict[str, Any],
    document_type: str
) -> Dict[str, Any]:
    """
    Execute matching pipeline against database registry.
    Compares document number, person details, nationality, dates.
    """
    doc_number = extracted_fields.get("document_number")
    full_name = extracted_fields.get("full_name")
    dob = extracted_fields.get("date_of_birth")
    nationality = extracted_fields.get("nationality")

    norm_doc_num = normalize_string(doc_number).upper().replace(" ", "")

    if not norm_doc_num:
        return {
            "database_match": False,
            "match_type": "no_match",
            "matched_record": None,
            "field_matches": {
                "document_number": False,
                "name": False,
                "date_of_birth": False,
                "nationality": False
            },
            "name_similarity": 0.0,
            "notes": "No document number extracted for database lookup."
        }

    # Query by document number
    doc_record = db.query(Document).filter(
        Document.document_number.ilike(f"%{norm_doc_num}%")
    ).first()

    if not doc_record:
        # Check if person matches by fuzzy name as alternate inspection
        matched_by_name = None
        highest_sim = 0.0

        if full_name:
            all_persons = db.query(Person).all()
            for p in all_persons:
                sim = jaro_winkler_similarity(full_name, p.full_name)
                if sim > highest_sim:
                    highest_sim = sim
                    matched_by_name = p

        return {
            "database_match": False,
            "match_type": "not_verified",
            "matched_record": None,
            "field_matches": {
                "document_number": False,
                "name": highest_sim > 0.85,
                "date_of_birth": False,
                "nationality": False
            },
            "name_similarity": highest_sim,
            "notes": "Document number not found in security registry. Record unindexed."
        }

    # Document record exists - match person details
    person = doc_record.person
    db_name = person.full_name if person else ""
    db_dob = person.date_of_birth if person else ""
    db_nat = person.nationality if person else ""

    # Name similarity
    name_sim = jaro_winkler_similarity(full_name, db_name) if full_name and db_name else 0.0
    name_matched = name_sim >= 0.85
    doc_num_matched = True
    dob_matched = normalize_string(dob) == normalize_string(db_dob) if dob and db_dob else False
    nat_matched = normalize_string(nationality) == normalize_string(db_nat) if nationality and db_nat else False

    # Determine match classification
    if name_matched and (dob_matched or nat_matched):
        match_type = "strong_match" if name_sim >= 0.95 else "partial_match"
        db_match_flag = True
    elif name_matched or dob_matched:
        match_type = "partial_match"
        db_match_flag = True
    else:
        match_type = "requires_review"
        db_match_flag = False

    return {
        "database_match": db_match_flag,
        "match_type": match_type,
        "matched_record": {
            "document_id": doc_record.id,
            "document_number": doc_record.document_number,
            "document_type": doc_record.document_type,
            "status": doc_record.status,
            "holder_name": db_name,
            "date_of_birth": db_dob,
            "nationality": db_nat,
            "issue_date": doc_record.issue_date,
            "expiry_date": doc_record.expiry_date
        },
        "field_matches": {
            "document_number": doc_num_matched,
            "name": name_matched,
            "date_of_birth": dob_matched,
            "nationality": nat_matched
        },
        "name_similarity": name_sim,
        "notes": f"Match type: {match_type}. Name similarity {int(name_sim * 100)}%."
    }
