import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from database.base import Base
from database.models.person import Person
from database.models.document import Document, DocumentStatus
from database.models.passport import Passport
from database.models.visa import Visa
from database.models.verification_record import VerificationRecord

# Use SQLite memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_person_creation(db_session):
    person = Person(
        full_name="TEST USER",
        date_of_birth=date(1990, 1, 1),
        nationality="USA"
    )
    db_session.add(person)
    db_session.commit()
    
    retrieved = db_session.query(Person).filter_by(full_name="TEST USER").first()
    assert retrieved is not None
    assert retrieved.nationality == "USA"
    assert retrieved.id is not None

def test_document_creation(db_session):
    person = Person(
        full_name="DOC USER",
        date_of_birth=date(1995, 5, 5),
        nationality="GBR"
    )
    db_session.add(person)
    db_session.flush()
    
    doc = Document(
        person_id=person.id,
        document_type="identity_card",
        document_number="ID987654321",
        issuing_country="GBR",
        status=DocumentStatus.ACTIVE
    )
    db_session.add(doc)
    db_session.commit()
    
    retrieved_doc = db_session.query(Document).filter_by(document_number="ID987654321").first()
    assert retrieved_doc is not None
    assert retrieved_doc.person.full_name == "DOC USER"
    assert retrieved_doc.status == DocumentStatus.ACTIVE

def test_passport_creation(db_session):
    person = Person(
        full_name="PASS USER",
        date_of_birth=date(2000, 10, 10),
        nationality="CAN"
    )
    db_session.add(person)
    db_session.flush()
    
    doc = Document(
        person_id=person.id,
        document_type="passport",
        document_number="CANPASS123",
        issuing_country="CAN",
        status=DocumentStatus.ACTIVE
    )
    db_session.add(doc)
    db_session.flush()
    
    passport = Passport(
        document_id=doc.id,
        passport_number="CANPASS123",
        nationality="CAN",
        date_of_birth=date(2000, 10, 10)
    )
    db_session.add(passport)
    db_session.commit()
    
    retrieved_pass = db_session.query(Passport).filter_by(passport_number="CANPASS123").first()
    assert retrieved_pass is not None
    assert retrieved_pass.document.person.full_name == "PASS USER"

def test_visa_creation(db_session):
    person = Person(
        full_name="VISA USER",
        date_of_birth=date(1985, 12, 12),
        nationality="IND"
    )
    db_session.add(person)
    db_session.flush()
    
    doc = Document(
        person_id=person.id,
        document_type="visa",
        document_number="V123456",
        issuing_country="USA",
        status=DocumentStatus.ACTIVE
    )
    db_session.add(doc)
    db_session.flush()
    
    visa = Visa(
        document_id=doc.id,
        visa_number="V123456",
        issuing_country="USA",
        stay_duration_days=180
    )
    db_session.add(visa)
    db_session.commit()
    
    retrieved_visa = db_session.query(Visa).filter_by(visa_number="V123456").first()
    assert retrieved_visa is not None
    assert retrieved_visa.stay_duration_days == 180

def test_verification_record(db_session):
    record = VerificationRecord(
        verification_status="PENDING"
    )
    db_session.add(record)
    db_session.commit()
    
    retrieved = db_session.query(VerificationRecord).first()
    assert retrieved is not None
    assert retrieved.verification_status == "PENDING"
