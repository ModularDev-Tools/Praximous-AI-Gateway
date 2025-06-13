# config/credentials_manager.py
import os
import re
import sys # Added for sys.path manipulation
import yaml

# Add the project root to the Python path to allow for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.logger import log

# Define paths relative to the project root for robustness
PROJECT_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_DIR_ABS = os.path.join(PROJECT_ROOT_DIR, 'config') # Absolute path to config dir
ENV_PATH = os.path.join(PROJECT_ROOT_DIR, '.env') # For monkeypatching in tests
PROVIDERS_CONFIG_PATH = os.path.join(CONFIG_DIR_ABS, 'providers.yaml')

def _extract_env_vars_from_string(s: str) -> set[str]:
    """Extracts environment variable names like ${VAR_NAME} from a string."""
    if not isinstance(s, str):
        return set()
    return set(re.findall(r'\$\{(\w+)\}', s))

def _find_env_vars_in_config(data: any) -> set[str]:
    """Recursively finds all environment variable placeholders in the providers config."""
    found_vars = set()
    if isinstance(data, dict):
        for k, v in data.items():
            found_vars.update(_extract_env_vars_from_string(v))
            found_vars.update(_find_env_vars_in_config(v))
    elif isinstance(data, list):
        for item in data:
            found_vars.update(_extract_env_vars_from_string(item))
            found_vars.update(_find_env_vars_in_config(item))
    elif isinstance(data, str):
        found_vars.update(_extract_env_vars_from_string(data))
    return found_vars

def setup_api_credentials():
    """
    Prompts the user for API keys and stores them in the .env file.
    Preserves existing variables in the .env file.
    """
    log.info("Managing API credentials / environment variables for .env file.")
    
    env_vars = {}
    # Read existing .env file if it exists, to preserve other variables
    if os.path.exists(ENV_PATH): # Use the defined constant
        with open(ENV_PATH, 'r') as f: # Use the defined constant
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Load providers.yaml to identify required environment variables
    provider_env_vars_to_prompt = {} # Store var_name: prompt_text
    if os.path.exists(PROVIDERS_CONFIG_PATH):
        try:
            with open(PROVIDERS_CONFIG_PATH, 'r') as f:
                providers_config = yaml.safe_load(f)
            if providers_config and "providers" in providers_config:
                for provider_info in providers_config["providers"]:
                    if isinstance(provider_info, dict) and "env_var" in provider_info:
                        var_name = provider_info["env_var"]
                        prompt_text = provider_info.get("prompt_text", f"API credential for {provider_info.get('name', var_name)}")
                        provider_env_vars_to_prompt[var_name] = prompt_text
                if provider_env_vars_to_prompt:
                    log.info(f"Identified provider environment variables from '{PROVIDERS_CONFIG_PATH}': {', '.join(provider_env_vars_to_prompt.keys())}")
        except Exception as e:
            log.error(f"Could not load or parse '{PROVIDERS_CONFIG_PATH}': {e}. API key prompts might be incomplete.")
    else:
        log.warning(f"'{PROVIDERS_CONFIG_PATH}' not found. API key prompts based on providers will be skipped.")

    # Prompt for keys found in providers.yaml
    # Iterate over the keys identified directly from the 'env_var' fields in providers.yaml
    for var_name in sorted(list(provider_env_vars_to_prompt.keys())):
        current_value = env_vars.get(var_name)
        prompt_message = f"Enter value for {var_name}"
        # Use the prompt_text from providers.yaml if available
        prompt_text_from_config = provider_env_vars_to_prompt.get(var_name, f"Enter value for {var_name}")
        prompt_message = f"{prompt_text_from_config}"

        # Special handling for OLLAMA_API_URL default
        if var_name == "OLLAMA_API_URL" and not current_value:
            default_val = "http://localhost:11434"
            prompt_message += f" (or press Enter for default: '{default_val}')"
            user_input = input(prompt_message + ": ").strip()
            env_vars[var_name] = user_input if user_input else default_val
        elif current_value:
            display_value = current_value[:3] + '...' + current_value[-3:] if len(current_value) > 6 else current_value
            prompt_message += f" (current: '{display_value}', leave blank to keep)"
            user_input = input(prompt_message + ": ").strip()
            if user_input: # Update only if user provides new input
                env_vars[var_name] = user_input
        else: # New variable not in .env yet
            env_vars[var_name] = input(prompt_message + ": ").strip()

    # Loop for other dynamic environment variables
    log.info("You can now add or update any other environment variables.")
    while True:
        if env_vars:
            log.info("Current environment variables to be saved:")
            for k, v_display in env_vars.items():
                display_value = v_display[:3] + '...' + v_display[-3:] if len(v_display) > 6 and k != 'OLLAMA_API_URL' else v_display
                log.info(f"  {k}={display_value}")

        action = input("Add/update another env variable? (yes/no/done): ").strip().lower()
        if action in ['no', 'done']:
            break
        if action == 'yes':
            var_name = input("Enter variable name (e.g., GEMINI_API_KEY): ").strip().upper() # Standardize to uppercase
            if not var_name:
                log.warning("Variable name cannot be empty. Skipping.")
                continue
            var_value = input(f"Enter value for {var_name}: ").strip()
            env_vars[var_name] = var_value
            log.info(f"Variable '{var_name}' set/updated.")
        else:
            log.warning("Invalid input. Please enter 'yes', 'no', or 'done'.")
    
    log.debug(f"Final env_vars to be written to {ENV_PATH}: {env_vars}") # DEBUG LOG
    with open(ENV_PATH, 'w') as f: # Use the defined constant
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    log.info(f"Environment variables saved to {ENV_PATH}")

def get_missing_provider_credentials() -> list[str]:
    """
    Checks .env file against providers.yaml to find missing or empty required credentials.
    Returns a list of missing/empty environment variable names.
    """
    missing_vars = []
    
    # 1. Load currently set environment variables from .env
    current_env_vars = {}
    if os.path.exists(ENV_PATH): # Use the defined constant
        with open(ENV_PATH, 'r') as f: # Use the defined constant
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    current_env_vars[key.strip()] = value.strip()

    # 2. Load providers.yaml to identify required environment variables
    required_env_vars_from_providers = set()
    if os.path.exists(PROVIDERS_CONFIG_PATH):
        try:
            with open(PROVIDERS_CONFIG_PATH, 'r') as f:
                providers_config = yaml.safe_load(f)
            if providers_config:
                required_env_vars_from_providers = _find_env_vars_in_config(providers_config)
        except Exception as e:
            log.error(f"Could not load or parse '{PROVIDERS_CONFIG_PATH}' for credential check: {e}")
            return [] # Cannot determine missing if providers.yaml is unreadable

    # 3. Check if required vars are present and non-empty in current_env_vars
    for req_var in required_env_vars_from_providers:
        if not current_env_vars.get(req_var): # Checks for presence and non-empty string
            missing_vars.append(req_var)
            
    return sorted(list(set(missing_vars))) # Return unique sorted list