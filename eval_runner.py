#!/usr/bin/env python3
"""
Eval Runner: Run golden dataset tests against the Claude API.

Usage:
    python eval_runner.py [--dataset golden_dataset.csv] [--prompt prompt.txt]

Exit codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import csv
import sys
import argparse
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed.")
    print("Run: pip install anthropic")
    sys.exit(1)


def load_prompt_template(path: str) -> str:
    """Load the prompt template from a file."""
    return Path(path).read_text()


def fill_template(template: str, variables: dict) -> str:
    """Replace {{VARIABLE}} placeholders with values."""
    result = template
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, value or "")
    return result


def check_output(actual: str, expected: str) -> bool:
    """
    Check if the actual output meets expectations.
    
    This is a simple substring check. For more sophisticated evals,
    consider LLM-as-judge (see README for resources).
    """
    if not expected:
        return True  # No expectation = always pass
    return expected.lower() in actual.lower()


def run_evals(dataset_path: str, prompt_path: str, model: str = "claude-sonnet-4-20250514") -> tuple[int, int, list]:
    """
    Run all evals from the dataset.
    
    Returns: (passed_count, total_count, failures_list)
    """
    client = anthropic.Anthropic()
    template = load_prompt_template(prompt_path)
    
    passed = 0
    total = 0
    failures = []
    
    with open(dataset_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total += 1
            test_name = f"Test {total}"
            
            # Separate expected_output from variables
            expected = row.pop('expected_output', '')
            variables = row
            
            # Fill the template
            prompt = fill_template(template, variables)
            
            # Call the API
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                actual = response.content[0].text
            except Exception as e:
                print(f"✗ {test_name}: API ERROR - {e}")
                failures.append({
                    "test": test_name,
                    "error": str(e),
                    "variables": variables
                })
                continue
            
            # Check the result
            if check_output(actual, expected):
                passed += 1
                print(f"✓ {test_name}: PASSED")
            else:
                print(f"✗ {test_name}: FAILED")
                print(f"  Expected to contain: {expected}")
                print(f"  Got: {actual[:300]}{'...' if len(actual) > 300 else ''}")
                failures.append({
                    "test": test_name,
                    "expected": expected,
                    "actual": actual[:500],
                    "variables": variables
                })
    
    return passed, total, failures


def main():
    parser = argparse.ArgumentParser(description="Run Claude API evals against a golden dataset")
    parser.add_argument("--dataset", default="golden_dataset.csv", help="Path to CSV dataset")
    parser.add_argument("--prompt", default="prompt.txt", help="Path to prompt template")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Model to use")
    args = parser.parse_args()
    
    # Validate files exist
    if not Path(args.dataset).exists():
        print(f"Error: Dataset not found: {args.dataset}")
        sys.exit(1)
    if not Path(args.prompt).exists():
        print(f"Error: Prompt template not found: {args.prompt}")
        sys.exit(1)
    
    print(f"Running evals...")
    print(f"  Dataset: {args.dataset}")
    print(f"  Prompt:  {args.prompt}")
    print(f"  Model:   {args.model}")
    print("-" * 40)
    
    passed, total, failures = run_evals(args.dataset, args.prompt, args.model)
    
    print("-" * 40)
    print(f"Results: {passed}/{total} tests passed ({100*passed//total}%)")
    
    if failures:
        print(f"\n{len(failures)} test(s) failed.")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
