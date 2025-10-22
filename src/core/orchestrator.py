# src/core/orchestrator.py

"""
Code Analysis Orchestrator
===========================
This module orchestrates the complete code analysis pipeline:
1. Static Analysis (pylint, bandit) - Fast, rule-based
2. LLM Analysis (AI reasoning) - Slow, context-aware
3. Combines and deduplicates results
4. Prioritizes issues for display

Think of this as the "conductor" coordinating the orchestra!

Author: Shobin Sebastian  
Day 3-4
"""

from typing import List, Dict, Any, Optional
from src.analyzers.static_analyzer import StaticAnalyzer
from src.agents.llm_agent import LLMAgent
import time

class CodeAnalysisOrchestrator:
    """
    Orchestrates the complete code analysis pipeline.
    
    Why we need this:
    - Static analyzer is fast but misses context
    - LLM is smart but slow
    - We want the best of both worlds!
    
    Strategy:
    1. Always run static analysis (fast, catches obvious issues)
    2. Run LLM only if requested (slow but insightful)
    3. Merge results intelligently
    4. Prioritize critical issues
    """
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the orchestrator with both analyzers.
        
        Args:
            groq_api_key: Optional Groq API key for LLM agent
        """
        print("Initializing Code Analysis Orchestrator...")

        # Initialize static analyzer (always available)
        self.static_analyzer = StaticAnalyzer()
        print(" ✓ Static analyzer ready")

        # Initialize LLM agent (may fail if no API key)
        try:
           self.llm_agent = LLMAgent(api_key=groq_api_key)
           self.llm_available = True
           print("  ✓ LLM agent ready")
        except Exception as e:
            self.llm_agent = None
            self.llm_available = False
            print(f"  ⚠ LLM agent unavailable: {e}")

    def analyze(self, code: str, use_llm: bool = True, max_llm_time: int = 30):
        """
        Perform complete code analysis.
        
        This is the main function that combines everything!
        
        Args:
            code: Python code to analyze
            use_llm: Whether to use LLM analysis (default: True)
            max_llm_time: Maximum seconds to wait for LLM (default: 30)
            
        Returns:
            Complete analysis results with:
                - issues: All issues found (deduplicated)
                - summary: Statistics
                - metadata: Analysis info (time, tools used)
        """

        print("\n" + "="*60)
        print("🔍 STARTING COMPREHENSIVE CODE ANALYSIS")
        print("="*60)

        start_time = time.time()
        # Phase 1: Static Analysis (always runs)
        print("\n📊 Phase 1: Static Analysis")
        print("-" * 40)
        static_result = self.static_analyzer.analyze(code)
        static_issues = static_result['issues']

        print(f"  ✓ Static analysis complete")
        print(f"    Found: {len(static_issues)} issues")

        # Phase 2: LLM Analysis (optional)
        llm_issues = []
        llm_used = False

        if use_llm and self.llm_available:
            print("\n🤖 Phase 2: LLM Analysis")
            print("-" * 40)

            try:
                # Pass static issues to LLM for context
                llm_issues = self.llm_agent.analyze(
                    code, 
                    static_issues=static_issues
                )
                llm_used = True
                print(f"  ✓ LLM analysis complete")
                print(f"    Found: {len(llm_issues)} issues")
            except Exception as e:
                print(f"  ⚠ LLM analysis failed: {e}")
                llm_issues = []
        elif use_llm and not self.llm_available:
            print("\n⚠ Skipping LLM Analysis (not available)")
        
        else:
            print("\n⏭ Skipping LLM Analysis (not requested)")

        # Phase 3: Merge and Deduplicate
        print("\n🔄 Phase 3: Merging Results")
        print("-" * 40)

        all_issues = self._merge_issues(static_issues, llm_issues)
        print(f"  ✓ Merged {len(all_issues)} unique issues")

        # Phase 4: Enrich and Prioritize
        print("\n✨ Phase 4: Enriching Issues")
        print("-" * 40)

        enriched_issues = self._enrich_issues(all_issues, code)
        sorted_issues = self._prioritize_issues(enriched_issues)
        print(f"  ✓ Issues enriched and prioritized")

        # Phase 5: Generate Summary
        summary = self._generate_summary(sorted_issues)

        # Calculate execution time
        execution_time = time.time() - start_time

        print("\n" + "="*60)
        print(f"✅ ANALYSIS COMPLETE ({execution_time:.2f}s)")
        print("="*60)

        return {
            'issues': sorted_issues,
            'summary': summary,
            'metadata': {
                'execution_time': round(execution_time, 2),
                'static_issues': len(static_issues),
                'llm_issues': len(llm_issues),
                'total_unique_issues': len(sorted_issues),
                'llm_used': llm_used,
                'code_lines': len(code.split('\n'))
            }
        }
    

    def _merge_issues(self, static_issues: List[Dict], llm_issues: List[Dict]) -> List[Dict]:
        """
        Merge issues from static and LLM analyzers.
        
        Smart merging:
        - Remove exact duplicates
        - Keep complementary issues (same line, different insights)
        - Prefer LLM explanations when both find same issue
        """

        merged = []
        seen_signatures = set()

        # Process static issues first
        for issue in static_issues:
            signature = self._create_issue_signature(issue)
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                merged.append(issue)

        # Add LLM issues
        for issue in llm_issues:
            signature = self._create_issue_signature(issue)

            # Check for similar issue from static analyzer
            similar_found = False
            for i, existing in enumerate(merged):
                if self._are_issues_similar(issue, existing):
                    # Merge: Keep static issue but add LLM insights
                    merged[i] = self._merge_similar_issues(existing, issue)
                    similar_found = True
                    break
            
            # If no similar issue, add as new
            if not similar_found:
                merged.append(issue)
        
        return merged
    

    def _create_issue_signature(self, issue: Dict) -> str:
        """
        Create unique signature for an issue.
        
        Signature = line + message (normalized)
        Used to detect duplicates.
        """
        line = issue.get('line', 0)
        message = issue.get('message', '').lower()
        # Take first 50 chars of message
        message_key = message[:50]
        return f"{line}:{message_key}"
    
    def _are_issues_similar(self, issue1: Dict, issue2: Dict) -> bool:
        """
        Check if two issues are about the same problem.
        
        Issues are similar if:
        - Same line number
        - Similar message content
        """
        if issue1.get('line') != issue2.get('line'):
            return False
        
        msg1 = issue1.get('message', '').lower()
        msg2 = issue2.get('message', '').lower()
        
        # Check for keyword overlap
        words1 = set(msg1.split())
        words2 = set(msg2.split())
        
        # If >50% words overlap, consider similar
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1 & words2)
        min_words = min(len(words1), len(words2))
        
        return (overlap / min_words) > 0.5
    
    def _merge_similar_issues(self, static_issue: Dict, llm_issue: Dict) -> Dict:
        """
        Merge two similar issues into one enhanced issue.
        
        Strategy:
        - Keep static issue's metadata (line, type, tool)
        - Enhance with LLM's explanation and fix suggestion
        """
        merged = static_issue.copy()
        
        # Add LLM insights
        if 'explanation' in llm_issue:
            merged['llm_explanation'] = llm_issue['explanation']
        
        if 'fix' in llm_issue:
            merged['suggested_fix'] = llm_issue['fix']
        
        if 'example' in llm_issue:
            merged['example'] = llm_issue['example']
        
        # Mark as enhanced by LLM
        merged['enhanced_by_llm'] = True
        
        return merged
    

    def _enrich_issues(self, issues: List[Dict], code: str) -> List[Dict]:
        """
        Enrich issues with additional context.
        
        Adds:
        - Code snippet (the actual line of code)
        - Surrounding context (lines before/after)
        - Category (bug, style, security, performance)
        """
        code_lines = code.split('\n')
        
        for issue in issues:
            line_num = issue.get('line', 0)
            
            # Add code snippet
            if 0 < line_num <= len(code_lines):
                issue['code_snippet'] = code_lines[line_num - 1].strip()
                
                # Add context (2 lines before and after)
                start = max(0, line_num - 3)
                end = min(len(code_lines), line_num + 2)
                issue['context'] = '\n'.join(code_lines[start:end])
            
            # Categorize issue
            issue['category'] = self._categorize_issue(issue)
            
            # Add educational tip
            issue['learning_tip'] = self._get_learning_tip(issue)
        
        return issues
    
    def _categorize_issue(self, issue: Dict) -> str:
        """
        Categorize issue into meaningful groups.
        
        Categories:
        - bug: Will cause errors
        - security: Security vulnerability
        - performance: Slow or inefficient code
        - style: Code style/readability
        - logic: Logical error
        """
        issue_type = issue.get('type', '').lower()
        message = issue.get('message', '').lower()
        
        if issue_type == 'security':
            return 'security'
        
        if issue_type == 'syntax_error':
            return 'bug'
        
        # Check message for keywords
        if any(word in message for word in ['undefined', 'not defined', 'error']):
            return 'bug'
        
        if any(word in message for word in ['performance', 'slow', 'inefficient']):
            return 'performance'
        
        if any(word in message for word in ['logic', 'edge case', 'division by zero']):
            return 'logic'
        
        return 'style'
    
    def _get_learning_tip(self, issue: Dict) -> str:
        """
        Generate educational tip for the issue.
        
        Helps developers learn WHY something matters.
        """
        category = issue.get('category', '')
        
        tips = {
            'security': "🔒 Security issues can expose your app to attacks. Always validate user input!",
            'bug': "🐛 Bugs cause crashes or wrong results. Test edge cases!",
            'logic': "🧠 Logic errors are subtle - code runs but gives wrong results.",
            'performance': "⚡ Performance matters at scale. Small optimizations add up!",
            'style': "✨ Clean code is easier to maintain and debug."
        }
        
        return tips.get(category, "💡 Writing good code is a skill that improves with practice!")
    
    def _prioritize_issues(self, issues: List[Dict]) -> List[Dict]:
        """
        Sort issues by priority.
        
        Priority order:
        1. Severity (critical > medium > low)
        2. Category (bug/security > logic > style)
        3. Line number (top to bottom)
        """
        severity_order = {'critical': 0, 'medium': 1, 'low': 2}
        category_order = {
            'bug': 0, 'security': 0, 
            'logic': 1, 'performance': 2, 'style': 3
        }
        
        def priority_key(issue):
            severity = severity_order.get(issue.get('severity', 'low'), 3)
            category = category_order.get(issue.get('category', 'style'), 4)
            line = issue.get('line', 9999)
            return (severity, category, line)
        
        return sorted(issues, key=priority_key)
    
    def _generate_summary(self, issues: List[Dict]) -> Dict[str, Any]:
        """
        Generate comprehensive summary statistics.
        """
        summary = {
            'total': len(issues),
            'by_severity': {
                'critical': 0,
                'medium': 0,
                'low': 0
            },
            'by_category': {
                'bug': 0,
                'security': 0,
                'logic': 0,
                'performance': 0,
                'style': 0
            },
            'by_tool': {
                'static': 0,
                'llm': 0,
                'enhanced': 0
            }
        }
        
        for issue in issues:
            # Count by severity
            severity = issue.get('severity', 'low')
            if severity in summary['by_severity']:
                summary['by_severity'][severity] += 1
            
            # Count by category
            category = issue.get('category', 'style')
            if category in summary['by_category']:
                summary['by_category'][category] += 1
            
            # Count by tool
            if issue.get('enhanced_by_llm'):
                summary['by_tool']['enhanced'] += 1
            elif issue.get('tool') == 'llm':
                summary['by_tool']['llm'] += 1
            else:
                summary['by_tool']['static'] += 1
        
        return summary
    
    # Example usage
if __name__ == "__main__":
    # Test code with multiple issues
    test_code = """
