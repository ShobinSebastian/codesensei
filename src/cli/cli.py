# src/cli/cli.py

"""
CodeSensei CLI
==============
Command-line interface for CodeSensei.

Usage:
    codesensei analyze <file>      # Analyze a Python file
    codesensei explain <file>      # Explain code
    codesensei debug <file>        # Debug bugs
    codesensei fix <file>          # Auto-fix bugs
    codesensei --help              # Show help

Author: Shobin Sebastian
Date: November 2025
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.orchestrator import CodeAnalysisOrchestrator
from src.features.code_explainer import CodeExplainer
from src.features.bug_debugger import BugDebugger
from src.analyzers.static_analyzer import StaticAnalyzer
from src.agents.llm_agent import LLMAgent

# Initialize Rich console
console = Console()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_code_from_file(filepath: str) -> str:
    """Load code from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        console.print(f"[red]❌ Error: File '{filepath}' not found[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error reading file: {e}[/red]")
        sys.exit(1)


def display_header(title: str):
    """Display a fancy header."""
    console.print()
    console.print(Panel(
        f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))


def display_code(code: str, title: str = "Code"):
    """Display code with syntax highlighting."""
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="blue"))


def display_issues_table(issues: list):
    """Display issues in a formatted table."""
    if not issues:
        console.print("[green]✅ No issues found![/green]")
        return
    
    table = Table(title="Issues Found", show_header=True, header_style="bold magenta")
    table.add_column("Line", style="cyan", width=6)
    table.add_column("Severity", width=10)
    table.add_column("Category", width=12)
    table.add_column("Message", style="white")
    
    for issue in issues:
        severity = issue.get('severity', 'medium')
        severity_color = {
            'critical': '[red]🔴 CRITICAL[/red]',
            'medium': '[yellow]🟡 MEDIUM[/yellow]',
            'low': '[green]🟢 LOW[/green]'
        }.get(severity, severity)
        
        table.add_row(
            str(issue.get('line', '?')),
            severity_color,
            issue.get('category', 'N/A'),
            issue.get('message', 'No message')[:60]
        )
    
    console.print(table)


def display_summary(summary: dict):
    """Display summary statistics."""
    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="cyan bold")
    table.add_column("Value", style="yellow")
    
    table.add_row("Total Issues", str(summary.get('total', 0)))
    table.add_row("Critical", f"[red]{summary.get('by_severity', {}).get('critical', 0)}[/red]")
    table.add_row("Medium", f"[yellow]{summary.get('by_severity', {}).get('medium', 0)}[/yellow]")
    table.add_row("Low", f"[green]{summary.get('by_severity', {}).get('low', 0)}[/green]")
    
    console.print(Panel(table, title="📊 Summary", border_style="cyan"))


# ============================================================================
# CLI COMMANDS
# ============================================================================

