# tests/test_llm_agent.py

"""
Tests for LLM Agent
===================
Testing AI is tricky because responses vary.
We test for:
1. API connection works
2. Returns structured data
3. Finds obvious issues
"""

import pytest
from src.agents.llm_agent import LLMAgent
import os


class TestLLMAgent:
    """Test suite for LLM Agent"""
    
    def setup_method(self):
        """Run before each test"""
        # Check if API key is available
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY not set in environment")
        
        self.agent = LLMAgent()
    
    def test_agent_initialization(self):
        """Test: Agent initializes correctly"""
        assert self.agent is not None
        assert self.agent.client is not None
        assert self.agent.model == "mixtral-8x7b-32768"
    
    def test_analyzes_simple_code(self):
        """Test: Can analyze simple code without errors"""
        code = """
def add(a, b):
    return a + b

result = add(2, 3)
print(result)
"""
        issues = self.agent.analyze(code)
        
        # Should return a list (even if empty)
        assert isinstance(issues, list)
    
    def test_finds_division_by_zero(self):
        """Test: Finds obvious error (division by zero)"""
        code = """
def divide(a, b):
    return a / b

result = divide(10, 0)
"""
        issues = self.agent.analyze(code)
        
        # Should find at least one issue
        assert len(issues) > 0
        
        # Check if any issue mentions division or zero
        messages = ' '.join([
            str(issue.get('message', '')) + ' ' + 
            str(issue.get('explanation', ''))
            for issue in issues
        ]).lower()
        
        assert 'zero' in messages or 'division' in messages
    
    def test_finds_sql_injection(self):
        """Test: Finds security issue (SQL injection)"""
        code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query
"""
        issues = self.agent.analyze(code)
        
        # Should find security issue
        assert len(issues) > 0
        
        # Check if mentions SQL or injection
        messages = ' '.join([
            str(issue.get('message', '')) + ' ' + 
            str(issue.get('explanation', ''))
            for issue in issues
        ]).lower()
        
        assert 'sql' in messages or 'injection' in messages
    
    def test_handles_empty_code(self):
        """Test: Handles edge case (empty code)"""
        code = ""
        
        # Should not crash
        issues = self.agent.analyze(code)
        assert isinstance(issues, list)
    
    def test_explain_code(self):
        """Test: Can explain code"""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        explanation = self.agent.explain_code(code)
        
        # Should return non-empty string
        assert isinstance(explanation, str)
        assert len(explanation) > 50  # At least some explanation
        
        # Should mention key concepts
        explanation_lower = explanation.lower()
        assert 'recursion' in explanation_lower or 'factorial' in explanation_lower


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, '-v'])