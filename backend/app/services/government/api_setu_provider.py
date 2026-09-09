"""
API Setu Government Verification Provider Adapter
Stub adapter for India's API Setu (National API Gateway).
STRICT RULE:
If credentials/certificates are not configured, returns status: "NOT_CONNECTED"
and message: "Government verification provider is not configured."
Never generates synthetic or fake responses.
"""

import os
from typing import Dict, Any, Optional
from .base_provider import GovernmentVerificationProvider

class ApiSetuProvider(GovernmentVerificationProvider):
    """
    Adapter for official API Setu document verification endpoints.
    Requires official API_SETU_CLIENT_ID and API_SETU_API_KEY environment variables.
    """

    def __init__(self):
        self._client_id = os.environ.get("API_SETU_CLIENT_ID")
        self._api_key = os.environ.get("API_SETU_API_KEY")

    @property
    def provider_id(self) -> str:
        return "api_setu"

    @property
    def provider_name(self) -> str:
        return "API Setu (National API Gateway of India)"

    @property
    def is_synthetic(self) -> bool:
        return False

    def is_configured(self) -> bool:
        return bool(self._client_id and self._api_key)

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
            "message": "API Setu credentials present. Awaiting production certificate handshake."
        }

    def verify_document(self, document_number: str, document_type: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "registry_match": False,
                "status": "NOT_CONNECTED",
                "message": "Government verification provider is not configured.",
                "is_synthetic": False
            }
        # In production: make authenticated mutual TLS call to API Setu
        raise NotImplementedError("Production API Setu TLS gateway is pending authorized certificate provisioning.")

    def verify_identity(self, extracted_fields: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "registry_match": False,
                "status": "NOT_CONNECTED",
                "message": "Government verification provider is not configured.",
                "is_synthetic": False,
                "provider_info": self.get_provider_status()
            }
        raise NotImplementedError("Production API Setu TLS gateway is pending authorized certificate provisioning.")

    def get_document_record(self, document_number: str) -> Optional[Dict[str, Any]]:
        return None
