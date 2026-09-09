"""
Government Verification Provider Manager
Coordinates registration, selection, and routing of government verification providers.
Allows seamless switching between the TestAuthorizedRegistryProvider, ApiSetuProvider,
and DigiLockerProvider without altering the verification pipeline.
"""

import os
from typing import Dict, Any, List, Optional
from .base_provider import GovernmentVerificationProvider
from .test_provider import TestAuthorizedRegistryProvider
from .api_setu_provider import ApiSetuProvider
from .digilocker_provider import DigiLockerProvider

class ProviderManager:
    """
    Registry and lifecycle manager for government verification providers.
    """

    def __init__(self):
        self._providers: Dict[str, GovernmentVerificationProvider] = {}
        # Default registration
        self.register_provider(TestAuthorizedRegistryProvider())
        self.register_provider(ApiSetuProvider())
        self.register_provider(DigiLockerProvider())

        # Select default provider via environment or fallback to test
        self._active_provider_id = os.environ.get("GOVERNMENT_PROVIDER", "test_registry").strip().lower()
        if self._active_provider_id not in self._providers:
            self._active_provider_id = "test_registry"

    def register_provider(self, provider: GovernmentVerificationProvider) -> None:
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: str) -> Optional[GovernmentVerificationProvider]:
        return self._providers.get(provider_id)

    def set_active_provider(self, provider_id: str) -> bool:
        if provider_id in self._providers:
            self._active_provider_id = provider_id
            return True
        return False

    def get_active_provider(self) -> GovernmentVerificationProvider:
        return self._providers.get(self._active_provider_id, self._providers["test_registry"])

    def list_providers(self) -> List[Dict[str, Any]]:
        result = []
        for pid, prov in self._providers.items():
            status_info = prov.get_provider_status()
            status_info["is_active"] = (pid == self._active_provider_id)
            result.append(status_info)
        return result

_provider_manager_instance: Optional[ProviderManager] = None

def get_provider_manager() -> ProviderManager:
    global _provider_manager_instance
    if _provider_manager_instance is None:
        _provider_manager_instance = ProviderManager()
    return _provider_manager_instance
