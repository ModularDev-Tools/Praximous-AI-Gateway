# tests/test_licensing_phase4_6.py
import pytest
import os
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import importlib # For reloading modules
import httpx # For API endpoint testing

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

import core
from core.license import (
    _cached_license_info, _cached_public_key, # For clearing cache
    load_public_key as original_load_public_key_func, # Keep a reference to the original
    verify_license_key,
    get_active_license_info,
    LicenseInfo
)
from core.license_generator import create_signed_license_payload
from core.license_manager import (
    get_current_license_tier,
    is_feature_enabled,
    Feature,
    LicenseTier
)
from core.enums import LicenseTier as CoreLicenseTierEnum # For direct comparison
import base64 # For test_verify_license_key_invalid_signature

# Mark all tests in this module to use asyncio if they use async_client
pytestmark = pytest.mark.anyio

@pytest.fixture(scope="session")
def test_rsa_key_pair():
    """Generates an RSA key pair for testing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

@pytest.fixture(scope="session")
def test_private_key(test_rsa_key_pair):
    return test_rsa_key_pair[0]

@pytest.fixture(scope="session")
def test_public_key(test_rsa_key_pair):
    return test_rsa_key_pair[1]

@pytest.fixture(scope="session")
def test_public_key_pem(test_public_key):
    """Returns the PEM representation of the test public key."""
    return test_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

@pytest.fixture
def temp_public_key_file(tmp_path, test_public_key_pem):
    """Creates a temporary public key file and returns its path."""
    key_file = tmp_path / "test_public.pem"
    key_file.write_bytes(test_public_key_pem)
    return str(key_file)


def create_test_license_str(private_key, customer_name, tier_enum: CoreLicenseTierEnum, validity_days) -> str:
    """Helper to create a signed license string for testing."""
    return create_signed_license_payload(customer_name, tier_enum.value, validity_days, private_key)

# --- Tests for core.license.py ---

def test_load_public_key_success(temp_public_key_file, test_public_key):
    loaded_key = original_load_public_key_func(temp_public_key_file)
    assert loaded_key is not None
    # Compare key numbers for equality (a bit more involved for RSA keys)
    assert loaded_key.public_numbers() == test_public_key.public_numbers()

def test_load_public_key_not_found(tmp_path):
    non_existent_key_file = tmp_path / "not_found.pem"
    loaded_key = original_load_public_key_func(str(non_existent_key_file))
    assert loaded_key is None

def test_verify_license_key_valid(test_private_key, test_public_key):
    license_str = create_test_license_str(test_private_key, "Test Customer", CoreLicenseTierEnum.ENTERPRISE, 30)
    license_info = verify_license_key(license_str, test_public_key)
    assert license_info is not None
    assert license_info.customer_name == "Test Customer"
    assert license_info.tier == CoreLicenseTierEnum.ENTERPRISE
    assert license_info.is_valid
    assert not license_info.is_expired

def test_verify_license_key_expired(test_private_key, test_public_key):
    license_str = create_test_license_str(test_private_key, "Expired Co", CoreLicenseTierEnum.PRO, -5) # Expired 5 days ago
    license_info = verify_license_key(license_str, test_public_key)
    assert license_info is not None
    assert license_info.is_expired
    assert not license_info.is_valid # is_valid should be False if expired

def test_verify_license_key_invalid_signature(test_private_key, test_public_key, test_rsa_key_pair):
    # Create a license with one private key
    license_str = create_test_license_str(test_private_key, "Bad Sig Inc.", CoreLicenseTierEnum.PRO, 30)
    
    # Generate a different public key for verification attempt
    _, other_public_key = test_rsa_key_pair # Re-use fixture to get a new pair if needed, or generate one
    # Ensure it's actually different if the fixture is session scoped and returns same object
    if other_public_key.public_numbers() == test_public_key.public_numbers():
         other_public_key = rsa.generate_private_key( # Fixed: Direct assignment
            public_exponent=65537, key_size=2048, backend=default_backend()
         ).public_key()

    # Tamper with the signature part of the license string
    license_obj = json.loads(license_str)
    # Correctly decode the base64 payload before loading as JSON
    decoded_payload_str = base64.b64decode(license_obj["payload"].encode('utf-8')).decode('utf-8')
    original_payload_bytes = json.dumps(json.loads(decoded_payload_str), sort_keys=True).encode('utf-8')

    # Sign with a different key to make it invalid for test_public_key
    different_private_key, _ = test_rsa_key_pair # Assuming this gives a different key or generate one
    if different_private_key == test_private_key: # Ensure it's different
        different_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    bad_signature = different_private_key.sign(
        original_payload_bytes,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    license_obj["signature"] = base64.b64encode(bad_signature).decode('utf-8')
    tampered_license_str = json.dumps(license_obj)

    license_info = verify_license_key(tampered_license_str, test_public_key)
    assert license_info is None # verify_license_key returns None on InvalidSignature

def test_get_active_license_info_env_var(monkeypatch, test_private_key, test_public_key, temp_public_key_file):
    valid_license_str = create_test_license_str(test_private_key, "Env Customer", CoreLicenseTierEnum.PRO, 30)
    monkeypatch.setenv("PRAXIMOUS_LICENSE_KEY", valid_license_str)

    # Ensure caches are clear before this specific test logic
    core.license._cached_public_key = None
    core.license._cached_license_info = None
        
    # Instead of patching DEFAULT_PUBLIC_KEY_PATH, patch load_public_key to return our test_public_key
    # This ensures get_active_license_info uses the correct key when it calls load_public_key internally.
    with patch("core.license.load_public_key", return_value=test_public_key) as mock_load_pk:
        # No need to reload if patch is applied to the already imported module and caches are clear
        license_info = get_active_license_info() # Call the function from the (potentially already imported) core.license

        mock_load_pk.assert_called_once() # Ensure our mock was used

    assert license_info is not None
    assert license_info.customer_name == "Env Customer"
    assert license_info.tier == CoreLicenseTierEnum.PRO

# --- Tests for core.license_manager.py ---
# Patch get_active_license_info where it's used by get_current_license_tier
@patch("core.license_manager.get_active_license_info")
def test_get_current_license_tier_enterprise(mock_get_active_license):
    mock_get_active_license.return_value = LicenseInfo(
        "Enterprise User", CoreLicenseTierEnum.ENTERPRISE, datetime.now(timezone.utc), 
        datetime.now(timezone.utc) + timedelta(days=30), True, False, {}
    )
    assert get_current_license_tier() == CoreLicenseTierEnum.ENTERPRISE

@patch("core.license_manager.get_active_license_info") # Patch where it's used
def test_get_current_license_tier_community_if_no_license(mock_get_active_license):
    mock_get_active_license.return_value = None
    assert get_current_license_tier() == CoreLicenseTierEnum.COMMUNITY

@patch("core.license_manager.get_active_license_info") # Patch where it's used
def test_get_current_license_tier_community_if_expired(mock_get_active_license):
    mock_get_active_license.return_value = LicenseInfo(
        "Expired User", CoreLicenseTierEnum.PRO, datetime.now(timezone.utc) - timedelta(days=5), 
        datetime.now(timezone.utc) - timedelta(days=2), False, True, {} # is_valid=False, is_expired=True
    )
    assert get_current_license_tier() == CoreLicenseTierEnum.COMMUNITY

@patch("core.license_manager.get_current_license_tier") # This mock is correct for testing is_feature_enabled directly
def test_is_feature_enabled(mock_get_tier):
    # Test Enterprise
    mock_get_tier.return_value = CoreLicenseTierEnum.ENTERPRISE
    assert is_feature_enabled(Feature.RAG_INTERFACE)
    assert is_feature_enabled(Feature.CORE_SKILLS)
    assert is_feature_enabled(Feature.ADVANCED_ANALYTICS_UI)

    # Test Pro
    mock_get_tier.return_value = CoreLicenseTierEnum.PRO
    assert not is_feature_enabled(Feature.RAG_INTERFACE)
    assert is_feature_enabled(Feature.CORE_SKILLS)
    assert is_feature_enabled(Feature.ADVANCED_ANALYTICS_UI)

    # Test Community
    mock_get_tier.return_value = CoreLicenseTierEnum.COMMUNITY
    assert not is_feature_enabled(Feature.RAG_INTERFACE)
    assert is_feature_enabled(Feature.CORE_SKILLS)
    assert not is_feature_enabled(Feature.ADVANCED_ANALYTICS_UI)

# --- Tests for RAG Interface Endpoint Licensing ---

async def test_rag_interface_access_enterprise(async_client: httpx.AsyncClient, valid_api_key_1: str, mocker):
    # Mock get_current_license_tier in core.license_manager, as that's what is_feature_enabled uses
    mocker.patch("core.license_manager.get_current_license_tier", return_value=CoreLicenseTierEnum.ENTERPRISE)
    
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/rag/query?query=test", headers=headers)
    assert response.status_code == 200
    assert "RAG query processed successfully" in response.json()["message"]

async def test_rag_interface_no_access_pro(async_client: httpx.AsyncClient, valid_api_key_1: str, mocker):
    # Mock is_feature_enabled to return False, simulating the feature is not enabled
    mocker.patch("api.v1.endpoints.rag_interface_router.is_feature_enabled", return_value=False)
    # Mock get_current_license_tier for the detail message in the HTTPException
    mocker.patch("api.v1.endpoints.rag_interface_router.get_current_license_tier", return_value=CoreLicenseTierEnum.PRO)
    
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/rag/query?query=test", headers=headers)
    assert response.status_code == 403
    # The detail message comes from verify_rag_access, which calls the mocked get_current_license_tier
    assert "not available for your current license tier (PRO)" in response.json()["detail"]

async def test_rag_interface_no_access_community(async_client: httpx.AsyncClient, valid_api_key_1: str, mocker):
    # Mock is_feature_enabled to return False
    mocker.patch("api.v1.endpoints.rag_interface_router.is_feature_enabled", return_value=False)
    # Mock get_current_license_tier for the detail message
    mocker.patch("api.v1.endpoints.rag_interface_router.get_current_license_tier", return_value=CoreLicenseTierEnum.COMMUNITY)
 
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/rag/query?query=test", headers=headers)
    assert response.status_code == 403
    assert "not available for your current license tier (COMMUNITY)" in response.json()["detail"]


# Helper for reloading core.license if needed after monkeypatching env vars
@pytest.fixture(autouse=True)
def reload_license_module_for_env_tests():
    """
    Ensures that core.license module's cached values are reset if tests modify
    environment variables it depends on (PRAXIMOUS_LICENSE_KEY).
    This is a bit broad; more targeted reloads or cache clearing might be better.
    """
    # This fixture doesn't do anything on its own but can be a placeholder
    # if more complex reload logic is needed.
    # For now, individual tests like test_get_active_license_info_env_var
    # handle their own reloads.
    pass

@pytest.fixture(autouse=True)
def clear_license_caches():
    """Clears cached license information before and after each test in this module."""
    # Access through the imported names for clarity and to avoid direct _module access if possible
    original_cached_public_key_val = _cached_public_key
    original_cached_license_info_val = _cached_license_info
    core.license._cached_public_key = None # Directly reset module-level cache
    core.license._cached_license_info = None # Directly reset module-level cache
    yield
    core.license._cached_public_key = original_cached_public_key_val
    core.license._cached_license_info = original_cached_license_info_val