from logs.logger_utils import get_logger

logger = get_logger(__name__)

def check_escalation(user_query, category):
    """
    Determines whether a user query should be escalated based on keywords or category.
    """
    logger.info(f"Checking escalation for category: {category}")
    query = user_query.lower()

    escalation_keywords = [
        "urgent", "asap", "immediately", "emergency", "critical","important",
        "presentation", "client call", "deadline", "won't turn on",
        "black screen", "pop-up", "hacked", "malware", "security breach"
    ]

    for word in escalation_keywords:
        if word in query:
            logger.info(f"Escalated due to keyword: {word}")
            return True, f"Escalated due to keyword: '{word}'"

    if category in ["security_incident", "hardware_failure"]:
        if any(term in query for term in ["won't turn on", "black screen", "hacked"]):
            return True, "Escalated due to critical hardware or security issue."

    return False, "No escalation conditions met."
