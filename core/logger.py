# core/logger.py
import logging
import os
import sys

LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "praximous.log")

class ContextFilter(logging.Filter):
    """
    Injects context (like system_name) into log records.
    """
    def filter(self, record):
        try:
            # Attempt to import here, inside the filter method
            from core.system_context import system_context
            record.system_name = system_context.display_name
        except ImportError: # Catches the "partially initialized module" error during circular import
            record.system_name = "Praximous-Initializing"
        # It's also good practice to catch AttributeError in case system_context is imported but display_name isn't ready
        return True

def setup_logger(name="praximous", log_level_env_var="LOG_LEVEL", default_level=logging.INFO):
    """
    Configures and returns a logger instance.
    """
    # Ensure logs directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    # Determine log level
    log_level_str = os.getenv(log_level_env_var, logging.getLevelName(default_level)).upper()
    log_level = getattr(logging, log_level_str, default_level)
    logger.setLevel(log_level)

    # Prevent duplicate handlers if logger is already configured (e.g., in tests or multiple calls)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(system_name)s - %(name)s - [%(levelname)s] - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    # Create and add context filter
    context_filter = ContextFilter()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler(LOG_FILE, mode='a') # Append mode
    file_handler.setFormatter(formatter)
    file_handler.addFilter(context_filter)
    logger.addHandler(file_handler)

    return logger

# Global logger instance for easy import
log = setup_logger()