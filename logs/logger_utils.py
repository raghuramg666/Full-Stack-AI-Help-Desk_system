import logging
import os

# Create logs directory if it doesn't exist
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

log_file = os.path.join(log_folder, "system.log")

# Configure global logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(module)s: %(message)s"
)

def get_logger(name: str):
    """
    Returns a named logger instance.
    """
    return logging.getLogger(name)

def log_interaction(data: dict):
    """
    Logs structured user interaction data.
    """
    logger = get_logger("interaction_logger")
    logger.info(f"User Interaction: {data}")
