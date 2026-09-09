"""
Government Verification Provider Architecture Package
"""

from .base_provider import GovernmentVerificationProvider
from .test_provider import TestAuthorizedRegistryProvider
from .api_setu_provider import ApiSetuProvider
from .digilocker_provider import DigiLockerProvider
from .provider_manager import ProviderManager, get_provider_manager

__all__ = [
    "GovernmentVerificationProvider",
    "TestAuthorizedRegistryProvider",
    "ApiSetuProvider",
    "DigiLockerProvider",
    "ProviderManager",
    "get_provider_manager"
]
