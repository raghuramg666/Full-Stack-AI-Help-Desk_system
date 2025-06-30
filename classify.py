from logs.logger_utils import get_logger

logger = get_logger(__name__)

def classify_request(text):
    """
    Classifies the user input into a predefined IT helpdesk category.
    """
    logger.info(f"Classifying request: {text}")
    text = text.lower()

    if "password" in text and "reset" in text:
        return "password_reset"
    if "install" in text or "installation" in text:
        return "software_installation"
    if "wifi" in text or "network" in text:
        return "network_connectivity"
    if "email" in text and ("not working" in text or "sync" in text):
        return "email_configuration"
    if "screen" in text and ("black" in text or "flicker" in text):
        return "hardware_failure"
    if "hack" in text or "suspicious" in text:
        return "security_incident"
    if "policy" in text or "rule" in text:
        return "policy_question"

    return "general_inquiry"
