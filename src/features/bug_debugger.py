# src/features/bug_debugger.py

"""
Bug Debugger Feature
====================
Intelligent debugging assistant that helps fix bugs step-by-step.

Features:
- Detects bugs using static analysis + LLM
- Provides root cause analysis
- Generates step-by-step fix instructions
- Shows before/after code examples
- Suggests prevention strategies
- Interactive debugging mode

Author: Shobin Sebastian
Date: November 2025
"""

from typing import Dict, List, Any, Optional
from src.analyzers.static_analyzer import StaticAnalyzer
from src.agents.llm_agent import LLMAgent
import re


class BugDebugger:
    """
    Intelligent bug debugging assistant.
    
    Helps developers understand and fix bugs with detailed guidance.
    """
    
    def __init__(
        self, 
        static_analyzer: Optional[StaticAnalyzer] = None,
        llm_agent: Optional[LLMAgent] = None
    ):
        """
        Initialize bug debugger.
        
        Args:
            static_analyzer: Static analyzer instance
            llm_agent: LLM agent instance
        """
        self.static_analyzer = static_analyzer or StaticAnalyzer()
        self.llm_agent = llm_agent or LLMAgent()
        print("🐛 Bug Debugger initialized")
    
    def debug(self, code: str, error_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive debugging analysis.
        
        Args:
            code: Buggy Python code
            error_message: Optional error message from running the code
            
        Returns:
            Complete debug report with:
                - bugs_found: List of detected bugs
                - root_causes: Analysis of why bugs occurred
                - fix_steps: Step-by-step instructions
                - fixed_code: Corrected version
                - prevention: How to avoid similar bugs
                - test_suggestions: How to test the fix
        """
        print(f"🔍 Debugging code...")
        
        result = {
            'bugs_found': [],
            'root_causes': [],
            'fix_steps': [],
            'fixed_code': '',
            'prevention_tips': [],
            'test_suggestions': [],
            'metadata': {}
        }
        
        # Step 1: Detect bugs
        result['bugs_found'] = self._detect_bugs(code, error_message)
        print(f"  ✓ Found {len(result['bugs_found'])} bug(s)")
        
        if not result['bugs_found']:
            result['metadata']['status'] = 'no_bugs_detected'
            return result
        
        # Step 2: Analyze root causes
        result['root_causes'] = self._analyze_root_causes(
            code, 
            result['bugs_found']
        )
        print(f"  ✓ Analyzed root causes")
        
        # Step 3: Generate fix steps
        result['fix_steps'] = self._generate_fix_steps(
            code,
            result['bugs_found']
        )
        print(f"  ✓ Generated fix steps")
        
        # Step 4: Create fixed code
        result['fixed_code'] = self._generate_fixed_code(
            code,
            result['bugs_found']
        )
        print(f"  ✓ Generated fixed code")
        
        # Step 5: Prevention strategies
        result['prevention_tips'] = self._generate_prevention_tips(
            result['bugs_found']
        )
        print(f"  ✓ Created prevention tips")
        
        # Step 6: Test suggestions
        result['test_suggestions'] = self._generate_test_suggestions(
            code,
            result['bugs_found']
        )
        print(f"  ✓ Generated test suggestions")
        
        # Metadata
        result['metadata'] = {
            'status': 'bugs_found',
            'bug_count': len(result['bugs_found']),
            'severity_breakdown': self._get_severity_breakdown(result['bugs_found']),
            'fixable': all(bug.get('fixable', True) for bug in result['bugs_found'])
        }
        
        print("✅ Debug analysis complete!")
        return result
    
    def _detect_bugs(self, code: str, error_message: Optional[str]) -> List[Dict]:
        """
        Detect bugs using static analysis + LLM.
        
        Combines results from both tools.
        """
        bugs = []
        
        # Get static analysis issues (only critical/medium)
        static_result = self.static_analyzer.analyze(code)
        for issue in static_result['issues']:
            if issue['severity'] in ['critical', 'medium']:
                bugs.append({
                    'type': issue['type'],
                    'severity': issue['severity'],
                    'line': issue['line'],
                    'message': issue['message'],
                    'category': self._categorize_bug(issue),
                    'source': 'static_analysis'
                })
        
        # If error message provided, analyze it with LLM
        if error_message:
            llm_bugs = self._analyze_error_with_llm(code, error_message)
            bugs.extend(llm_bugs)
        
        # Use LLM to find logical bugs
        logical_bugs = self._find_logical_bugs(code)
        bugs.extend(logical_bugs)
        
        return self._deduplicate_bugs(bugs)
    
    def _categorize_bug(self, issue: Dict) -> str:
        """Categorize bug into specific types."""
        message = issue.get('message', '').lower()
        
        categories = {
            'index_error': ['index', 'out of range', 'list index'],
            'type_error': ['type', 'cannot', 'unsupported'],
            'value_error': ['value', 'invalid'],
            'name_error': ['undefined', 'not defined', 'name'],
            'zero_division': ['division', 'zero', 'divide by zero'],
            'logic_error': ['logic', 'incorrect', 'wrong result'],
            'security': ['security', 'sql', 'injection', 'password'],
            'resource_leak': ['file', 'not closed', 'resource'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in message for keyword in keywords):
                return category
        
        return 'general_bug'
    
    def _analyze_error_with_llm(self, code: str, error_message: str) -> List[Dict]:
        """Use LLM to analyze a runtime error."""
        prompt = f"""Analyze this Python error and identify the exact bug.

Code:
```python
{code}
```

Error:
{error_message}

Provide a JSON response with:
- line: line number where bug occurs
- category: type of bug (e.g., "index_error", "type_error")
- message: brief description
- severity: "critical" or "medium"

Response format:
{{"line": 5, "category": "index_error", "message": "List index out of range", "severity": "critical"}}
"""
        
        try:
            response = self.llm_agent._call_llm(prompt)
            # Parse JSON from response
            import json
            bug_data = json.loads(response)
            
            return [{
                'type': 'runtime_error',
                'severity': bug_data.get('severity', 'critical'),
                'line': bug_data.get('line', 0),
                'message': bug_data.get('message', 'Runtime error'),
                'category': bug_data.get('category', 'general_bug'),
                'source': 'llm_error_analysis'
            }]
        except:
            return []
    
    def _find_logical_bugs(self, code: str) -> List[Dict]:
        """Use LLM to find logical bugs that static tools miss."""
        prompt = f"""Find logical bugs in this Python code.
Focus on: incorrect logic, edge cases not handled, algorithmic errors.

Code:
```python
{code}
```

Return a JSON array of bugs found:
[
  {{
    "line": 5,
    "category": "logic_error",
    "message": "Brief description",
    "severity": "medium"
  }}
]

If no logical bugs found, return: []
"""
        
        try:
            response = self.llm_agent._call_llm(prompt)
            import json
            
            # Extract JSON from response
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_text = response[json_start:json_end].strip()
            elif '[' in response:
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                json_text = response[json_start:json_end]
            else:
                return []
            
            bugs_data = json.loads(json_text)
            
            return [{
                'type': 'logic_error',
                'severity': bug.get('severity', 'medium'),
                'line': bug.get('line', 0),
                'message': bug.get('message', 'Logical error'),
                'category': bug.get('category', 'logic_error'),
                'source': 'llm_logic_analysis'
            } for bug in bugs_data]
            
        except Exception as e:
            print(f"  ⚠ LLM logical analysis failed: {e}")
            return []
    
    def _deduplicate_bugs(self, bugs: List[Dict]) -> List[Dict]:
        """Remove duplicate bug reports."""
        seen = set()
        unique = []
        
        for bug in bugs:
            key = (bug['line'], bug['category'], bug['message'][:50])
            if key not in seen:
                seen.add(key)
                unique.append(bug)
        
        return unique
    
    def _analyze_root_causes(self, code: str, bugs: List[Dict]) -> List[Dict]:
        """Analyze why bugs occurred (root cause analysis)."""
        root_causes = []
        
        for bug in bugs[:3]:  # Analyze top 3 bugs
            prompt = f"""Explain the ROOT CAUSE of this bug in simple terms.

Code:
```python
{code}
```

Bug: {bug['message']} on line {bug['line']}
Category: {bug['category']}

Explain:
1. WHY this bug occurs (root cause)
2. WHAT happens when code runs
3. WHEN this becomes a problem

Keep it simple and educational.
"""
            
            try:
                explanation = self.llm_agent._call_llm(prompt)
                root_causes.append({
                    'bug': bug['message'],
                    'line': bug['line'],
                    'explanation': explanation.strip()
                })
            except:
                root_causes.append({
                    'bug': bug['message'],
                    'line': bug['line'],
                    'explanation': f"Bug on line {bug['line']}: {bug['message']}"
                })
        
        return root_causes
    
    def _generate_fix_steps(self, code: str, bugs: List[Dict]) -> List[Dict]:
        """Generate step-by-step fix instructions."""
        fix_steps = []
        
        for i, bug in enumerate(bugs[:3], 1):  # Top 3 bugs
            prompt = f"""Provide step-by-step instructions to fix this bug.

Code:
```python
{code}
```

Bug: {bug['message']} on line {bug['line']}

Provide 3-5 clear steps to fix it:
1. Step one...
2. Step two...
etc.

Be specific and actionable.
"""
            
            try:
                response = self.llm_agent._call_llm(prompt)
                
                # Extract steps from response
                steps = []
                for line in response.split('\n'):
                    line = line.strip()
                    if re.match(r'^\d+\.', line):  # Starts with number
                        steps.append(line[line.find('.')+1:].strip())
                
                fix_steps.append({
                    'bug_number': i,
                    'bug': bug['message'],
                    'line': bug['line'],
                    'steps': steps if steps else [response[:200]]
                })
            except:
                fix_steps.append({
                    'bug_number': i,
                    'bug': bug['message'],
                    'line': bug['line'],
                    'steps': [f"Review and fix line {bug['line']}"]
                })
        
        return fix_steps
    
    def _generate_fixed_code(self, code: str, bugs: List[Dict]) -> str:
        """Generate corrected version of code."""
        if not bugs:
            return code
        
        # Get most critical bug
        critical_bugs = [b for b in bugs if b['severity'] == 'critical']
        target_bug = critical_bugs[0] if critical_bugs else bugs[0]
        
        prompt = f"""Fix this bug in the code and return the COMPLETE corrected code.

Original Code:
```python
{code}
```

Bug to fix: {target_bug['message']} on line {target_bug['line']}

Return ONLY the corrected Python code, no explanations.
Include all original code with the fix applied.
"""
        
        try:
            response = self.llm_agent._call_llm(prompt)
            
            # Extract code from response
            if '```python' in response:
                code_start = response.find('```python') + 9
                code_end = response.find('```', code_start)
                fixed_code = response[code_start:code_end].strip()
            elif '```' in response:
                code_start = response.find('```') + 3
                code_end = response.find('```', code_start)
                fixed_code = response[code_start:code_end].strip()
            else:
                # Take first code-like block
                lines = [l for l in response.split('\n') if l.strip()]
                fixed_code = '\n'.join(lines)
            
            return fixed_code if fixed_code else code
            
        except Exception as e:
            print(f"  ⚠ Could not generate fixed code: {e}")
            return code
    
    def _generate_prevention_tips(self, bugs: List[Dict]) -> List[Dict]:
        """Generate tips to prevent similar bugs in future."""
        tips = []
        
        # Category-specific prevention tips
        prevention_strategies = {
            'index_error': {
                'tip': 'Always check list length before accessing indices',
                'example': 'if i < len(my_list): ...',
                'best_practice': 'Use enumerate() or iterate directly over list'
            },
            'zero_division': {
                'tip': 'Check denominator is not zero before division',
                'example': 'if b != 0: result = a / b',
                'best_practice': 'Add input validation at function start'
            },
            'type_error': {
                'tip': 'Use type hints and validate input types',
                'example': 'def func(x: int) -> str: ...',
                'best_practice': 'Add type checking with isinstance()'
            },
            'name_error': {
                'tip': 'Define variables before using them',
                'example': 'x = 0  # Initialize before use',
                'best_practice': 'Use IDE that catches undefined variables'
            },
            'logic_error': {
                'tip': 'Test edge cases: empty input, negative numbers, etc.',
                'example': 'if not data: return default_value',
                'best_practice': 'Write unit tests for all functions'
            },
            'security': {
                'tip': 'Never trust user input, always validate and sanitize',
                'example': 'Use parameterized queries for SQL',
                'best_practice': 'Follow OWASP security guidelines'
            },
            'resource_leak': {
                'tip': 'Always close resources (files, connections)',
                'example': 'with open(file) as f: ...',
                'best_practice': 'Use context managers (with statement)'
            }
        }
        
        seen_categories = set()
        for bug in bugs:
            category = bug.get('category', 'general_bug')
            if category not in seen_categories and category in prevention_strategies:
                tips.append(prevention_strategies[category])
                seen_categories.add(category)
        
        return tips[:5]  # Top 5 tips
    
    def _generate_test_suggestions(self, code: str, bugs: List[Dict]) -> List[str]:
        """Suggest tests to verify the fix works."""
        suggestions = []
        
        for bug in bugs[:3]:
            category = bug.get('category', 'general_bug')
            
            if category == 'index_error':
                suggestions.append("Test with empty list: my_func([])")
                suggestions.append("Test with single item: my_func([1])")
            
            elif category == 'zero_division':
                suggestions.append("Test with zero divisor: divide(10, 0)")
                suggestions.append("Test with normal values: divide(10, 2)")
            
            elif category == 'type_error':
                suggestions.append("Test with wrong type: my_func('string')")
                suggestions.append("Test with correct type: my_func(42)")
            
            elif category == 'logic_error':
                suggestions.append("Test edge case: empty input")
                suggestions.append("Test boundary values: 0, -1, MAX_INT")
            
            else:
                suggestions.append(f"Add unit test for line {bug['line']}")
        
        return list(set(suggestions))[:5]  # Unique, top 5
    
    def _get_severity_breakdown(self, bugs: List[Dict]) -> Dict[str, int]:
        """Count bugs by severity."""
        breakdown = {'critical': 0, 'medium': 0, 'low': 0}
        for bug in bugs:
            severity = bug.get('severity', 'medium')
            if severity in breakdown:
                breakdown[severity] += 1
        return breakdown


# Example usage
if __name__ == "__main__":
    debugger = BugDebugger()
    
    # Test with buggy code
    buggy_code = """
def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

data = []
avg = calculate_average(data)
print(f"Average: {avg}")
"""
    
    result = debugger.debug(buggy_code)
    
    print("\n" + "="*70)
    print("BUG DEBUG REPORT")
    print("="*70)
    
    print(f"\n🐛 Bugs Found: {len(result['bugs_found'])}")
    for i, bug in enumerate(result['bugs_found'], 1):
        print(f"\n{i}. [{bug['severity'].upper()}] Line {bug['line']}")
        print(f"   {bug['message']}")
        print(f"   Category: {bug['category']}")
    
    print(f"\n🔍 Root Causes:")
    for cause in result['root_causes']:
        print(f"\nLine {cause['line']}: {cause['bug']}")
        print(f"{cause['explanation'][:150]}...")
    
    print(f"\n🔧 Fix Steps:")
    for fix in result['fix_steps']:
        print(f"\nBug #{fix['bug_number']}: {fix['bug']}")
        for i, step in enumerate(fix['steps'], 1):
            print(f"  {i}. {step}")
    
    print(f"\n✅ Fixed Code:")
    print(result['fixed_code'][:200] + "...")
    
    print(f"\n💡 Prevention Tips:")
    for tip in result['prevention_tips']:
        print(f"  • {tip['tip']}")
        print(f"    Example: {tip['example']}")