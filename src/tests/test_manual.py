# src/tests/test_manual.py

"""
Manual Testing Script
=====================
Quick script to test the complete system manually.

Usage:
    python src/tests/test_manual.py
    OR
    python -m src.tests.test_manual

Author: Shobin Sebastian
Date: November 2025
"""

import sys
import os

# CRITICAL FIX: Add project root to Python path
# This allows imports like "from src.core.orchestrator import ..."
current_file = os.path.abspath(__file__)  # Full path to this file
tests_dir = os.path.dirname(current_file)  # src/tests/
src_dir = os.path.dirname(tests_dir)  # src/
project_root = os.path.dirname(src_dir)  # F:\Projects\CodeSensei

sys.path.insert(0, project_root)

print(f"🔍 Project root: {project_root}")
print(f"🔍 Python path: {sys.path[0]}\n")

# Now imports should work
try:
    from src.core.orchestrator import CodeAnalysisOrchestrator
    print("✅ Import successful!\n")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nMake sure you have created:")
    print("  - src/core/orchestrator.py")
    print("  - src/core/__init__.py")
    sys.exit(1)


def print_separator(title=""):
    """Print a nice separator."""
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)


def print_issues(issues, max_issues=5):
    """Print issues in a readable format."""
    if not issues:
        print("✅ No issues found!")
        return
    
    print(f"\n🔍 Found {len(issues)} issue(s):\n")
    
    for i, issue in enumerate(issues[:max_issues], 1):
        severity_emoji = {
            'critical': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(issue.get('severity', 'low'), '⚪')
        
        print(f"{i}. {severity_emoji} [{issue.get('severity', 'unknown').upper()}] "
              f"Line {issue.get('line', '?')}")
        print(f"   Category: {issue.get('category', 'unknown')}")
        print(f"   {issue.get('message', 'No message')}")
        
        if 'explanation' in issue:
            print(f"   💡 {issue['explanation'][:100]}...")
        
        if 'learning_tip' in issue:
            print(f"   {issue['learning_tip']}")
        
        if 'code_snippet' in issue:
            print(f"   Code: {issue['code_snippet']}")
        
        print()
    
    if len(issues) > max_issues:
        print(f"... and {len(issues) - max_issues} more issues")


def test_case_1_buggy_code():
    """Test Case 1: Code with obvious bugs."""
    print_separator("TEST 1: Buggy Code (Division by Zero)")
    
    code = """
def divide_numbers(a, b):
    return a / b

result = divide_numbers(10, 0)
print(result)
"""
    
    print("Code:")
    print(code)
    
    orchestrator = CodeAnalysisOrchestrator()
    result = orchestrator.analyze(code, use_llm=False)  # Start with static only
    
    print(f"\n📊 Summary:")
    print(f"   Total: {result['summary']['total']}")
    print(f"   Critical: {result['summary']['by_severity']['critical']}")
    print(f"   Medium: {result['summary']['by_severity']['medium']}")
    print(f"   Low: {result['summary']['by_severity']['low']}")
    print(f"   Time: {result['metadata']['execution_time']}s")
    
    print_issues(result['issues'])


def test_case_2_security_issue():
    """Test Case 2: SQL Injection vulnerability."""
    print_separator("TEST 2: Security Issue (SQL Injection)")
    
    code = """
def get_user_by_id(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

user = get_user_by_id(input("Enter user ID: "))
"""
    
    print("Code:")
    print(code)
    
    orchestrator = CodeAnalysisOrchestrator()
    result = orchestrator.analyze(code, use_llm=False)
    
    print(f"\n📊 Summary:")
    print(f"   Security issues: {result['summary']['by_category'].get('security', 0)}")
    print(f"   Time: {result['metadata']['execution_time']}s")
    
    print_issues(result['issues'])


def test_case_3_clean_code():
    """Test Case 3: Clean, well-written code."""
    print_separator("TEST 3: Clean Code")
    
    code = """
def calculate_factorial(n: int) -> int:
    \"\"\"Calculate factorial of n using recursion.\"\"\"
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

def main():
    number = 5
    result = calculate_factorial(number)
    print(f"Factorial of {number} is {result}")

if __name__ == "__main__":
    main()
"""
    
    print("Code:")
    print(code)
    
    orchestrator = CodeAnalysisOrchestrator()
    result = orchestrator.analyze(code, use_llm=False)
    
    print(f"\n📊 Summary:")
    print(f"   Total: {result['summary']['total']}")
    print(f"   Critical: {result['summary']['by_severity']['critical']}")
    print(f"   Time: {result['metadata']['execution_time']}s")
    
    if result['summary']['total'] == 0:
        print("\n✅ Perfect! No issues found in this clean code!")
    else:
        print_issues(result['issues'])


def test_case_4_multiple_issues():
    """Test Case 4: Code with multiple types of issues."""
    print_separator("TEST 4: Multiple Issues")
    
    code = """
import os

def process_data(data):
    results = []
    for i in range(len(data) + 1):
        results.append(data[i] * 2)
    return results

def save_to_file(filename, content):
    file = open(filename, 'w')
    file.write(content)

password = "admin123"

unused_variable = 42

numbers = [1, 2, 3, 4, 5]
processed = process_data(numbers)
"""
    
    print("Code:")
    print(code)
    
    orchestrator = CodeAnalysisOrchestrator()
    result = orchestrator.analyze(code, use_llm=False)
    
    print(f"\n📊 Summary:")
    print(f"   Total: {result['summary']['total']}")
    print(f"   By Category:")
    for category, count in result['summary']['by_category'].items():
        if count > 0:
            print(f"      {category}: {count}")
    print(f"   Time: {result['metadata']['execution_time']}s")
    
    print_issues(result['issues'])


def test_case_5_static_only():
    """Test Case 5: Quick static analysis test."""
    print_separator("TEST 5: Static Analysis Only")
    
    code = """
def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

result = calculate_average([])
"""
    
    print("Code:")
    print(code)
    
    orchestrator = CodeAnalysisOrchestrator()
    
    print("\n🔹 Running Static Analysis:")
    static_result = orchestrator.analyze(code, use_llm=False)
    print(f"   Issues found: {len(static_result['issues'])}")
    print(f"   Time: {static_result['metadata']['execution_time']}s")
    
    print("\n📝 Issues:")
    print_issues(static_result['issues'])


def run_all_tests():
    """Run all test cases."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "CODESENSEI MANUAL TESTING" + " "*28 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Test 1: Buggy Code", test_case_1_buggy_code),
        ("Test 2: Security Issue", test_case_2_security_issue),
        ("Test 3: Clean Code", test_case_3_clean_code),
        ("Test 4: Multiple Issues", test_case_4_multiple_issues),
        ("Test 5: Static Only", test_case_5_static_only),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print_separator("TESTING COMPLETE")
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("\nNext steps:")
    print("1. Start API server: uvicorn src.api.main:app --reload")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Test the /analyze endpoint with sample code")
    print("\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()