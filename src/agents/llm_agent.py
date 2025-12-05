"""
LLM Agent for Code Review
==========================
This module uses Large Language Models (like GPT, Claude, Mixtral) 
to analyze code with human-like reasoning.

Why use LLM for code review?
- Understands context (not just patterns)
- Can explain WHY something is wrong
- Finds logical errors static tools miss
- Provides educational feedback
 
"""

import os
from typing import List, Dict, Any, Optional
from groq import Groq
import json
from dotenv import load_dotenv

# Load environmental variable from .env file
load_dotenv()

class LLMAgent:
    """
    An AI agent that reviews code using Large Language Models.
    These models can understand and reason about code like a human.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM agent.
        
        Args:
            api_key: Groq API key (if None, loads from environment)
        """
        # Get Groq api key from env
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found! "
                "Please add it to your .env file or pass it as parameter."
            )
        
        # Initialize Groq client
        # Groq provides fast, free access to open-source LLMs
        self.client = Groq(api_key=self.api_key)
        
        # Model to use (llama-3.3-70b-versatile is the fast model)
        self.model = "llama-3.3-70b-versatile"
        
        # Temperature controls randomness (0 = deterministic, 1 = creative)
        # For code review, we want consistent, accurate responses
        self.temperature = 0.1
        
        print("✅ LLM Agent initialized with Groq")

    def analyze(self, code: str, static_issues: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        Analyze code using LLM reasoning.
    
        This is different from static analysis because:
        - LLM understands the MEANING of code
        - Can find logical errors
        - Provides explanations in plain English
        
        Args:
            code: Python code to analyze
            static_issues: Issues found by static analyzer (optional)
                        LLM uses these as hints
        
        Returns:
            List of issues found by the LLM
        """
        print("🤖 LLM Agent analyzing code...")
        
        # Build the prompt (instructions for the LLM)
        prompt = self._build_prompt(code, static_issues)
        
        # Call the LLM
        try:
            response = self._call_llm(prompt)
            
            # Parse LLM's response into structured format
            issues = self._parse_response(response)
            print(f"  ✓ LLM found {len(issues)} issues")
            return issues
        except Exception as e:
            print(f"  ⚠ LLM analysis failed: {e}")
            return []

    def _build_prompt(self, code: str, static_issues: Optional[List[Dict]] = None) -> str:
        """
        Build the prompt (instruction) for the LLM.
        
        Prompt engineering = Writing good instructions for AI
        This is crucial for getting good results!
        
        A good prompt should:
        1. Be clear and specific
        2. Provide context
        3. Request structured output
        4. Include examples (if needed)
        """
        
        # System message: Defines the LLM's role and behavior
        system_message = """You are an expert code reviewer and teacher.

Your task: Review Python code and find issues that automated tools might miss.

Focus on:
1. Logic errors (code that runs but gives wrong results)
2. Edge cases not handled (what if input is empty? negative?)
3. Potential bugs (undefined behavior, race conditions)
4. Best practices violations
5. Code that's hard to understand

For EACH issue you find:
- Explain WHAT is wrong
- Explain WHY it's a problem
- Explain HOW to fix it
- Rate severity: critical, medium, or low

Output format: JSON array of issues
[
{
    "type": "logic_error" | "edge_case" | "best_practice" | "bug",
    "severity": "critical" | "medium" | "low",
    "line": <line_number>,
    "message": "Brief description",
    "explanation": "Detailed explanation of WHY this is a problem",
    "fix": "How to fix it",
    "example": "Example of what could go wrong"
}
]

Be educational: Help the developer learn, not just find mistakes."""

        # User message: The actual code to review
        user_message = f"""Review this Python code:
```python
{code}
```"""
        
        # Add static analysis context if available
        if static_issues and len(static_issues) > 0:
            user_message += f"\n\nNote: Static analysis already found these issues:\n"
            for issue in static_issues[:3]:  # Show first 3
                user_message += f"- Line {issue.get('line', 'N/A')}: {issue.get('message', 'N/A')}\n"
            user_message += "\nFocus on issues the static analyzer might have missed.\n"
        
        # Complete prompt
        full_prompt = f"{system_message}\n\n{user_message}"
        
        return full_prompt
    
    def _call_llm(self, prompt: str) -> str:
        """
        Make API call to Groq (LLM provider).
        
        This is where the magic happens!
        We send the code + instructions to the AI,
        and it sends back its analysis.
        
        Args:
            prompt: The instruction + code to analyze
            
        Returns:
            LLM's response as text
        """
        try:
            # Call Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=2000,  # Maximum length of response
                top_p=1,
                stream=False  # Get complete response at once
            )
            
            # Extract the text response
            response_text = completion.choices[0].message.content
            
            return response_text
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")
        
    
    def _parse_response(self, response: str) -> List[Dict]:
        """
        Parse LLM's text response into structured data.
        
        LLMs return text, but we need structured data (Python dicts).
        This function extracts JSON from the response.
        """
        issues = []
        
        try:
            # Try to find JSON in the response
            if "```json" in response:
                # Extract JSON from markdown code block
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_text = response[json_start:json_end].strip()
            elif "```" in response:
                # Generic code block
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_text = response[json_start:json_end].strip()
            else:
                # No code blocks, try to parse entire response
                json_text = response.strip()
            
            # Parse JSON
            parsed = json.loads(json_text)
            
            # Handle both single dict and list of dicts
            if isinstance(parsed, list):
                issues = parsed
            elif isinstance(parsed, dict):
                issues = [parsed]
            else:
                print(f"  ⚠ Unexpected JSON format: {type(parsed)}")
        
        except json.JSONDecodeError as e:
            # JSON parsing failed
            print(f"  ⚠ Could not parse LLM response as JSON: {e}")
            
            # Create a generic issue with the LLM's text
            if response.strip():
                issues = [{
                    'type': 'llm_analysis',
                    'severity': 'medium',
                    'line': 0,
                    'message': 'LLM analysis (unstructured)',
                    'explanation': response[:500],
                    'tool': 'llm'
                }]
        
        # Post-process all issues
        for issue in issues:
            issue['tool'] = 'llm'  # Mark as coming from LLM
            
            # Set defaults for missing fields
            if 'severity' not in issue:
                issue['severity'] = 'medium'
            if 'line' not in issue:
                issue['line'] = 0
            if 'message' not in issue:
                issue['message'] = 'Code quality issue'
        
        return issues
    
    def explain_code(self, code: str) -> str:
        """
        Generate a beginner-friendly explanation of code.
        
        This is a bonus feature - can be used for the
        "Code Explainer" feature later.
        
        Args:
            code: Python code to explain
            
        Returns:
            Plain English explanation
        """
        
        prompt = f"""Explain this Python code to a beginner in simple terms. 
Focus on what it does, not how it works internally.

```python
{code}
```

Provide a clear, friendly explanation."""
        
        try:
            response = self._call_llm(prompt)
            return response
        except Exception as e:
            print(f"  ⚠ Code explanation failed: {e}")
            return f"Could not explain code: {str(e)}"