@click.group()
@click.version_option(version="0.3.0", prog_name="CodeSensei")
def cli():
    """
    🎓 CodeSensei - AI-Powered Code Analysis Tool
    
    Analyze, explain, and debug Python code with AI assistance.
    """
    pass


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--llm/--no-llm', default=False, help='Use LLM analysis (slower but smarter)')
@click.option('--output', '-o', type=click.Path(), help='Save results to file')
def analyze(filepath, llm, output):
    """
    Analyze a Python file for bugs and issues.
    
    Example: codesensei analyze my_code.py
    """
    display_header(f"Analyzing: {filepath}")
    
    # Load code
    code = load_code_from_file(filepath)
    
    # Show code preview
    preview = '\n'.join(code.split('\n')[:10])
    if len(code.split('\n')) > 10:
        preview += '\n... (truncated)'
    display_code(preview, f"Code Preview ({len(code.split('\n'))} lines)")
    
    # Analyze with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing code...", total=None)
        
        try:
            orchestrator = CodeAnalysisOrchestrator()
            result = orchestrator.analyze(code, use_llm=llm)
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]❌ Analysis failed: {e}[/red]")
            sys.exit(1)
    
    # Display results
    console.print()
    display_summary(result['summary'])
    console.print()
    display_issues_table(result['issues'][:10])  # Show top 10
    
    # Show metadata
    metadata = result['metadata']
    console.print(f"\n[dim]Analysis completed in {metadata['execution_time']:.2f}s[/dim]")
    console.print(f"[dim]LLM used: {metadata['llm_used']}[/dim]")
    
    # Save to file if requested
    if output:
        save_results(result, output)
        console.print(f"\n[green]✅ Results saved to {output}[/green]")


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--detail', type=click.Choice(['basic', 'medium', 'detailed']), default='medium')
def explain(filepath, detail):
    """
    Explain what the code does in simple terms.
    
    Example: codesensei explain my_code.py --detail detailed
    """
    display_header(f"Explaining: {filepath}")
    
    # Load code
    code = load_code_from_file(filepath)
    display_code(code[:500], "Code to Explain")
    
    # Explain with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating explanation...", total=None)
        
        try:
            explainer = CodeExplainer()
            result = explainer.explain(code, detail_level=detail)
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]❌ Explanation failed: {e}[/red]")
            sys.exit(1)
    
    # Display explanation
    console.print()
    console.print(Panel(
        result['overview'],
        title="📖 Explanation",
        border_style="green"
    ))
    
    # Show concepts
    if result['concepts']:
        console.print("\n[bold cyan]🎯 Key Concepts:[/bold cyan]")
        for concept in result['concepts'][:5]:
            console.print(f"  • [yellow]{concept['name']}[/yellow]: {concept['description']}")
    
    # Show complexity
    complexity = result['complexity']
    console.print(f"\n[bold cyan]📊 Complexity:[/bold cyan]")
    console.print(f"  Grade: {complexity.get('complexity_grade', 'N/A')}")
    console.print(f"  {complexity.get('interpretation', '')}")


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--error', '-e', help='Error message from running the code')
@click.option('--output', '-o', type=click.Path(), help='Save debug report to file')
def debug(filepath, error, output):
    """
    Debug bugs in a Python file.
    
    Example: codesensei debug buggy.py --error "ZeroDivisionError"
    """
    display_header(f"Debugging: {filepath}")
    
    # Load code
    code = load_code_from_file(filepath)
    display_code(code, "Buggy Code")
    
    if error:
        console.print(f"\n[red]Error Message: {error}[/red]")
    
    # Debug with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Debugging code...", total=None)
        
        try:
            debugger = BugDebugger()
            result = debugger.debug(code, error_message=error)
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]❌ Debugging failed: {e}[/red]")
            sys.exit(1)
    
    # Display bugs found
    console.print()
    bugs = result['bugs_found']
    
    if not bugs:
        console.print("[green]✅ No bugs detected![/green]")
        return
    
    console.print(f"[bold red]🐛 Found {len(bugs)} bug(s)[/bold red]\n")
    
    for i, bug in enumerate(bugs, 1):
        console.print(f"{i}. [yellow]Line {bug['line']}[/yellow]: {bug['message']}")
        console.print(f"   Category: {bug['category']}, Severity: {bug['severity']}\n")
    
    # Show fix steps
    if result['fix_steps']:
        console.print("[bold cyan]🔧 Fix Steps:[/bold cyan]\n")
        for fix in result['fix_steps'][:2]:  # Show first 2
            console.print(f"[yellow]Bug: {fix['bug']}[/yellow]")
            for j, step in enumerate(fix['steps'], 1):
                console.print(f"  {j}. {step}")
            console.print()
    
    # Show prevention tips
    if result['prevention_tips']:
        console.print("[bold cyan]💡 Prevention Tips:[/bold cyan]\n")
        for tip in result['prevention_tips'][:3]:
            console.print(f"  • {tip['tip']}")
            console.print(f"    Example: [dim]{tip['example']}[/dim]\n")
    
    # Save if requested
    if output:
        save_results(result, output)
        console.print(f"[green]✅ Debug report saved to {output}[/green]")


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Save fixed code to file')
def fix(filepath, output):
    """
    Automatically fix bugs in a Python file.
    
    Example: codesensei fix buggy.py --output fixed.py
    """
    display_header(f"Auto-fixing: {filepath}")
    
    # Load code
    code = load_code_from_file(filepath)
    display_code(code, "Original Code")
    
    # Fix with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating fix...", total=None)
        
        try:
            debugger = BugDebugger()
            bugs = debugger._detect_bugs(code, None)
            
            if not bugs:
                console.print("\n[green]✅ No bugs detected! Code looks good.[/green]")
                return
            
            fixed_code = debugger._generate_fixed_code(code, bugs)
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]❌ Fix generation failed: {e}[/red]")
            sys.exit(1)
    
    # Display fixed code
    console.print()
    display_code(fixed_code, "Fixed Code")
    
    console.print(f"\n[green]✅ Fixed {len(bugs)} bug(s)[/green]")
    
    # Save if requested
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        console.print(f"[green]✅ Fixed code saved to {output}[/green]")
    else:
        console.print("\n[yellow]💡 Tip: Use --output to save the fixed code[/yellow]")


@cli.command()
def interactive():
    """
    Start interactive mode.
    
    Example: codesensei interactive
    """
    display_header("Interactive Mode")
    
    console.print("[cyan]Welcome to CodeSensei Interactive Mode![/cyan]")
    console.print("[dim]Type 'help' for commands, 'exit' to quit[/dim]\n")
    
    while True:
        try:
            command = console.input("[bold green]codesensei> [/bold green]")
            
            if not command.strip():
                continue
            
            if command.lower() in ['exit', 'quit']:
                console.print("[cyan]Goodbye! 👋[/cyan]")
                break
            
            elif command.lower() == 'help':
                console.print("""
[cyan]Available commands:[/cyan]
  analyze <file>  - Analyze a Python file
  explain <file>  - Explain code
  debug <file>    - Debug bugs
  fix <file>      - Auto-fix bugs
  help            - Show this help
  exit            - Exit interactive mode
                """)
            
            else:
                console.print("[yellow]Unknown command. Type 'help' for available commands.[/yellow]")
        
        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye! 👋[/cyan]")
            break
        except EOFError:
            break


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_results(results: dict, filepath: str):
    """Save analysis results to a file."""
    import json
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    cli()