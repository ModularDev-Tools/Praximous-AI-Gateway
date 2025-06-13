#!/bin/sh
# Entrypoint script for Praximous application

# Exit immediately if a command exits with a non-zero status.
set -e

CONFIG_FILE_PATH="/app/config/identity.yaml"

# Check if the identity configuration file exists
if [ ! -f "$CONFIG_FILE_PATH" ]; then
  echo "---------------------------------------------------------------------"
  echo "ERROR: Praximous identity file not found at $CONFIG_FILE_PATH."
  echo "The application cannot start without an identity."
  echo ""
  echo "To resolve this, you have a few options:"
  echo "1. Initialize interactively (if the container is running and you can exec into it):"
  echo "   docker compose exec praximous python main.py --init"
  echo "   (After initialization, you might need to restart the service: docker compose restart praximous)"
  echo ""
  echo "2. Create the identity file locally first, then start the container:"
  echo "   Run 'python main.py --init' in your project directory on your host machine."
  echo "   This will create './config/identity.yaml'. Your docker-compose.yml"
  echo "   is already configured to mount './config' into '/app/config'."
  echo ""
  echo "3. (Advanced) Modify 'init_identity()' in 'main.py' to support"
  echo "   non-interactive initialization (e.g., via environment variables)"
  echo "   and trigger this modified initialization from this entrypoint script."
  echo "---------------------------------------------------------------------"
  exit 1
fi

echo "Identity file found at $CONFIG_FILE_PATH. Proceeding to start application..."
# Execute the CMD passed to this entrypoint script (e.g., python main.py)
exec "$@"