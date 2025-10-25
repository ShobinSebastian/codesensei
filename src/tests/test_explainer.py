# src/tests/test_explainer.py

"""
Code Explainer Tests
====================
Test the code explainer feature (Day 8-10).

Run with: python src/tests/test_explainer.py

Author: Shobin Sebastian
Date: November 2025
"""

import sys
import os

# src/tests/test_explainer.py

"""
Code Explainer Tests
====================
Test the code explainer feature (Day 8-10).

Run with: python -m src.tests.test_explainer

Author: Shobin Sebastian
Date: November 2025
"""

import sys
import os

# Add project root to path
current_file = os.path.abspath(__file__)
tests_dir = os.path.dirname(current_file)
src_dir = os.path.dirname(tests_dir)
project_root = os.path.dirname(src_dir)
sys.path.insert(0, project_root)

from src.features.code_explainer import CodeExplainer


def print_header(title):
    """Print test header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_1_simple_function():
    """Test 1: Explain a simple function."""
    print_header("TEST 1: Simple Function")
    
    code = """
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
print(result)
"""
    
    print("Code:")
    print(code)
    
    explainer = CodeExplainer()
    result = explainer.explain(code, detail_level="medium")
    
    print(f"\n📖 Overview:")
    print(f"{result['overview']}")
    
    print(f"\n🎯 Concepts Found ({len(result['concepts'])}):")
    for concept in result['concepts']:
        print(f"  • {concept['name']}: {concept['description']}")
    
    print(f"\n📊 Complexity:")
    print(f"  Grade: {result['complexity']['complexity_grade']}")
    print(f"  {result['complexity']['interpretation']}")
    
    print("\n✅ Test 1 Complete!")


def test_2_recursive_function():
    """Test 2: Explain recursion."""
    print_header("TEST 2: Recursive Function")
    
    code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"5! = {result}")
"""
    
    print("Code:")
    print(code)
    
    explainer = CodeExplainer()
    result = explainer.explain(code, detail_level="detailed")
    
    print(f"\n📖 Overview:")
    print(f"{result['overview']}")
    
    print(f"\n📝 Line-by-Line Breakdown:")
    for item in result['line_by_line']:
        print(f"\n  Lines {item['line_range']}:")
        print(f"  Code: {item['code'][:50]}...")
        print(f"  → {item['explanation']}")
    
    print(f"\n🎯 Concepts Found:")
    for concept in result['concepts']:
        print(f"  • {concept['name']}")
    
    print(f"\n📚 Learning Path:")
    for item in result['learning_path']:
        print(f"  [{item['difficulty']}] {item['topic']}")
        print(f"    Why: {item['why']}")
    
    print("\n✅ Test 2 Complete!")


def test_3_class_example():
    """Test 3: Explain a class."""
    print_header("TEST 3: Class Definition")
    
    code = """
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x):
        self.result += x
        return self.result
    
    def reset(self):
        self.result = 0

calc = Calculator()
calc.add(5)
calc.add(3)
print(calc.result)
"""
    
    print("Code:")
    print(code)
    
    explainer = CodeExplainer()
    result = explainer.explain(code, detail_level="medium")
    
    print(f"\n📖 Overview:")
    print(f"{result['overview']}")
    
    print(f"\n🎯 Key Concepts:")
    for concept in result['concepts']:
        print(f"  • {concept['name']}: {concept['description']}")
    
    print(f"\n📊 Complexity:")
    print(f"  {result['complexity']['interpretation']}")
    
    print(f"\n📚 Suggested Learning:")
    for item in result['learning_path'][:3]:
        print(f"  • {item['topic']} ({item['difficulty']})")
    
    print("\n✅ Test 3 Complete!")


def test_4_list_comprehension():
    """Test 4: Explain list comprehension."""
    print_header("TEST 4: List Comprehension")
    
    code = """
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers if x % 2 == 0]
print(squared)
"""
    
    print("Code:")
    print(code)
    
    explainer = CodeExplainer()
    result = explainer.explain(code, detail_level="basic")
    
    print(f"\n📖 Overview:")
    print(f"{result['overview']}")
    
    print(f"\n🎯 Concepts Found:")
    for concept in result['concepts']:
        print(f"  • {concept['name']}")
    
    print("\n✅ Test 4 Complete!")


