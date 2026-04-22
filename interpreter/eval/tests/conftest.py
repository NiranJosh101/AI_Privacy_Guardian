import pytest
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def check_environment():
    """
    Ensure the Judge LLM has its credentials before running.
    DeepEval usually defaults to OpenAI, but you can configure 
    other providers here.
    """
    required_keys = ["GROQ_API_KEY"] 
    
    for key in required_keys:
        if not os.getenv(key):
            pytest.exit(f"CRITICAL: {key} is not set. The 'Truth Detector' needs a Judge LLM.")

@pytest.fixture(scope="session")
def eval_logger():
    """
    Optional: Setup a custom logger to track how many 'Golden'
    cases we are processing.
    """
    import logging
    logger = logging.getLogger("TruthDetector")
    logger.setLevel(logging.INFO)
    return logger

def pytest_sessionfinish(session, exitstatus):
    """
    This runs after all tests are done. 
    You can use this to trigger a notification or 
    move the 'results.json' to a specific folder.
    """
    print("\n--- Evaluation Session Complete ---")
    if exitstatus == 0:
        print("All metrics within acceptable thresholds.")
    else:
        print("Accuracy dropped below threshold. Check the reports.")