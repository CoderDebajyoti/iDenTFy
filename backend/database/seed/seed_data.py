import os
import sys
from datetime import date
from dotenv import load_dotenv

# Add backend directory to sys.path to resolve 'database' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.connection import SessionLocal
from database.models.person import Person
from database.models.document import Document, DocumentStatus
from database.models.passport import Passport
from database.models.visa import Visa

def seed_database():
    print("Starting database seeding...")
    db = SessionLocal()
    
    try:
        # Check if database is already seeded
        if db.query(Person).count() > 0:
            print("Database already contains data. Skipping seeding.")
            return

        print("Inserting synthetic test data...")
        
        # 1. Exact Match Case
        person1 = Person(
            full_name="DEBOJYOTI DAS",
            date_of_birth=date(2000, 5, 10),
            nationality="IND",
            gender="M"
        )
        db.add(person1)
        db.flush()

        doc1 = Document(
            person_id=person1.id,
            document_type="passport",
            document_number="TESTP123456",
            issuing_country="IND",
            issue_date=date(2020, 1, 1),
            expiry_date=date(2030, 1, 1),
            status=DocumentStatus.ACTIVE
        )
        db.add(doc1)
        db.flush()

        pass1 = Passport(
            document_id=doc1.id,
            passport_number="TESTP123456",
            nationality="IND",
            date_of_birth=date(2000, 5, 10),
            gender="M",
            date_of_issue=date(2020, 1, 1),
            date_of_expiry=date(2030, 1, 1),
            mrz_line_1="P<INDDAS<<DEBOJYOTI<<<<<<<<<<<<<<<<<<<<<<<<",
            mrz_line_2="TESTP123456IND0005104M3001014<<<<<<<<<<<<<<0"
        )
        db.add(pass1)

        # 2. Minor Spelling Variation (different person but similar name, or just another doc for same person)
        person2 = Person(
            full_name="DEBAJYOTI DAS",
            date_of_birth=date(2000, 5, 10),
            nationality="IND",
            gender="M"
        )
        db.add(person2)
        db.flush()
        
        doc2 = Document(
            person_id=person2.id,
            document_type="identity_card",
            document_number="ID123456789",
            issuing_country="IND",
            status=DocumentStatus.ACTIVE
        )
        db.add(doc2)

        # 3. Different Person
        person3 = Person(
            full_name="RAHUL KUMAR",
            date_of_birth=date(1995, 8, 15),
            nationality="IND",
            gender="M"
        )
        db.add(person3)
        db.flush()
        
        doc3 = Document(
            person_id=person3.id,
            document_type="passport",
            document_number="PASS9876543",
            issuing_country="IND",
            issue_date=date(2018, 5, 10),
            expiry_date=date(2028, 5, 10),
            status=DocumentStatus.ACTIVE
        )
        db.add(doc3)
        db.flush()
        
        pass3 = Passport(
            document_id=doc3.id,
            passport_number="PASS9876543",
            nationality="IND",
            date_of_birth=date(1995, 8, 15)
        )
        db.add(pass3)

        # 4. Expired Document
        person4 = Person(
            full_name="ALICE SMITH",
            date_of_birth=date(1980, 2, 20),
            nationality="USA",
            gender="F"
        )
        db.add(person4)
        db.flush()
        
        doc4 = Document(
            person_id=person4.id,
            document_type="passport",
            document_number="EXPIRED123",
            issuing_country="USA",
            expiry_date=date(2022, 1, 1),
            status=DocumentStatus.EXPIRED
        )
        db.add(doc4)
        db.flush()
        
        pass4 = Passport(
            document_id=doc4.id,
            passport_number="EXPIRED123",
            nationality="USA",
            date_of_birth=date(1980, 2, 20)
        )
        db.add(pass4)

        # 5. Blacklisted Document
        person5 = Person(
            full_name="JOHN DOE",
            date_of_birth=date(1990, 11, 11),
            nationality="GBR",
            gender="M"
        )
        db.add(person5)
        db.flush()

        doc5 = Document(
            person_id=person5.id,
            document_type="residence_permit",
            document_number="BLACKLIST999",
            issuing_country="GBR",
            status=DocumentStatus.BLACKLISTED
        )
        db.add(doc5)

        # 6. Visa Example
        doc6 = Document(
            person_id=person1.id, # Visa for Debojyoti Das
            document_type="visa",
            document_number="VISA555666",
            issuing_country="CAN",
            issue_date=date(2024, 1, 1),
            expiry_date=date(2025, 1, 1),
            status=DocumentStatus.ACTIVE
        )
        db.add(doc6)
        db.flush()

        visa1 = Visa(
            document_id=doc6.id,
            visa_number="VISA555666",
            visa_type="Tourist",
            issuing_country="CAN",
            entry_type="Multiple",
            valid_from=date(2024, 1, 1),
            valid_until=date(2025, 1, 1),
            stay_duration_days=90,
            status="Valid"
        )
        db.add(visa1)

        db.commit()
        print("Successfully seeded synthetic data!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
