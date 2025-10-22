# src/tests/test_10_samples.py

"""
10 Sample Tests - Day 6-7 Task
================================
Test the analyzer with 10 different code samples.

Run with: python src/tests/test_10_samples.py

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

from src.core.orchestrator import CodeAnalysisOrchestrator
import time


# 10 Test Samples
SAMPLES = {
    "1_division_by_zero": """
def divide(a, b):
    return a / b

result = divide(10, 0)
print(result)
""",
    
    "2_sql_injection": """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

user = get_user(request.args.get('id'))
""",
    
    "3_index_out_of_range": """
numbers = [1, 2, 3, 4, 5]
for i in range(10):
    print(numbers[i])
""",
    
    "4_unused_variables": """
def calculate(a, b):
    x = a + b
    y = a * b
    z = a - b
    w = a / b
    return x
""",
    
    "5_file_not_closed": """
def read_config():
    file = open('config.txt', 'r')
    content = file.read()
    return content
""",
    
    "6_hardcoded_secrets": """
DATABASE_URL = "postgresql://user:password123@localhost/db"
API_KEY = "sk_test_abc123xyz"
SECRET_TOKEN = "my_secret_token"

def connect():
    return connect_db(DATABASE_URL, API_KEY)
""",
    
    "7_infinite_recursion": """
def factorial(n):
    return n * factorial(n - 1)

result = factorial(5)
""",
    
    "8_type_confusion": """
def add_numbers(a, b):
    return a + b

result1 = add_numbers(5, 3)
result2 = add_numbers("5", "3")
print(result1, result2)
""",
    
    "9_missing_error_handling": """
import json

def load_data(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

config = load_data('config.json')
""",
    
    "10_clean_code": """
def calculate_average(numbers: list) -> float:
    \"\"\"Calculate average of numbers.\"\"\"
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

def main():
    data = [1, 2, 3, 4, 5]
    avg = calculate_average(data)
    print(f"Average: {avg:.2f}")

if __name__ == "__main__":
    main()
"""
}


def test_sample(name, code, orchestrator):
    """Test a single code sample."""
    print("\n" + "="*70)
    print(f"  SAMPLE: {name}")
    print("="*70)
    
    print("\nCode:")
    print("-" * 70)
    print(code.strip())
    print("-" * 70)
    
    # Analyze
    start = time.time()
    result = orchestrator.analyze(code, use_llm=False)  # Static only for speed
    duration = time.time() - start
    
    # Display results
    summary = result['summary']
    print(f"\n📊 Results:")
    print(f"   Total Issues: {summary['total']}")
    print(f"   Critical: {summary['by_severity']['critical']}")
    print(f"   Medium: {summary['by_severity']['medium']}")
    print(f"   Low: {summary['by_severity']['low']}")
    print(f"   Analysis Time: {duration:.2f}s")
    
    # Show categories
    if summary['total'] > 0:
        print(f"\n   Issues by Category:")
        for category, count in summary['by_category'].items():
            if count > 0:
                print(f"      {category}: {count}")
    
    # Show top 3 issues
    if result['issues']:
        print(f"\n   Top Issues:")
        for i, issue in enumerate(result['issues'][:3], 1):
            severity_emoji = {
                'critical': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(issue['severity'], '⚪')
            
            print(f"      {i}. {severity_emoji} Line {issue['line']}: {issue['message'][:60]}...")
    else:
        print(f"\n   ✅ No issues found! Clean code!")
    
    return result


def main():
    """Run all 10 samples."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "DAY 6-7: 10 SAMPLE TESTS" + " "*23 + "║")
    print("╚" + "="*68 + "╝")
    
    # Initialize orchestrator
    print("\n🎭 Initializing CodeSensei...")
    orchestrator = CodeAnalysisOrchestrator()
    print("✅ Ready!\n")
    
    # Track results
    results = {}
    total_issues = 0
    total_time = 0
    
    # Test each sample
    for name, code in SAMPLES.items():
        try:
            result = test_sample(name, code, orchestrator)
            results[name] = {
                'success': True,
                'issues': len(result['issues']),
                'critical': result['summary']['by_severity']['critical'],
                'time': result['metadata']['execution_time']
            }
            total_issues += len(result['issues'])
            total_time += result['metadata']['execution_time']
            
        except Exception as e:
            print(f"\n❌ Error analyzing {name}: {e}")
            results[name] = {
                'success': False,
                'error': str(e)
            }
    
    # Final Summary
    print("\n" + "="*70)
    print("  📊 FINAL SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r['success'])
    
    print(f"\n✅ Tests Passed: {passed}/10")
    print(f"📝 Total Issues Found: {total_issues}")
    print(f"⏱️  Total Analysis Time: {total_time:.2f}s")
    print(f"⚡ Average Time per Sample: {total_time/10:.2f}s")
    
    # Show summary table
    print(f"\n📋 Detailed Results:")
    print(f"{'Sample':<25} {'Issues':<10} {'Critical':<10} {'Status'}")
    print("-" * 70)
    
    for name, result in results.items():
        if result['success']:
            status = "✅ PASS"
            issues = result['issues']
            critical = result['critical']
        else:
            status = "❌ FAIL"
            issues = "N/A"
            critical = "N/A"
        
        print(f"{name:<25} {str(issues):<10} {str(critical):<10} {status}")
    
    # Recommendations
    print("\n" + "="*70)
    print("  💡 RECOMMENDATIONS")
    print("="*70)
    
    critical_count = sum(r.get('critical', 0) for r in results.values() if r['success'])
    
    if critical_count > 0:
        print(f"\n⚠️  Found {critical_count} critical issues across samples")
        print("   These should be fixed immediately in production code!")
    
    if passed == 10:
        print("\n🎉 All 10 samples analyzed successfully!")
        print("   CodeSensei is working perfectly!")
    else:
        print(f"\n⚠️  {10-passed} samples failed to analyze")
        print("   Review errors above and fix issues")
    
    print("\n✅ Day 6-7 testing complete!")
    print("\nNext steps:")
    print("1. Review the issues found")
    print("2. Fix any bugs in the analyzer")
    print("3. Test with LLM: Set use_llm=True in code")
    print("4. Start API server: uvicorn src.api.main:app --reload")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted")
    except Exception as e:
        print(("\n❌ Fatal error: {e}"))
        import traceback
        traceback.print_exc()