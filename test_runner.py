import asyncio
import httpx
import json
import re
import os
from difflib import SequenceMatcher
from logs.logger_utils import get_logger

# Initialize logger
logger = get_logger("test_runner")

# Load and validate test data
with open("documents/test_requests.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f).get("test_requests", [])

tests = []
for entry in raw_data:
    if isinstance(entry, dict):
        tests.append(entry)
    elif isinstance(entry, list) and isinstance(entry[0], str):
        try:
            tests.append(json.loads(entry[0]))
        except json.JSONDecodeError:
            logger.warning(f"Skipping malformed test entry: {entry[0]}")

def tokenize(text):
    """Returns a set of lowercase word tokens from the input text."""
    return set(re.findall(r'\w+', text.lower()))

def is_fuzzy_present(expected, response_text):
    """Checks if expected text is approximately present in the response."""
    expected_tokens = tokenize(expected)
    response_sentences = re.split(r'[.?!\n]', response_text)

    for sentence in response_sentences:
        sentence_tokens = tokenize(sentence)
        if not sentence_tokens:
            continue

        intersection = expected_tokens & sentence_tokens
        union = expected_tokens | sentence_tokens
        jaccard = len(intersection) / len(union) if union else 0
        fuzzy_score = SequenceMatcher(None, expected.lower(), sentence.lower()).ratio()

        if jaccard > 0.35 or fuzzy_score > 0.6:
            return True
    return False

async def run_tests():
    """Executes all test cases against the /helpdesk endpoint."""
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=60.0) as client:
        passed, failed = 0, 0
        logger.info("Starting Helpdesk test suite")

        for test in tests:
            user_request = test["request"]
            expected_category = test["expected_classification"].lower()
            expected_elements = test.get("expected_elements", [])
            should_escalate = test.get("escalate", False)

            try:
                response = await client.post("/helpdesk", json={
                    "request": user_request,
                    "username": "TestUser",
                    "contact": "test@example.com"
                })

                try:
                    result = response.json()
                except Exception as json_err:
                    logger.error(f"FAIL: Invalid JSON response for request: '{user_request}'")
                    logger.error(f"Raw response: {response.text}")
                    logger.error(f"JSON Error: {json_err}")
                    failed += 1
                    continue

                if "error" in result:
                    logger.error(f"FAIL: Server error for '{user_request}' - {result['error']}")
                    failed += 1
                    continue

                actual_category = result["category"].lower()
                category_match = actual_category == expected_category
                escalation_match = result["escalate"] == should_escalate

                missing_elements = [
                    elem for elem in expected_elements if not is_fuzzy_present(elem, result["response"])
                ]
                elements_present = not missing_elements

                if category_match and escalation_match and elements_present:
                    logger.info(f"PASS: {user_request}")
                    passed += 1
                else:
                    logger.warning(f"FAIL: {user_request}")
                    logger.warning(f"Expected Category: {expected_category}, Got: {actual_category}")
                    logger.warning(f"Expected Escalation: {should_escalate}, Got: {result['escalate']}")
                    if missing_elements:
                        logger.warning(f"Missing Elements: {missing_elements}")
                    logger.warning(f"Full Response: {result['response']}")
                    failed += 1

            except httpx.RequestError as e:
                logger.critical(f"REQUEST ERROR: '{user_request}' - Exception: {e}")
                failed += 1

        logger.info(f"Test Run Summary: {passed} Passed, {failed} Failed")

if __name__ == "__main__":
    asyncio.run(run_tests())
