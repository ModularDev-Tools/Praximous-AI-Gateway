# main.py
import sys
import os
import yaml
from api.v1.endpoints import rag_interface_router # Import the new RAG router

from core.logger import log # Import the configured logger
from config.credentials_manager import setup_api_credentials, get_missing_provider_credentials

CONFIG_DIR = 'config'
CONFIG_PATH = os.path.join('config', 'identity.yaml')

def init_identity():
    log.info("Starting Praximous Identity Initialization.")
    data = {}
    data['system_name'] = input("System Name (e.g. Praximous-Acme): ").strip() or "Praximous-Default"
    data['business_name'] = input("Business Name: ").strip() or "Default Business"
    data['industry'] = input("Industry: ").strip() or "General"
    data['persona_style'] = input("Persona Style (tone): ").strip() or "Professional and concise"
    data['sensitivity_level'] = input("Sensitivity Level (Low/Medium/High): ").strip() or "High"
    data['location'] = input("Location: ").strip() or "Unknown"
    
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(data, f)

    log.info(f"Identity configuration saved to {CONFIG_PATH}.")

    # Call the separate function to handle API credentials
    setup_api_credentials()

def rename_system(new_name: str):
    """Renames the system in the identity.yaml file."""
    if not os.path.exists(CONFIG_PATH):
        log.error(f"Identity configuration file '{CONFIG_PATH}' not found. Cannot rename.")
        log.error("Please run 'python main.py --init' first to create an identity.")
        return

    try:
        with open(CONFIG_PATH, 'r') as f:
            identity_data = yaml.safe_load(f) or {}
        
        old_name = identity_data.get('system_name', 'Unknown')
        identity_data['system_name'] = new_name

        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(identity_data, f)
        log.info(f"System renamed from '{old_name}' to '{new_name}' in '{CONFIG_PATH}'.")
        log.info("The display name in logs will update on the next full application restart.")
    except Exception as e:
        log.error(f"Failed to rename system: {e}", exc_info=True)

def reset_identity_config():
    """Resets the system identity by removing identity.yaml."""
    if not os.path.exists(CONFIG_PATH):
        log.info(f"Identity configuration file '{CONFIG_PATH}' does not exist. Nothing to reset.")
        log.info("You can create a new identity by running 'python main.py --init'.")
        return

    confirm = input(f"Are you sure you want to reset the identity by deleting '{CONFIG_PATH}'? (yes/no): ").strip().lower()
    if confirm == 'yes':
        try:
            os.remove(CONFIG_PATH)
            log.info(f"Identity configuration file '{CONFIG_PATH}' has been removed.")
            log.info("Please run 'python main.py --init' to create a new identity and setup API credentials.")
        except Exception as e:
            log.error(f"Failed to remove identity file: {e}", exc_info=True)
    else:
        log.info("Identity reset cancelled.")

def main():
    if '--init' in sys.argv:
        init_identity()
        return

    # Default action: Start the API server
    log.info("Attempting to start Praximous API server...")
    if not os.path.exists(CONFIG_PATH):
        log.error("Identity not initialized. Run `python main.py --init` to setup.")
        log.error("API server will not start without an identity.")
        return
    
    # Handle --rename argument
    if '--rename' in sys.argv:
        try:
            rename_idx = sys.argv.index('--rename')
            if len(sys.argv) > rename_idx + 1:
                new_name_arg = sys.argv[rename_idx + 1]
                rename_system(new_name_arg)
            else:
                log.error("No new name provided for --rename. Usage: python main.py --rename \"New-System-Name\"")
        except ValueError:
            pass # Should not happen if '--rename' is in sys.argv
        return # Exit after rename attempt

    if '--reset-identity' in sys.argv:
        reset_identity_config()
        return # Exit after reset attempt

    # Check for missing required credentials based on providers.yaml
    missing_keys = get_missing_provider_credentials()
    if missing_keys:
        log.warning("The following required API keys/environment variables are missing or empty in your .env file:")
        for key in missing_keys:
            log.warning(f"  - {key}")
        log.warning("Praximous will attempt to start, but functionality requiring these keys may be limited or fall back to local providers if configured.")
        log.warning(f"Please ensure these environment variables are set. They can be configured in your .env file or directly in your container's environment.")

    try:
        import uvicorn

        # Configure Uvicorn reload behavior
        # Enabled by default for local development.
        # Can be disabled by setting the UVICORN_RELOAD environment variable to "false".
        uvicorn_reload_env = os.getenv("UVICORN_RELOAD", "true").lower()
        reload_enabled = uvicorn_reload_env == "true"

        log_level = "info"
        if reload_enabled:
            log.info("Starting Uvicorn server with auto-reload enabled (development mode).")
        else:
            log.info("Starting Uvicorn server with auto-reload disabled (production mode).")
            # Optionally, adjust log level for production
            # log_level = "warning" 

        # We assume api.server:app points to your FastAPI application instance
        uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=reload_enabled, log_level=log_level)
    except ImportError:
        log.critical("Uvicorn is not installed. Please install it with: pip install uvicorn[standard]")
    except Exception as e:
        log.critical(f"Could not start API server: {e}", exc_info=True)

if __name__ == "__main__":
    main()