def test_5_complex_code():
    """Test 5: Complex code with multiple features."""
    print_header("TEST 5: Complex Code")
    
    code = """
import json
from typing import List, Dict

class DataProcessor:
    def __init__(self, filename: str):
        self.filename = filename
        self.data = []
    
    def load(self) -> None:
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print(f"File {self.filename} not found")
            self.data = []
    
    def filter_by_value(self, key: str, value: any) -> List[Dict]:
        return [item for item in self.data if item.get(key) == value]
    
    def get_statistics(self) -> Dict[str, int]:
        return {
            'total': len(self.data),
            'keys': len(self.data[0].keys()) if self.data else 0
        }
"""
    
    print("Code:")
    print(code[:200] + "...")
    
    explainer = CodeExplainer()
    result = explainer.explain(code, detail_level="detailed")
    
    print(f"\n📖 Overview:")
    print(f"{result['overview'][:150]}...")
    
    print(f"\n🎯 Concepts Found ({len(result['concepts'])}):")
    for concept in result['concepts']:
        print(f"  • {concept['name']}")
    
    print(f"\n📊 Complexity Analysis:")
    print(f"  Grade: {result['complexity']['complexity_grade']}")
    print(f"  Cyclomatic: {result['complexity']['cyclomatic']}")
    print(f"  Maintainability: {result['complexity']['maintainability']}")
    print(f"  {result['complexity']['interpretation']}")
    
    print(f"\n📚 Learning Path:")
    for item in result['learning_path']:
        print(f"  • {item['topic']} ({item['difficulty']})")
    
    print(f"\n📋 Metadata:")
    print(f"  Lines of Code: {result['metadata']['lines_of_code']}")
    print(f"  Has Functions: {result['metadata']['has_functions']}")
    print(f"  Has Classes: {result['metadata']['has_classes']}")
    
    print("\n✅ Test 5 Complete!")


def test_comparison():
    """Test 6: Compare different detail levels."""
    print_header("TEST 6: Detail Level Comparison")
    
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    print("Code:")
    print(code)
    
    explainer = CodeExplainer()
    
    print("\n🔹 BASIC Level:")
    basic = explainer.explain(code, detail_level="basic")
    print(f"  {basic['overview']}")
    print(f"  Line-by-line: {len(basic['line_by_line'])} items")
    
    print("\n🔹 MEDIUM Level:")
    medium = explainer.explain(code, detail_level="medium")
    print(f"  {medium['overview'][:100]}...")
    print(f"  Line-by-line: {len(medium['line_by_line'])} items")
    print(f"  Concepts: {len(medium['concepts'])}")
    
    print("\n🔹 DETAILED Level:")
    detailed = explainer.explain(code, detail_level="detailed")
    print(f"  {detailed['overview'][:100]}...")
    print(f"  Line-by-line: {len(detailed['line_by_line'])} items")
    print(f"  Concepts: {len(detailed['concepts'])}")
    print(f"  Learning path: {len(detailed['learning_path'])} suggestions")
    
    print("\n✅ Test 6 Complete!")


def run_all_tests():
    """Run all explainer tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*18 + "CODE EXPLAINER TESTS" + " "*29 + "║")
    print("║" + " "*23 + "Day 8-10 Feature" + " "*29 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Simple Function", test_1_simple_function),
        ("Recursive Function", test_2_recursive_function),
        ("Class Definition", test_3_class_example),
        ("List Comprehension", test_4_list_comprehension),
        ("Complex Code", test_5_complex_code),
        ("Detail Levels", test_comparison),
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
    
    # Summary
    print("\n" + "="*70)
    print("  📊 TEST SUMMARY")
    print("="*70)
    print(f"\n✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Code Explainer is working!")
    
    print("\n📋 Next Steps:")
    print("1. Start API server: uvicorn src.api.main:app --reload")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Try the /explain endpoint with your own code")
    print("4. Test different detail levels (basic/medium/detailed)")
    print()


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()