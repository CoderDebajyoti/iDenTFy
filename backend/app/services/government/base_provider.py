"""
Government Verification Provider Base Abstraction
Defines the contract for external government registries and test adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class GovernmentVerificationProvider(ABC):
    """
    Abstract interface for all government document and identity registry providers.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier for this provider (e.g. 'test_registry', 'api_setu', 'digilocker')."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name."""
        pass

    @property
    @abstractmethod
    def is_synthetic(self) -> bool:
        """True if provider uses synthetic/test records; False for live government registries."""
        pass

    @abstractmethod
    def get_provider_status(self) -> Dict[str, Any]:
        """
        Return the provider connectivity and operational status.
        Structure:
        {
            "provider_id": str,
            "name": str,
            "status": "ACTIVE" | "NOT_CONNECTED" | "UNAVAILABLE",
            "is_synthetic": bool,
            "message": str
        }
        """
        pass

    @abstractmethod
    def verify_document(self, document_number: str, document_type: str) -> Dict[str, Any]:
        """
        Query provider for document registry record by document number and type.
        """
        pass

    @abstractmethod
    def verify_identity(self, extracted_fields: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """
        Match extracted document fields against registry records.
        """
        pass

    @abstractmethod
    def get_document_record(self, document_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve raw authorized registry entry if available.
        """
        pass
