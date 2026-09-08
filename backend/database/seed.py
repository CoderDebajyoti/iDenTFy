"""
Synthetic Database Seed Generator for iDenTFy
Strictly uses fictional/synthetic names, dates, and numbers.
Covers all 10 evaluation test cases:
1. Exact document match
2. Name spelling variation
3. Wrong document number
4. Different person
5. Expired document
6. Blacklisted document
7. Suspended document
8. Valid passport
9. Valid identity card
10. Multiple documents belonging to one person
"""

import sys
import os
# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)

from database.database import engine, SessionLocal, Base
from database.models import Person, Document, Passport, Visa, VerificationRecord
from datetime import datetime

def seed_database():
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Person).count() > 0:
            print("Database already contains records. Clearing existing synthetic records for clean re-seed...")
            db.query(VerificationRecord).delete()
            db.query(Visa).delete()
            db.query(Passport).delete()
            db.query(Document).delete()
            db.query(Person).delete()
            db.commit()

        # ======================================================================
        # 1. PERSON 1: Synthetic Valid Indian Subject (Aarav Sharma)
        # Test Cases: Exact match, Valid Passport (Case 1 & 8)
        # ======================================================================
        p1 = Person(
            id="p-syn-001",
            full_name="Aarav Sharma",
            date_of_birth="1995-08-15",
            nationality="IND",
            gender="M"
        )
        d1 = Document(
            id="doc-syn-001",
            person_id=p1.id,
            document_type="passport",
            document_number="Z6549210",
            issuing_country="IND",
            issue_date="2020-08-15",
            expiry_date="2030-08-14",
            status="active"
        )
        pass1 = Passport(
            id="pass-syn-001",
            document_id=d1.id,
            passport_number="Z6549210",
            nationality="IND",
            date_of_birth="1995-08-15",
            gender="M",
            issue_date="2020-08-15",
            expiry_date="2030-08-14",
            mrz_line_1="P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<",
            mrz_line_2="Z6549210<2IND9508152M3008144<<<<<<<<<<<<<<08"
        )

        # ======================================================================
        # 2. PERSON 2: Synthetic Subject for Name Variation (Priya Patel)
        # Test Cases: Name spelling variation (Priya Patel vs Priyaa Patel), Case 2 & 9
        # ======================================================================
        p2 = Person(
            id="p-syn-002",
            full_name="Priya Patel",
            date_of_birth="1991-11-23",
            nationality="IND",
            gender="F"
        )
        d2 = Document(
            id="doc-syn-002",
            person_id=p2.id,
            document_type="identity_card",
            document_number="ID5502914",
            issuing_country="IND",
            issue_date="2019-02-15",
            expiry_date="2029-02-14",
            status="active"
        )

        # ======================================================================
        # 3. PERSON 3: Synthetic Expired Document (Rajesh Verma)
        # Test Cases: Expired document check (Case 5)
        # ======================================================================
        p3 = Person(
            id="p-syn-003",
            full_name="Rajesh Verma",
            date_of_birth="1980-05-12",
            nationality="IND",
            gender="M"
        )
        d3 = Document(
            id="doc-syn-003",
            person_id=p3.id,
            document_type="passport",
            document_number="Z1102945",
            issuing_country="IND",
            issue_date="2012-01-10",
            expiry_date="2022-01-09", # Expired in past
            status="expired"
        )
        pass3 = Passport(
            id="pass-syn-003",
            document_id=d3.id,
            passport_number="Z1102945",
            nationality="IND",
            date_of_birth="1980-05-12",
            gender="M",
            issue_date="2012-01-10",
            expiry_date="2022-01-09",
            mrz_line_1="P<INDVERMA<<RAJESH<<<<<<<<<<<<<<<<<<<<<<<<<<",
            mrz_line_2="Z11029455IND8005124M2201091<<<<<<<<<<<<<<06"
        )

        # ======================================================================
        # 4. PERSON 4: Synthetic Blacklisted Document / Stolen (Vikram Singh)
        # Test Cases: Blacklisted document check (Case 6)
        # ======================================================================
        p4 = Person(
            id="p-syn-004",
            full_name="Vikram Singh",
            date_of_birth="1985-08-30",
            nationality="IND",
            gender="M"
        )
        d4 = Document(
            id="doc-syn-004",
            person_id=p4.id,
            document_type="driver_license",
            document_number="DL04202300789",
            issuing_country="IND",
            issue_date="2021-01-12",
            expiry_date="2031-01-11",
            status="blacklisted" # Stolen / Fraud Alert
        )

        # ======================================================================
        # 5. PERSON 5: Synthetic Suspended Document (Ananya Sen)
        # Test Cases: Suspended document check (Case 7)
        # ======================================================================
        p5 = Person(
            id="p-syn-005",
            full_name="Ananya Sen",
            date_of_birth="1989-03-21",
            nationality="IND",
            gender="F"
        )
        d5 = Document(
            id="doc-syn-005",
            person_id=p5.id,
            document_type="identity_card",
            document_number="ID4401829",
            issuing_country="IND",
            issue_date="2020-08-11",
            expiry_date="2028-08-10",
            status="suspended" # Suspended pending investigation
        )

        # ======================================================================
        # 6. PERSON 6: Multiple Documents Belonging to One Person (Rohan Mehta)
        # Test Cases: Multiple documents (Passport + Driver License), Case 10
        # ======================================================================
        p6 = Person(
            id="p-syn-006",
            full_name="Rohan Mehta",
            date_of_birth="1994-12-05",
            nationality="IND",
            gender="M"
        )
        d6_a = Document(
            id="doc-syn-006-a",
            person_id=p6.id,
            document_type="passport",
            document_number="Z6630192",
            issuing_country="IND",
            issue_date="2021-09-01",
            expiry_date="2031-08-31",
            status="active"
        )
        pass6 = Passport(
            id="pass-syn-006",
            document_id=d6_a.id,
            passport_number="Z6630192",
            nationality="IND",
            date_of_birth="1994-12-05",
            gender="M",
            issue_date="2021-09-01",
            expiry_date="2031-08-31",
            mrz_line_1="P<INDMEHTA<<ROHAN<<<<<<<<<<<<<<<<<<<<<<<<<<<",
            mrz_line_2="Z66301924IND9412053M3108318<<<<<<<<<<<<<<04"
        )
        d6_b = Document(
            id="doc-syn-006-b",
            person_id=p6.id,
            document_type="driver_license",
            document_number="DL07202201098",
            issuing_country="IND",
            issue_date="2022-04-18",
            expiry_date="2032-04-17",
            status="active"
        )

        # ======================================================================
        # 7. PERSON 7: Foreign Arrival Exception (David K. Miller)
        # Supporting international traveler entering India on Indian e-Visa
        # ======================================================================
        p7 = Person(
            id="p-syn-007",
            full_name="David K. Miller",
            date_of_birth="1986-04-18",
            nationality="GBR",
            gender="M"
        )
        d7 = Document(
            id="doc-syn-007",
            person_id=p7.id,
            document_type="passport",
            document_number="PA4401829",
            issuing_country="GBR",
            issue_date="2021-08-11",
            expiry_date="2031-08-10",
            status="active"
        )
        pass7 = Passport(
            id="pass-syn-007",
            document_id=d7.id,
            passport_number="PA4401829",
            nationality="GBR",
            date_of_birth="1986-04-18",
            gender="M",
            issue_date="2021-08-11",
            expiry_date="2031-08-10",
            mrz_line_1="P<GBRMILLER<<DAVID<K<<<<<<<<<<<<<<<<<<<<<<<<",
            mrz_line_2="PA44018293GBR8604182M3108106<<<<<<<<<<<<<<08"
        )
        v_ind_7 = Visa(
            id="visa-syn-007",
            document_id=d7.id,
            visa_number="V-IND-2026-98124",
            visa_type="tourist",
            issuing_country="IND",
            entry_type="multiple",
            valid_from="2026-04-18",
            valid_until="2027-04-18",
            stay_duration_days=90,
            status="valid"
        )

        # Add reference registry entities to session (zero verification records)
        db.add_all([
            p1, d1, pass1,
            p2, d2,
            p3, d3, pass3,
            p4, d4,
            p5, d5,
            p6, d6_a, pass6, d6_b,
            p7, d7, pass7, v_ind_7
        ])

        db.commit()
        print("Successfully seeded registry test entities (0 verification records created).")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
