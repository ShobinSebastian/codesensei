# src/tests/test_debugger.py

"""
Bug Debugger Tests
==================
Test the bug debugger feature (Day 11-14).

Run with: python -m src.tests.test_debugger

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

from src.features.bug_debugger import BugDebugger


def print_header(title):
    """Print test header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_1_division_by_zero():
    """Test 1: Debug division by zero error."""
    print_header("TEST 1: Division by Zero")
    
    code = """
def divide(a, b):
    return a / b

result = divide(10, 0)
print(result)
"""
    
    error_msg = "ZeroDivisionError: division by zero"
    
    print("Buggy Code:")
    print(code)
    print(f"\nError: {error_msg}")
    
    debugger = BugDebugger()
    result = debugger.debug(code, error_message=error_msg)
    
    print(f"\n🐛 Bugs Found: {len(result['bugs_found'])}")
    for bug in result['bugs_found']:
        print(f"  • Line {bug['line']}: {bug['message']}")
        print(f"    Category: {bug['category']}, Severity: {bug['severity']}")
    
    print(f"\n🔍 Root Cause:")
    if result['root_causes']:
        print(f"{result['root_causes'][0]['explanation'][:200]}...")
    
    print(f"\n🔧 Fix Steps:")
    if result['fix_steps']:
        for step in result['fix_steps'][0]['steps'][:3]:
            print(f"  • {step}")
    
    print(f"\n✅ Fixed Code:")
    print(result['fixed_code'][:150] + "...")
    
    print("\n✅ Test 1 Complete!")


def test_2_index_out_of_range():
    """Test 2: Debug index error."""
    print_header("TEST 2: Index Out of Range")
    
    code = """
numbers = [1, 2, 3, 4, 5]
for i in range(10):
    print(numbers[i])
"""
    
    print("Buggy Code:")
    print(code)
    
    debugger = BugDebugger()
    result = debugger.debug(code)
    
    print(f"\n🐛 Bugs Found: {len(result['bugs_found'])}")
    for bug in result['bugs_found']:
        print(f"  • {bug['message']} (Line {bug['line']})")
    
    print(f"\n💡 Prevention Tips:")
    for tip in result['prevention_tips'][:2]:
        print(f"\n  {tip['tip']}")
        print(f"  Example: {tip['example']}")
        print(f"  Best Practice: {tip['best_practice']}")
    
    print(f"\n🧪 Test Suggestions:")
    for test in result['test_suggestions'][:3]:
        print(f"  • {test}")
    
    print("\n✅ Test 2 Complete!")


def test_3_undefined_variable():
    """Test 3: Debug undefined variable."""
    print_header("TEST 3: Undefined Variable")
    
    code = """
def calculate():
    x = 10
    y = 20
    return x + z  # z is not defined

result = calculate()
"""
    
    print("Buggy Code:")
    print(code)
    
    debugger = BugDebugger()
    result = debugger.debug(code)
    
    print(f"\n🐛 Bugs Found: {len(result['bugs_found'])}")
    
    print(f"\n📊 Severity Breakdown:")
    breakdown = result['metadata']['severity_breakdown']
    print(f"  Critical: {breakdown['critical']}")
    print(f"  Medium: {breakdown['medium']}")
    print(f"  Low: {breakdown['low']}")
    
    print(f"\n🔧 Fixable: {result['metadata']['fixable']}")
    
    print("\n✅ Test 3 Complete!")


def test_4_type_error():
    """Test 4: Debug type error."""
    print_header("TEST 4: Type Error")
    
    code = """
def add_numbers(a, b):
    return a + b

result = add_numbers("5", 3)
print(result)
"""
    
    print("Buggy Code:")
    print(code)
    
    debugger = BugDebugger()
    result = debugger.debug(code)
    
    print(f"\n🐛 Bugs Found: {len(result['bugs_found'])}")
    
    if result['bugs_found']:
        print(f"\n🔍 Root Cause Analysis:")
        for cause in result['root_causes']:
            print(f"\nBug: {cause['bug']}")
            print(f"Explanation: {cause['explanation'][:150]}...")
    
    print(f"\n✅ Fixed Code Preview:")
    print(result['fixed_code'][:200] + "...")
    
    print("\n✅ Test 4 Complete!")


