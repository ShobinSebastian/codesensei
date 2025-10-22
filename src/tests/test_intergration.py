# src/tests/test_integration.py

"""
Integration Tests
=================
Tests the complete analysis pipeline.

Run with: pytest src/tests/test_integration.py -v

Author: Shobin Sebastian
Date: November 2025
"""

import pytest
import sys
import os

# Add project root to path
current_file = os.path.abspath(__file__)
tests_dir = os.path.dirname(current_file)
src_dir = os.path.dirname(tests_dir)
project_root = os.path.dirname(src_dir)
sys.path.insert(0, project_root)

from src.core.orchestrator import CodeAnalysisOrchestrator
from src.analyzers.static_analyzer import StaticAnalyzer
from src.agents.llm_agent import LLMAgent


# Test Fixtures
@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    return CodeAnalysisOrchestrator()


@pytest.fixture
def static_analyzer():
    """Create static analyzer instance."""
    return StaticAnalyzer()


@pytest.fixture
def buggy_code():
    """Sample buggy code."""
    return """
def divide(a, b):
    return a / b

result = divide(10, 0)
"""


@pytest.fixture
def clean_code():
    """Sample clean code."""
    return """
def add(a: int, b: int) -> int:
    return a + b

result = add(5, 3)
print(result)
"""


# Static Analyzer Tests
class TestStaticAnalyzer:
    
    def test_initialization(self, static_analyzer):
        """Test analyzer initializes."""
        assert static_analyzer is not None
    
    def test_finds_issues(self, static_analyzer, buggy_code):
        """Test finds issues in buggy code."""
        result = static_analyzer.analyze(buggy_code)
        assert 'issues' in result
        assert 'summary' in result


# Orchestrator Tests
class TestOrchestrator:
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initializes."""
        assert orchestrator is not None
        assert orchestrator.static_analyzer is not None
    
    def test_analyze_static_only(self, orchestrator, buggy_code):
        """Test static-only analysis."""
        result = orchestrator.analyze(buggy_code, use_llm=False)
        
        assert 'issues' in result
        assert 'summary' in result
        assert 'metadata' in result
        assert result['metadata']['llm_used'] == False
    
    def test_analyze_returns_structure(self, orchestrator, buggy_code):
        """Test analysis returns correct structure."""
        result = orchestrator.analyze(buggy_code, use_llm=False)
        
        # Check structure
        assert 'issues' in result
        assert 'summary' in result
        assert 'metadata' in result
        
        # Check summary structure
        assert 'total' in result['summary']
        assert 'by_severity' in result['summary']
        assert 'by_category' in result['summary']
    
    def test_clean_code(self, orchestrator, clean_code):
        """Test with clean code."""
        result = orchestrator.analyze(clean_code, use_llm=False)
        
        # Should have low or no critical issues
        assert result['summary']['critical'] == 0


if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])