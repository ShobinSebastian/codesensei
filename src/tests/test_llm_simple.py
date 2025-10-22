import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.llm_agent import LLMAgent

# Initialize the agent
agent = LLMAgent()

# Test 1: Analyze buggy code
buggy_code = """
def divide(a, b):
    return a / b

result = divide(10, 0) 
"""

print("Testing LLM Agent...")
issues = agent.analyze(buggy_code)

print(f"\nFound {len(issues)} issues:")
for issue in issues:
    print(f"\nMessage: {issue.get('message')}")
    print(f"Explanation: {issue.get('explanation')}")
    print(f"Severity: {issue.get('severity')}")

# Test 2: Explain code
print("\n\n--- CODE EXPLANATION ---")
explanation = agent.explain_code(buggy_code)
print(explanation)