def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

result = calculate_average([])
print(result)
"""

    # Initialize orchestrator
    orchestrator = CodeAnalysisOrchestrator()
    
    # Run analysis
    result = orchestrator.analyze(test_code, use_llm=True)
    
    # Display results
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📊 Summary:")
    print(f"  Total Issues: {result['summary']['total']}")
    print(f"  Critical: {result['summary']['by_severity']['critical']}")
    print(f"  Medium: {result['summary']['by_severity']['medium']}")
    print(f"  Low: {result['summary']['by_severity']['low']}")
    
    print(f"\n🔧 By Category:")
    for category, count in result['summary']['by_category'].items():
        if count > 0:
            print(f"  {category.capitalize()}: {count}")
    
    print(f"\n⏱ Metadata:")
    print(f"  Execution Time: {result['metadata']['execution_time']}s")
    print(f"  LLM Used: {result['metadata']['llm_used']}")
    
    print(f"\n🔍 Issues Found:")
    for i, issue in enumerate(result['issues'][:5], 1):  # Show first 5
        print(f"\n{i}. [{issue['severity'].upper()}] Line {issue['line']}")
        print(f"   Category: {issue['category']}")
        print(f"   {issue['message']}")
        if 'learning_tip' in issue:
            print(f"   {issue['learning_tip']}")