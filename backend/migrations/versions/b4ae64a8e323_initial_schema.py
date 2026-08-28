"""Initial schema

Revision ID: b4ae64a8e323
Revises: 
Create Date: 2026-08-28 10:56:56.852506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b4ae64a8e323'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create person table
    op.create_table(
        'persons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('nationality', sa.String(), nullable=False),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_persons_date_of_birth'), 'persons', ['date_of_birth'], unique=False)
    op.create_index(op.f('ix_persons_full_name'), 'persons', ['full_name'], unique=False)
    op.create_index(op.f('ix_persons_nationality'), 'persons', ['nationality'], unique=False)

    # Create document status enum type
    document_status_enum = postgresql.ENUM('ACTIVE', 'EXPIRED', 'REVOKED', 'BLACKLISTED', 'SUSPENDED', name='documentstatus')
    document_status_enum.create(op.get_bind())

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_type', sa.String(), nullable=False),
        sa.Column('document_number', sa.String(), nullable=False),
        sa.Column('issuing_country', sa.String(), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'EXPIRED', 'REVOKED', 'BLACKLISTED', 'SUSPENDED', name='documentstatus', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_document_number'), 'documents', ['document_number'], unique=True)
    op.create_index(op.f('ix_documents_document_type'), 'documents', ['document_type'], unique=False)
    op.create_index(op.f('ix_documents_status'), 'documents', ['status'], unique=False)

    # Create passports table
    op.create_table(
        'passports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('passport_number', sa.String(), nullable=False),
        sa.Column('nationality', sa.String(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('date_of_issue', sa.Date(), nullable=True),
        sa.Column('date_of_expiry', sa.Date(), nullable=True),
        sa.Column('mrz_line_1', sa.String(), nullable=True),
        sa.Column('mrz_line_2', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )
    op.create_index(op.f('ix_passports_passport_number'), 'passports', ['passport_number'], unique=True)

    # Create visas table
    op.create_table(
        'visas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('visa_number', sa.String(), nullable=False),
        sa.Column('visa_type', sa.String(), nullable=True),
        sa.Column('issuing_country', sa.String(), nullable=False),
        sa.Column('entry_type', sa.String(), nullable=True),
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('stay_duration_days', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visas_visa_number'), 'visas', ['visa_number'], unique=True)

    # Create verification_records table
    op.create_table(
        'verification_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verification_status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('verification_records')
    op.drop_index(op.f('ix_visas_visa_number'), table_name='visas')
    op.drop_table('visas')
    op.drop_index(op.f('ix_passports_passport_number'), table_name='passports')
    op.drop_table('passports')
    op.drop_index(op.f('ix_documents_status'), table_name='documents')
    op.drop_index(op.f('ix_documents_document_type'), table_name='documents')
    op.drop_index(op.f('ix_documents_document_number'), table_name='documents')
    op.drop_table('documents')
    
    document_status_enum = postgresql.ENUM('ACTIVE', 'EXPIRED', 'REVOKED', 'BLACKLISTED', 'SUSPENDED', name='documentstatus')
    document_status_enum.drop(op.get_bind())

    op.drop_index(op.f('ix_persons_nationality'), table_name='persons')
    op.drop_index(op.f('ix_persons_full_name'), table_name='persons')
    op.drop_index(op.f('ix_persons_date_of_birth'), table_name='persons')
    op.drop_table('persons')
