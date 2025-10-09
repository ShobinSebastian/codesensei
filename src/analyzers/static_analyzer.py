# src/analyzers/static_analyzer.py

"""
Static Code Analyzer
====================
This module analyzes Python code using multiple static analysis tools:
- pylint: Finds code quality issues, bugs, and style problems
- bandit: Finds security vulnerabilities
- radon: Measures code complexity

Author: Your Name
Date: November 2025
"""

import ast
import tempfile
import os
from typing import List, Dict, Any
from pylint import lint
from pylint.reporters.text import TextReporter
import io
import subprocess
import json


class StaticAnalyzer:
    """
    A class that performs static analysis on Python code.
    
    Static analysis = analyzing code WITHOUT running it.
    Like a spell-checker for code!
    """
    
    def __init__(self):
        """
        Initialize the static analyzer.
        
        We set up severity levels to categorize issues:
        - critical: Must fix (security holes, critical bugs)
        - medium: Should fix (bad practices, potential bugs)
        - low: Nice to fix (style issues, minor improvements)
        """
        self.severity_mapping = {
            'error': 'critical',      # Pylint errors = critical
            'warning': 'medium',      # Pylint warnings = medium
            'HIGH': 'critical',       # Bandit HIGH = critical
            'MEDIUM': 'medium',       # Bandit MEDIUM = medium
            'LOW': 'low'              # Bandit LOW = low
        }
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Main function to analyze code.
        
        Args:
            code (str): The Python code to analyze (as a string)
            
        Returns:
            Dict containing:
                - issues: List of problems found
                - summary: Statistics about the analysis
        
        Example:
            analyzer = StaticAnalyzer()
            result = analyzer.analyze("print('hello')")
        """
        print("🔍 Starting static analysis...")
        
        # Step 1: Check if code is valid Python syntax
        syntax_issues = self._check_syntax(code)
        if syntax_issues:
            # If syntax is broken, return immediately
            # (no point analyzing invalid code!)
            return {
                'issues': syntax_issues,
                'summary': {
                    'total': len(syntax_issues),
                    'critical': len(syntax_issues),
                    'medium': 0,
                    'low': 0
                }
            }
        
        # Step 2: Run pylint (finds bugs and style issues)
        print("  ✓ Running pylint...")
        pylint_issues = self._run_pylint(code)
        
        # Step 3: Run bandit (finds security issues)
        print("  ✓ Running bandit...")
        bandit_issues = self._run_bandit(code)
        
        # Step 4: Combine all issues
        all_issues = pylint_issues + bandit_issues
        
        # Step 5: Remove duplicates (sometimes tools find same issue)
        unique_issues = self._deduplicate_issues(all_issues)
        
        # Step 6: Sort by severity (critical first)
        sorted_issues = self._sort_by_severity(unique_issues)
        
        # Step 7: Create summary statistics
        summary = self._create_summary(sorted_issues)
        
        print(f"  ✓ Analysis complete! Found {len(sorted_issues)} issues.")
        
        return {
            'issues': sorted_issues,
            'summary': summary
        }
    
    def _check_syntax(self, code: str) -> List[Dict]:
        """
        Check if Python code has syntax errors.
        
        Uses Python's built-in ast (Abstract Syntax Tree) module.
        AST = Internal representation of code structure.
        
        Args:
            code: Python code string
            
        Returns:
            List of syntax error issues (empty if no errors)
        """
        try:
            # Try to parse the code into AST
            ast.parse(code)
            return []  # No syntax errors!
            
        except SyntaxError as e:
            # Syntax error found!
            return [{
                'type': 'syntax_error',
                'severity': 'critical',
                'line': e.lineno,  # Which line has the error
                'message': f"Syntax Error: {e.msg}",
                'explanation': "Python can't understand this code. Fix syntax first!",
                'code_snippet': e.text.strip() if e.text else "N/A"
            }]
    
    def _run_pylint(self, code: str) -> List[Dict]:
        """
        Run pylint to find code quality issues.
        
        Pylint checks for:
        - Bugs (like using undefined variables)
        - Bad practices (like unused variables)
        - Style issues (like bad naming)
        
        How it works:
        1. Save code to temporary file (pylint needs a file)
        2. Run pylint on that file
        3. Parse pylint's output
        4. Delete temporary file
        5. Return structured issues
        """
        issues = []
        
        # Create temporary file to store code
        # (We use tempfile so file is automatically cleaned up)
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',  # Must end with .py for pylint
            delete=False    # Don't delete yet, we need the path
        ) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name
        
        try:
            # Capture pylint output
            pylint_output = io.StringIO()
            reporter = TextReporter(pylint_output)
            
            # Run pylint with specific checks
            # We disable some noisy checks for better signal-to-noise
            lint.Run(
                [
                    temp_path,
                    '--disable=C0111,C0103',  # Disable docstring and naming warnings (too strict for learning)
                    '--reports=n',             # No detailed reports (just the issues)
                    '--score=n'                # No score (we calculate our own)
                ],
                reporter=reporter,
                exit=False  # Don't exit Python when pylint finishes
            )
            
            # Get pylint's output
            output = pylint_output.getvalue()
            
            # Parse each line of output
            for line in output.split('\n'):
                if ':' not in line:
                    continue  # Skip non-issue lines
                
                # Pylint format: "filename:line:column: type: message"
                parts = line.split(':', 4)
                if len(parts) >= 5:
                    try:
                        line_num = int(parts[1].strip())
                        issue_type = parts[3].strip()
                        message = parts[4].strip()
                        
                        # Map pylint type to our severity
                        severity = self.severity_mapping.get(
                            issue_type.lower(), 
                            'low'
                        )
                        
                        issues.append({
                            'type': 'code_quality',
                            'severity': severity,
                            'line': line_num,
                            'message': message,
                            'tool': 'pylint',
                            'explanation': self._explain_pylint_issue(message)
                        })
                    except (ValueError, IndexError):
                        continue  # Skip malformed lines
            
        finally:
            # Clean up: delete temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return issues
    
    def _run_bandit(self, code: str) -> List[Dict]:
        """
        Run bandit to find security vulnerabilities.
        
        Bandit checks for:
        - SQL injection risks
        - Hardcoded passwords
        - Use of unsafe functions
        - Insecure configurations
        
        Example issues it finds:
        - Using eval() (can execute malicious code)
        - SQL queries with string formatting
        - Weak cryptography
        """
        issues = []
        
        # Create temporary file for bandit
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name
        
        try:
            # Run bandit as subprocess (external command)
            # -f json: Output in JSON format (easy to parse)
            result = subprocess.run(
                ['bandit', '-f', 'json', temp_path],
                capture_output=True,  # Capture stdout and stderr
                text=True,            # Return as string, not bytes
                timeout=10            # Kill if takes >10 seconds
            )
            
            # Bandit returns JSON output
            if result.stdout:
                try:
                    bandit_data = json.loads(result.stdout)
                    
                    # Parse each issue from bandit
                    for item in bandit_data.get('results', []):
                        issues.append({
                            'type': 'security',
                            'severity': self.severity_mapping.get(
                                item['issue_severity'], 
                                'medium'
                            ),
                            'line': item['line_number'],
                            'message': item['issue_text'],
                            'tool': 'bandit',
                            'explanation': self._explain_security_issue(item),
                            'confidence': item.get('issue_confidence', 'MEDIUM')
                        })
                except json.JSONDecodeError:
                    # If JSON parsing fails, skip bandit results
                    pass
        
        except subprocess.TimeoutExpired:
            # Bandit took too long
            print("  ⚠ Bandit timed out (code too complex)")
        
        except FileNotFoundError:
            # Bandit not installed (should not happen, we installed it)
            print("  ⚠ Bandit not found (check installation)")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return issues
    
    def _deduplicate_issues(self, issues: List[Dict]) -> List[Dict]:
        """
        Remove duplicate issues.
        
        Sometimes pylint and bandit find the same problem.
        We keep only one copy.
        
        Two issues are "same" if they:
        - Are on the same line
        - Have similar messages
        """
        seen = set()
        unique = []
        
        for issue in issues:
            # Create unique key: line number + first 50 chars of message
            key = (
                issue['line'],
                issue['message'][:50].lower()
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(issue)
        
        return unique
    
    def _sort_by_severity(self, issues: List[Dict]) -> List[Dict]:
        """
        Sort issues by severity.
        
        Order: critical → medium → low
        
        Why? User should see critical issues first!
        """
        severity_order = {
            'critical': 0,
            'medium': 1,
            'low': 2
        }
        
        return sorted(
            issues,
            key=lambda x: severity_order.get(x['severity'], 3)
        )
    
    def _create_summary(self, issues: List[Dict]) -> Dict[str, int]:
        """
        Create summary statistics.
        
        Counts how many issues of each severity.
        """
        summary = {
            'total': len(issues),
            'critical': 0,
            'medium': 0,
            'low': 0
        }
        
        for issue in issues:
            severity = issue['severity']
            if severity in summary:
                summary[severity] += 1
        
        return summary
    
    def _explain_pylint_issue(self, message: str) -> str:
        """
        Add human-friendly explanation to pylint messages.
        
        Pylint messages can be cryptic (like "E1101").
        We add simple explanations.
        """
        explanations = {
            'undefined': "You're using a variable that doesn't exist yet.",
            'unused': "You created a variable but never used it.",
            'import': "Problem with how you're importing modules.",
            'redefined': "You're defining the same thing twice.",
            'no-member': "Trying to use something that doesn't exist in this object."
        }
        
        # Check if any keyword matches
        for keyword, explanation in explanations.items():
            if keyword in message.lower():
                return explanation
        
        return "Code quality issue detected by pylint."
    
    def _explain_security_issue(self, item: Dict) -> str:
        """
        Add context to security issues from bandit.
        
        Security issues need clear explanations of:
        - What's wrong
        - Why it's dangerous
        - How to fix
        """
        test_id = item.get('test_id', '')
        
        explanations = {
            'B608': "SQL injection risk! Never put user input directly in SQL queries.",
            'B201': "Using eval() is dangerous - it can run malicious code.",
            'B303': "Weak cryptography detected. Use stronger algorithms.",
            'B105': "Hardcoded password found. Store secrets in environment variables.",
        }
        
        return explanations.get(
            test_id,
            f"Security issue: {item['issue_text']}"
        )


# Example usage (this runs when you execute this file directly)
if __name__ == "__main__":
    # Test the analyzer with sample code
    
    test_code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

x = 10
y = 20
print(x)
"""
    
    analyzer = StaticAnalyzer()
    result = analyzer.analyze(test_code)
    
    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)
    
    print(f"\nSummary:")
    print(f"  Total issues: {result['summary']['total']}")
    print(f"  Critical: {result['summary']['critical']}")
    print(f"  Medium: {result['summary']['medium']}")
    print(f"  Low: {result['summary']['low']}")
    
    print(f"\nDetailed Issues:")
    for i, issue in enumerate(result['issues'], 1):
        print(f"\n{i}. [{issue['severity'].upper()}] Line {issue['line']}")
        print(f"   {issue['message']}")
        print(f"   → {issue['explanation']}")