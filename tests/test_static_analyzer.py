# tests/test_static_analyzer.py

"""
Tests for Static Analyzer
==========================
These tests verify our static analyzer works correctly.

Why test?
- Catch bugs early
- Verify features work
- Prevent regressions (breaking things when we add features)
"""

import pytest
from src.analyzers.static_analyzer import StaticAnalyzer


class TestStaticAnalyzer:
    """Test suite for StaticAnalyzer class"""
    
    def setup_method(self):
        """
        Run before each test.
        Creates a fresh analyzer for each test.
        """
        self.analyzer = StaticAnalyzer()
    
    def test_finds_syntax_error(self):
        """
        Test: Should detect syntax errors
        
        We give it invalid Python code.
        It should return a syntax error issue.
        """
        bad_code = """
def broken function():
    print("missing colon above!")
"""
        result = self.analyzer.analyze(bad_code)
        
        # Assert (verify) that:
        assert len(result['issues']) > 0, "Should find at least one issue"
        assert result['issues'][0]['type'] == 'syntax_error'
        assert result['summary']['critical'] > 0
    
    def test_finds_unused_variable(self):
        """
        Test: Should detect unused variables
        
        Variable 'y' is created but never used.
        Pylint should catch this.
        """
        code = """
x = 10
y = 20
print(x, y)
"""
        result = self.analyzer.analyze(code)
        
        # Check that 'unused' appears in one of the messages
        messages = [issue['message'].lower() for issue in result['issues']]
        assert any('unused' in msg for msg in messages)
    
    def test_finds_security_issue(self):
        """
        Test: Should detect SQL injection risk
        
        Using f-string in SQL query is dangerous.
        Bandit should catch this.
        """
        dangerous_code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query
"""
        result = self.analyzer.analyze(dangerous_code)
        
        # Should find security issue
        security_issues = [
            issue for issue in result['issues'] 
            if issue['type'] == 'security'
        ]
        assert len(security_issues) > 0, "Should find SQL injection risk"
    
    def test_handles_valid_code(self):
        """
        Test: Should handle clean code
        
        Perfect code should have very few (or zero) issues.
        """
        clean_code = """
def add_numbers(a, b):
    '''Add two numbers and return result'''
    return a + b

result = add_numbers(5, 3)
print(result)
"""
        result = self.analyzer.analyze(clean_code)
        
        # Clean code might have zero issues, or only minor style issues
        assert result['summary']['critical'] == 0, "No critical issues in clean code"
    
    def test_summary_counts_match(self):
        """
        Test: Summary counts should be accurate
        
        Total should equal sum of critical + medium + low
        """
        code = """
x = 10
y = 20
z = 30
print(x)
"""
        result = self.analyzer.analyze(code)
        
        summary = result['summary']
        total_counted = summary['critical'] + summary['medium'] + summary['low']
        
        assert summary['total'] == total_counted, "Summary counts should match"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, '-v'])  # -v = verbose output