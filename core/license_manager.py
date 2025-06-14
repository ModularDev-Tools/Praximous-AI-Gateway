# core/license_manager.py
from enum import Enum
from typing import Dict, Set
from core.logger import log
import os # For a temporary mock license tier
from core.license import get_active_license_info # Import the new license verification

class LicenseTier(Enum):
    COMMUNITY = "community" # Or Free/Basic
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Feature(Enum):
    # Core features available to all
    CORE_SKILLS = "core_skills"
    LLM_INTEGRATION = "llm_integration"
    AUDIT_LOGGING = "audit_logging"
    BASIC_ANALYTICS = "basic_analytics"

    # Premium Features
    ADVANCED_ANALYTICS_UI = "advanced_analytics_ui" # From Phase 5
    RAG_INTERFACE = "rag_interface" # Premium feature
    RBAC = "rbac" # Role-Based Access Control - Premium feature
    PII_REDACTION = "pii_redaction" # Premium feature
    # Add other features as needed

# Define which features are available for each tier
# This mapping defines the minimum tier required for a feature.
# A higher tier automatically includes features from lower tiers.
TIER_FEATURES: Dict[LicenseTier, Set[Feature]] = {
    LicenseTier.COMMUNITY: {
        Feature.CORE_SKILLS,
        Feature.LLM_INTEGRATION,
        Feature.AUDIT_LOGGING,
        Feature.BASIC_ANALYTICS, # Assuming the current analytics endpoint is basic
    },
    LicenseTier.PRO: {
        Feature.CORE_SKILLS,
        Feature.LLM_INTEGRATION,
        Feature.AUDIT_LOGGING,
        Feature.BASIC_ANALYTICS,
        Feature.ADVANCED_ANALYTICS_UI, # Example: Pro gets the advanced UI
    },
    LicenseTier.ENTERPRISE: {
        Feature.CORE_SKILLS,
        Feature.LLM_INTEGRATION,
        Feature.AUDIT_LOGGING,
        Feature.BASIC_ANALYTICS,
        Feature.ADVANCED_ANALYTICS_UI,
        Feature.RAG_INTERFACE,
        Feature.RBAC,
        Feature.PII_REDACTION,
    }
}

def get_current_license_tier() -> LicenseTier:
    """
    Retrieves the current license tier.
    This now uses the license verification module.
    """
    active_license = get_active_license_info()

    if active_license and active_license.is_valid and not active_license.is_expired:
        log.info(f"Valid license found for {active_license.customer_name}. Tier: {active_license.tier.name}")
        return active_license.tier
    elif active_license and active_license.is_expired:
        log.warning(f"License for {active_license.customer_name} is EXPIRED. Defaulting to Community tier.")
        return LicenseTier.COMMUNITY
    else: # No license, invalid license, or other error during verification
        log.warning("No valid license found or license verification failed. Defaulting to Community tier.")
        return LicenseTier.COMMUNITY

def is_feature_enabled(feature: Feature) -> bool:
    """Checks if a given feature is enabled for the current license tier."""
    current_tier = get_current_license_tier()
    # A feature is enabled if it's in the set of features for the current tier.
    # This simple check assumes enterprise includes all pro features, etc.
    # If tiers are not strictly hierarchical, this logic would need adjustment.
    enabled = feature in TIER_FEATURES.get(current_tier, set())
    log.debug(f"Feature check: '{feature.name}' for tier '{current_tier.name}'. Enabled: {enabled}")
    return enabled