def test_5_logical_bug():
    """Test 5: Debug logical error."""
    print_header("TEST 5: Logical Bug")
    
    code = """
def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

data = []
avg = calculate_average(data)
print(f"Average: {avg}")
"""
    
    print("Buggy Code:")
    print(code)
    
    debugger = BugDebugger()
    result = debugger.debug(code)
    
    print(f"\n🐛 Bugs Found: {len(result['bugs_found'])}")
    for i, bug in enumerate(result['bugs_found'], 1):
        print(f"\n{i}. {bug['message']}")
        print(f"   Line: {bug['line']}")
        print(f"   Category: {bug['category']}")
        print(f"   Severity: {bug['severity']}")
    
    print(f"\n🔧 Complete Fix Steps:")
    for fix_group in result['fix_steps']:
        print(f"\nBug #{fix_group['bug_number']}: {fix_group['bug']}")
        for j, step in enumerate(fix_group['steps'], 1):
            print(f"  Step {j}: {step}")
    
    print(f"\n💡 Prevention Strategy:")
    for tip in result['prevention_tips']:
        print(f"  • {tip['tip']}")
    
    print("\n✅ Test 5 Complete!")


def test_6_multiple_bugs():
    """Test 6: Code with multiple bugs."""
    print_header("TEST 6: Multiple Bugs")
    
    code = """
def process_data(data):
    results = []
    for i in range(len(data) + 1):
        results.append(data[i] * 2)
    return results

def save_results(filename, data):
    file = open(filename, 'w')
    file.write(str(data))
    # File not closed!

numbers = [1, 2, 3]
processed = process_data(numbers)
save_results('output.txt', processed)
"""
    
    print("Buggy Code:")
    print(code[:150] + "...")
    
    debugger = BugDebugger()
    result = debugger.debug(code)
    
    print(f"\n🐛 Total Bugs Found: {len(result['bugs_found'])}")
    print(f"\n📊 Bug Categories:")
    categories = {}
    for bug in result['bugs_found']:
        cat = bug['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in categories.items():
        print(f"  • {category}: {count}")
    
    print(f"\n🔧 Top 3 Fixes:")
    for fix in result['fix_steps'][:3]:
        print(f"\n{fix['bug_number']}. {fix['bug']} (Line {fix['line']})")
        print(f"   Steps: {len(fix['steps'])} steps to fix")
    
    print(f"\n💡 Prevention Tips ({len(result['prevention_tips'])}):")
    for tip in result['prevention_tips'][:3]:
        print(f"  • {tip['tip']}")
    
    print(f"\n🧪 Test Suggestions:")
    for test in result['test_suggestions'][:3]:
        print(f"  • {test}")
    
    print("\n✅ Test 6 Complete!")


def test_comparison():
    """Test 7: Compare debugging different error types."""
    print_header("TEST 7: Error Type Comparison")
    
    test_cases = [
        ("Division by Zero", "def f(x): return 10/x\nf(0)", "ZeroDivisionError"),
        ("Index Error", "x=[1,2,3]\nprint(x[10])", "IndexError"),
        ("Name Error", "print(undefined_var)", "NameError"),
    ]
    
    debugger = BugDebugger()
    
    for name, code, error_type in test_cases:
        result = debugger.debug(code)
        bugs_count = len(result['bugs_found'])
        
        print(f"\n{name}:")
        print(f"  Code: {code[:40]}...")
        print(f"  Bugs Found: {bugs_count}")
        if result['bugs_found']:
            print(f"  Category: {result['bugs_found'][0]['category']}")
            print(f"  Severity: {result['bugs_found'][0]['severity']}")
    
    print("\n✅ Test 7 Complete!")


def run_all_tests():
    """Run all debugger tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "BUG DEBUGGER TESTS" + " "*29 + "║")
    print("║" + " "*23 + "Day 11-14 Feature" + " "*28 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Division by Zero", test_1_division_by_zero),
        ("Index Out of Range", test_2_index_out_of_range),
        ("Undefined Variable", test_3_undefined_variable),
        ("Type Error", test_4_type_error),
        ("Logical Bug", test_5_logical_bug),
        ("Multiple Bugs", test_6_multiple_bugs),
        ("Error Comparison", test_comparison),
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
        print("\n🎉 All tests passed! Bug Debugger is working perfectly!")
    
    print("\n📋 Next Steps:")
    print("1. Start API server: uvicorn src.api.main:app --reload")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Try the /debug endpoint with buggy code")
    print("4. Test /debug/quick for fast bug detection")
    print("5. Try /debug/fix to get corrected code")
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