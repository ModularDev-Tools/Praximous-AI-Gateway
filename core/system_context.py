# core/system_context.py
import os
import re
import yaml
from typing import Optional, Dict, Any
from core.logger import log

IDENTITY_CONFIG_PATH = os.path.join('config', 'identity.yaml')

class SystemContext:
    """
    Loads and provides access to the system's identity configuration
    from identity.yaml.
    """
    def __init__(self):
        self._identity_data: Dict[str, Any] = {}
        self._load_context()

    def _load_context(self):
        if not os.path.exists(IDENTITY_CONFIG_PATH):
            # This case should ideally be caught by main.py before server start
            # for server operations. For CLI tools or tests, this might be relevant.
            log.warning(f"Identity configuration file not found at '{IDENTITY_CONFIG_PATH}'. System context will be empty.")
            log.warning("Run 'python main.py --init' to create it.")
            return

        try:
            with open(IDENTITY_CONFIG_PATH, 'r') as f:
                self._identity_data = yaml.safe_load(f) or {}
            log.info(f"System context loaded successfully from '{IDENTITY_CONFIG_PATH}'. Display Name: {self.display_name}")
        except Exception as e:
            log.error(f"Failed to load or parse identity configuration from '{IDENTITY_CONFIG_PATH}': {e}", exc_info=True)
            self._identity_data = {} # Ensure it's an empty dict on error

    @property
    def system_name(self) -> Optional[str]:
        return self._identity_data.get('system_name', 'Praximous-Unconfigured')

    @property
    def business_name(self) -> Optional[str]:
        return self._identity_data.get('business_name')

    @property
    def industry(self) -> Optional[str]:
        return self._identity_data.get('industry')

    @property
    def persona_style(self) -> Optional[str]:
        return self._identity_data.get('persona_style')

    @property
    def sensitivity_level(self) -> Optional[str]:
        return self._identity_data.get('sensitivity_level')

    @property
    def location(self) -> Optional[str]:
        return self._identity_data.get('location')

    def _slugify_business_name(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        # Remove common suffixes like Inc, Ltd, Corp, LLC
        name_no_suffix = re.sub(r'(?i)\s+(Inc\.?|Ltd\.?|Corp\.?|LLC\.?)$', '', name.strip())
        # Keep only alphanumeric characters
        slug = re.sub(r'[^a-zA-Z0-9]', '', name_no_suffix)
        return slug if slug else None

    @property
    def display_name(self) -> str:
        s_name = self._identity_data.get('system_name', 'Praximous-Unconfigured')
        b_name_orig = self._identity_data.get('business_name')

        # If system_name already contains a hyphen (e.g., "Praximous-Acme")
        # or if business_name is not provided, use system_name as is.
        if '-' in s_name or not b_name_orig:
            return s_name

        b_name_slug = self._slugify_business_name(b_name_orig)
        if b_name_slug:
            return f"{s_name}-{b_name_slug}"
        return s_name # Fallback to system_name if slug is empty or business_name was empty

    def get_all_context(self) -> Dict[str, Any]:
        return self._identity_data.copy()

# Global instance, loaded when this module is imported.
system_context = SystemContext()