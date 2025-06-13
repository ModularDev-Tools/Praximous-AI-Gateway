# Dockerfile

# Start with a lightweight Python base image
FROM python:3.11-slim

# Create a non-root user and group
RUN groupadd --system appuser && useradd --system --gid appuser appuser

ENV PYTHONUNBUFFERED=1
# Default to Uvicorn reload disabled (production mode).
# This aligns with the comment below and main.py's behavior.
# Can be overridden at runtime by setting UVICORN_RELOAD=true for development.
ENV UVICORN_RELOAD=false

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container.
# This includes main.py, the 'api' directory, and entrypoint.sh (if present in the build context root).
COPY . .

# Make the entrypoint script executable (assuming it's now at /app/entrypoint.sh)
RUN chmod +x /app/entrypoint.sh

# Change ownership of the app directory to the non-root user after all files are copied and permissions set
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Set the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# The command to run when the container starts
# This command is passed as arguments to the ENTRYPOINT script.
# Note: We are not using --reload in production
# (UVICORN_RELOAD env var controls this, see above)
CMD ["python", "main.py"]

# Healthcheck to ensure the application is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl --fail http://localhost:8000/ || exit 1