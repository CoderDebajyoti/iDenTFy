"""
DigiLocker Government Verification Provider Adapter
Stub adapter for DigiLocker document verification API.
STRICT RULE:
If credentials/OAuth tokens are not configured, returns status: "NOT_CONNECTED"
and message: "Government verification provider is not configured."
Never generates synthetic or fake responses.
"""

import os
from typing import Dict, Any, Optional
from .base_provider import GovernmentVerificationProvider

class DigiLockerProvider(GovernmentVerificationProvider):
    """
    Adapter for official DigiLocker document verification endpoints.
    Requires official DIGILOCKER_CLIENT_ID and DIGILOCKER_CLIENT_SECRET.
    """

    def __init__(self):
        self._client_id = os.environ.get("DIGILOCKER_CLIENT_ID")
        self._client_secret = os.environ.get("DIGILOCKER_CLIENT_SECRET")

    @property
    def provider_id(self) -> str:
        return "digilocker"

    @property
    def provider_name(self) -> str:
        return "DigiLocker Verification Gateway"

    @property
    def is_synthetic(self) -> bool:
        return False

    def is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    def get_provider_status(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "provider_id": self.provider_id,
                "name": self.provider_name,
                "status": "NOT_CONNECTED",
                "is_synthetic": False,
                "message": "Government verification provider is not configured."
            }
        return {
            "provider_id": self.provider_id,
            "name": self.provider_name,
            "status": "CONFIGURED",
            "is_synthetic": False,
            "message": "DigiLocker credentials configured."
        }

    def verify_document(self, document_number: str, document_type: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "registry_match": False,
                "status": "NOT_CONNECTED",
                "message": "Government verification provider is not configured.",
                "is_synthetic": False
            }
        raise NotImplementedError("DigiLocker integration requires user consent redirect and authorized token.")

    def verify_identity(self, extracted_fields: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "registry_match": False,
                "status": "NOT_CONNECTED",
                "message": "Government verification provider is not configured.",
                "is_synthetic": False,
                "provider_info": self.get_provider_status()
            }
        raise NotImplementedError("DigiLocker integration requires user consent redirect and authorized token.")

    def get_document_record(self, document_number: str) -> Optional[Dict[str, Any]]:
        return None
