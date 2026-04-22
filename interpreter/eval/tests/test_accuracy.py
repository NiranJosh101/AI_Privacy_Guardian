import pytest
import json
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerCorrectnessMetric, FaithfulnessMetric
from engine.orchestrator import InterpreterOrchestrator # Adjust based on your actual class name

# 1. Load the Golden Dataset
def load_golden_set():
    with open("eval/data/golden_set.json", "r") as f:
        return json.load(f)

@pytest.mark.parametrize("case", load_golden_set())
def test_privacy_interpreter_logic(case):
    """
    Test the Interpreter's ability to extract accurate privacy data 
    from a live URL against our Golden Ground Truth.
    """
    
    # --- STEP 1: Run your actual Microservice Logic ---
    # instantiate the interpreter here. 
    interpreter = InterpreterOrchestrator()
    actual_response = interpreter.interpret_policy(case['url'])
    
    # Convert actual response to string for the evaluator if it's a dict/Pydantic model
    actual_output_str = json.dumps(actual_response)
    expected_output_str = json.dumps(case['expected_output'])
    
    # --- STEP 2: Define the Metrics ---
    # AnswerCorrectness: Compares actual vs expected (the "Truth" score)
    # Faithfulness: Ensures the AI didn't hallucinate info NOT in the context
    correctness_metric = AnswerCorrectnessMetric(threshold=0.7)
    faithfulness_metric = FaithfulnessMetric(threshold=0.8)

    # --- STEP 3: Create the DeepEval Test Case ---
    test_case = LLMTestCase(
        input=f"Analyze the privacy policy at {case['url']}",
        actual_output=actual_output_str,
        expected_output=expected_output_str,
        retrieval_context=case['gold_context'] # Using the snippets we manually verified
    )

    # --- STEP 4: Run the Evaluation ---
    assert_test(test_case, [correctness_metric, faithfulness_metric])