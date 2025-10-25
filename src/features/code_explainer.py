# src/features/code_explainer.py

"""
Code Explainer Feature
=======================
Explains code in simple, beginner-friendly language.

This module:
- Generates plain English explanations
- Provides line-by-line breakdowns
- Identifies key programming concepts
- Suggests learning resources
- Calculates code complexity

Author: Shobin Sebastian
Date: November 2025
"""

import ast
import re
from typing import Dict, List, Any, Optional
from src.agents.llm_agent import LLMAgent
from radon.complexity import cc_visit
from radon.metrics import mi_visit


class CodeExplainer:
    """
    Explains code in beginner-friendly language.
    
    Uses LLM + static analysis to provide comprehensive explanations.
    """
    
    def __init__(self, llm_agent: Optional[LLMAgent] = None):
        """
        Initialize code explainer.
        
        Args:
            llm_agent: Optional LLM agent (creates new one if not provided)
        """
        self.llm_agent = llm_agent or LLMAgent()
        print("✅ Code Explainer initialized")
    
    def explain(self, code: str, detail_level: str = "medium") -> Dict[str, Any]:
        """
        Generate comprehensive code explanation.
        
        Args:
            code: Python code to explain
            detail_level: "basic", "medium", or "detailed"
            
        Returns:
            Dictionary with:
                - overview: High-level explanation
                - line_by_line: Line-by-line breakdown
                - concepts: Key concepts used
                - complexity: Complexity analysis
                - learning_path: Suggested topics to learn
        """
        print(f"📖 Explaining code (detail level: {detail_level})...")
        
        result = {
            'overview': '',
            'line_by_line': [],
            'concepts': [],
            'complexity': {},
            'learning_path': [],
            'metadata': {}
        }
        
        # Step 1: Generate overview explanation
        result['overview'] = self._generate_overview(code, detail_level)
        
        # Step 2: Line-by-line breakdown (if medium or detailed)
        if detail_level in ['medium', 'detailed']:
            result['line_by_line'] = self._generate_line_breakdown(code)
        
        # Step 3: Identify key concepts
        result['concepts'] = self._identify_concepts(code)
        
        # Step 4: Calculate complexity
        result['complexity'] = self._analyze_complexity(code)
        
        # Step 5: Generate learning path
        result['learning_path'] = self._generate_learning_path(
            result['concepts'], 
            result['complexity']
        )
        
        # Step 6: Add metadata
        result['metadata'] = {
            'lines_of_code': len(code.split('\n')),
            'detail_level': detail_level,
            'has_functions': self._has_functions(code),
            'has_classes': self._has_classes(code)
        }
        
        print("✅ Explanation complete!")
        return result
    
    def _generate_overview(self, code: str, detail_level: str) -> str:
        """
        Generate high-level explanation of what code does.
        
        Uses LLM to create beginner-friendly overview.
        """
        if detail_level == "basic":
            prompt = f"""Explain this Python code in ONE simple sentence.
Focus on WHAT it does, not HOW.

Code:
```python
{code}
```

Answer in one clear sentence."""
        
        elif detail_level == "medium":
            prompt = f"""Explain this Python code in 2-3 simple sentences.
Explain WHAT it does and WHY someone might use it.

Code:
```python
{code}
```

Keep it simple and beginner-friendly."""
        
        else:  # detailed
            prompt = f"""Provide a detailed but clear explanation of this Python code.

Code:
```python
{code}
```

Include:
1. What the code does (main purpose)
2. How it works (high-level approach)
3. Why this approach is used
4. Any important details a beginner should know

Keep language simple and avoid jargon."""
        
        try:
            explanation = self.llm_agent._call_llm(prompt)
            return explanation.strip()
        except Exception as e:
            return f"Could not generate explanation: {str(e)}"
    
    def _generate_line_breakdown(self, code: str) -> List[Dict[str, str]]:
        """
        Generate line-by-line explanation.
        
        Returns list of {line_number, code, explanation}
        """
        lines = code.split('\n')
        breakdown = []
        
        # Group lines into logical chunks (to avoid explaining blank lines)
        chunks = self._group_code_lines(lines)
        
        for chunk in chunks:
            start_line = chunk['start']
            end_line = chunk['end']
            chunk_code = '\n'.join(chunk['lines'])
            
            if not chunk_code.strip():
                continue
            
            # Ask LLM to explain this chunk
            prompt = f"""Explain this code snippet in ONE simple sentence:

```python
{chunk_code}
```

Be concise and beginner-friendly."""
            
            try:
                explanation = self.llm_agent._call_llm(prompt)
                
                breakdown.append({
                    'line_range': f"{start_line}-{end_line}" if start_line != end_line else str(start_line),
                    'code': chunk_code,
                    'explanation': explanation.strip()
                })
            except:
                breakdown.append({
                    'line_range': f"{start_line}-{end_line}",
                    'code': chunk_code,
                    'explanation': "Code snippet"
                })
        
        return breakdown
    
    def _group_code_lines(self, lines: List[str]) -> List[Dict]:
        """
        Group related lines of code together.
        
        Groups by:
        - Function definitions
        - Class definitions
        - Logical blocks (if/for/while)
        - Single statements
        """
        chunks = []
        current_chunk = []
        start_line = 1
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if current_chunk:
                    chunks.append({
                        'start': start_line,
                        'end': i - 1,
                        'lines': current_chunk
                    })
                    current_chunk = []
                continue
            
            # Start of function/class
            if stripped.startswith(('def ', 'class ')):
                if current_chunk:
                    chunks.append({
                        'start': start_line,
                        'end': i - 1,
                        'lines': current_chunk
                    })
                start_line = i
                current_chunk = [line]
            
            # Continuation of block
            elif line.startswith((' ', '\t')) and current_chunk:
                current_chunk.append(line)
            
            # New statement
            else:
                if current_chunk:
                    chunks.append({
                        'start': start_line,
                        'end': i - 1,
                        'lines': current_chunk
                    })
                start_line = i
                current_chunk = [line]
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'start': start_line,
                'end': len(lines),
                'lines': current_chunk
            })
        
        return chunks
    
    def _identify_concepts(self, code: str) -> List[Dict[str, str]]:
        """
        Identify key programming concepts used in code.
        
        Returns list of concepts with descriptions.
        """
        concepts = []
        
        # Concept patterns to look for
        patterns = {
            'Functions': r'def\s+\w+\s*\(',
            'Classes': r'class\s+\w+',
            'Loops (for)': r'for\s+\w+\s+in\s+',
            'Loops (while)': r'while\s+',
            'Conditionals (if)': r'if\s+',
            'List Comprehension': r'\[.*for.*in.*\]',
            'Dictionary': r'\{.*:.*\}',
            'Exception Handling': r'try:|except|finally:',
            'Imports': r'^import\s+|^from\s+.*import',
            'Recursion': None,  # Special check
            'Type Hints': r':\s*\w+\s*=|def.*->\s*\w+',
            'F-strings': r'f["\']',
            'List Operations': r'\.append\(|\.extend\(|\.pop\(',
            'String Methods': r'\.strip\(|\.split\(|\.join\(',
        }
        
        # Check each pattern
        for concept, pattern in patterns.items():
            if pattern and re.search(pattern, code, re.MULTILINE):
                concepts.append({
                    'name': concept,
                    'description': self._get_concept_description(concept)
                })
        
        # Special check for recursion
        if self._has_recursion(code):
            concepts.append({
                'name': 'Recursion',
                'description': 'Function that calls itself'
            })
        
        return concepts
    
    def _get_concept_description(self, concept: str) -> str:
        """Get beginner-friendly description of concept."""
        descriptions = {
            'Functions': 'Reusable blocks of code that perform specific tasks',
            'Classes': 'Templates for creating objects with data and behavior',
            'Loops (for)': 'Repeat actions for each item in a sequence',
            'Loops (while)': 'Repeat actions while a condition is true',
            'Conditionals (if)': 'Make decisions in code based on conditions',
            'List Comprehension': 'Concise way to create lists',
            'Dictionary': 'Store data as key-value pairs',
            'Exception Handling': 'Handle errors gracefully',
            'Imports': 'Use code from other modules',
            'Recursion': 'Function that calls itself',
            'Type Hints': 'Specify expected data types',
            'F-strings': 'Format strings with embedded expressions',
            'List Operations': 'Add, remove, or modify list elements',
            'String Methods': 'Transform and manipulate text',
        }
        return descriptions.get(concept, 'Programming concept')
    
    def _has_recursion(self, code: str) -> bool:
        """Check if code contains recursion."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    # Check if function calls itself
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                if child.func.id == func_name:
                                    return True
        except:
            pass
        return False
    
    def _has_functions(self, code: str) -> bool:
        """Check if code has functions."""
        return bool(re.search(r'def\s+\w+\s*\(', code))
    
    def _has_classes(self, code: str) -> bool:
        """Check if code has classes."""
        return bool(re.search(r'class\s+\w+', code))
    
    def _analyze_complexity(self, code: str) -> Dict[str, Any]:
        """
        Analyze code complexity using Radon.
        
        Returns complexity metrics and interpretation.
        """
        complexity = {
            'cyclomatic': 0,
            'maintainability': 0,
            'complexity_grade': 'A',
            'interpretation': ''
        }
        
        try:
            # Cyclomatic complexity
            cc_results = cc_visit(code)
            if cc_results:
                avg_complexity = sum(r.complexity for r in cc_results) / len(cc_results)
                complexity['cyclomatic'] = round(avg_complexity, 2)
                
                # Grade complexity
                if avg_complexity <= 5:
                    complexity['complexity_grade'] = 'A (Simple)'
                elif avg_complexity <= 10:
                    complexity['complexity_grade'] = 'B (Moderate)'
                elif avg_complexity <= 20:
                    complexity['complexity_grade'] = 'C (Complex)'
                else:
                    complexity['complexity_grade'] = 'D (Very Complex)'
            
            # Maintainability index
            mi_result = mi_visit(code, multi=True)
            if mi_result:
                complexity['maintainability'] = round(mi_result, 2)
            
            # Interpretation
            complexity['interpretation'] = self._interpret_complexity(
                complexity['cyclomatic'],
                complexity['maintainability']
            )
            
        except Exception as e:
            complexity['interpretation'] = f"Could not analyze: {str(e)}"
        
        return complexity
    
    def _interpret_complexity(self, cyclomatic: float, maintainability: float) -> str:
        """Generate human-readable complexity interpretation."""
        if cyclomatic <= 5 and maintainability >= 20:
            return "✅ This code is simple and easy to understand!"
        elif cyclomatic <= 10 and maintainability >= 10:
            return "👍 This code is reasonably clear and maintainable."
        elif cyclomatic <= 20:
            return "⚠️ This code is getting complex. Consider breaking it into smaller functions."
        else:
            return "🔴 This code is very complex! Refactoring recommended."
    
    def _generate_learning_path(
        self, 
        concepts: List[Dict], 
        complexity: Dict
    ) -> List[Dict[str, str]]:
        """
        Generate personalized learning path based on code.
        
        Suggests topics to study next.
        """
        learning_path = []
        
        # Extract concept names
        concept_names = [c['name'] for c in concepts]
        
        # Beginner concepts
        if 'Functions' in concept_names:
            learning_path.append({
                'topic': 'Function Parameters and Return Values',
                'why': 'Deepen your understanding of functions',
                'difficulty': 'Beginner'
            })
        
        if 'Loops (for)' in concept_names or 'Loops (while)' in concept_names:
            learning_path.append({
                'topic': 'Loop Control (break, continue)',
                'why': 'Master loop control flow',
                'difficulty': 'Beginner'
            })
        
        # Intermediate concepts
        if 'List Comprehension' in concept_names:
            learning_path.append({
                'topic': 'Generator Expressions',
                'why': 'Next step after list comprehensions',
                'difficulty': 'Intermediate'
            })
        
        if 'Classes' in concept_names:
            learning_path.append({
                'topic': 'Object-Oriented Programming',
                'why': 'Master OOP principles',
                'difficulty': 'Intermediate'
            })
        
        if 'Recursion' in concept_names:
            learning_path.append({
                'topic': 'Dynamic Programming',
                'why': 'Optimize recursive solutions',
                'difficulty': 'Advanced'
            })
        
        # Add based on complexity
        if complexity.get('cyclomatic', 0) > 10:
            learning_path.append({
                'topic': 'Code Refactoring Techniques',
                'why': 'Learn to simplify complex code',
                'difficulty': 'Intermediate'
            })
        
        return learning_path[:5]  # Return top 5 suggestions


# Example usage
if __name__ == "__main__":
    explainer = CodeExplainer()
    
    test_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"Factorial: {result}")
"""
    
    explanation = explainer.explain(test_code, detail_level="detailed")
    
    print("\n" + "="*70)
    print("CODE EXPLANATION")
    print("="*70)
    
    print(f"\n📖 Overview:")
    print(f"{explanation['overview']}\n")
    
    print(f"📊 Complexity:")
    print(f"  Grade: {explanation['complexity']['complexity_grade']}")
    print(f"  {explanation['complexity']['interpretation']}\n")
    
    print(f"🎯 Key Concepts ({len(explanation['concepts'])}):")
    for concept in explanation['concepts']:
        print(f"  • {concept['name']}: {concept['description']}")
    
    print(f"\n📚 Learning Path:")
    for item in explanation['learning_path']:
        print(f"  {item['difficulty']}: {item['topic']}")
        print(f"     Why: {item['why']}")