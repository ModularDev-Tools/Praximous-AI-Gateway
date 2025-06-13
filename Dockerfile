# Dockerfile

# Start with a lightweight Python base image
FROM python:3.11-slim

# Create a non-root user and group
RUN groupadd --system appuser && useradd --system --gid appuser appuser

ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This includes main.py and the entire 'api' directory
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the port that Uvicorn will run on
EXPOSE 8000

# The command to run when the container starts
# This will first check for the identity file and then start the server
# Note: We are not using --reload in production
# (UVICORN_RELOAD env var controls this, see above)
CMD ["python", "main.py"]

# Healthcheck to ensure the application is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl --fail http://localhost:8000/ || exit 1