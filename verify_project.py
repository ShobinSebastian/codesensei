# verify_project.py
"""
Project Verification Script
============================
This script checks your entire CodeSensei project structure
and tells you exactly what's missing and what works.

Save this file as: F:\Projects\CodeSensei\verify_project.py
Then run: python verify_project.py

Author: Shobin Sebastian
Date: November 2025
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Print fancy header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_file(filepath, description):
    """Check if a file exists and show result."""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}")
    if exists:
        size = os.path.getsize(filepath)
        if size == 0:
            print(f"   ⚠️  WARNING: File is empty (0 bytes)")
        else:
            print(f"   📄 Size: {size} bytes")
    return exists

def check_directory(dirpath, description):
    """Check if directory exists."""
    exists = os.path.exists(dirpath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}")
    return exists

def test_import(module_path, description):
    """Test if a Python module can be imported."""
    try:
        # Add project root to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        __import__(module_path)
        print(f"✅ {description} - Import works!")
        return True
    except ImportError as e:
        print(f"❌ {description} - Import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {description} - Error: {e}")
        return False

def main():
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "CODESENSEI PROJECT VERIFICATION" + " "*22 + "║")
    print("╚" + "="*68 + "╝")
    
    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"\n📁 Project Root: {project_root}")
    
    # Track what's working
    results = {
        'directories': {},
        'files': {},
        'imports': {}
    }
    
    # ========================================================================
    # CHECK DIRECTORIES
    # ========================================================================
    print_header("1️⃣  CHECKING DIRECTORY STRUCTURE")
    
    dirs_to_check = [
        ("src", "Source directory"),
        ("src/analyzers", "Analyzers module"),
        ("src/agents", "Agents module"),
        ("src/core", "Core module"),
        ("src/api", "API module"),
        ("src/tests", "Tests module"),
    ]
    
    for dir_path, description in dirs_to_check:
        full_path = os.path.join(project_root, dir_path)
        results['directories'][dir_path] = check_directory(full_path, description)
    
    # ========================================================================
    # CHECK __init__.py FILES
    # ========================================================================
    print_header("2️⃣  CHECKING __init__.py FILES")
    
    init_files = [
        "src/__init__.py",
        "src/analyzers/__init__.py",
        "src/agents/__init__.py",
        "src/core/__init__.py",
        "src/api/__init__.py",
        "src/tests/__init__.py",
    ]
    
    for init_file in init_files:
        full_path = os.path.join(project_root, init_file)
        results['files'][init_file] = check_file(full_path, init_file)
    
    # ========================================================================
    # CHECK MAIN SOURCE FILES
    # ========================================================================
    print_header("3️⃣  CHECKING MAIN SOURCE FILES")
    
    source_files = [
        ("src/analyzers/static_analyzer.py", "Static Analyzer", True),
        ("src/agents/llm_agent.py", "LLM Agent", True),
        ("src/core/orchestrator.py", "Orchestrator", True),
        ("src/api/main.py", "FastAPI Main", True),
    ]
    
    for file_path, description, required in source_files:
        full_path = os.path.join(project_root, file_path)
        exists = check_file(full_path, f"{description} ({file_path})")
        results['files'][file_path] = exists
        
        if required and not exists:
            print(f"   ❗ CRITICAL: This file is REQUIRED!")
    
    # ========================================================================
    # CHECK TEST FILES
    # ========================================================================
    print_header("4️⃣  CHECKING TEST FILES")
    
    test_files = [
        ("src/tests/test_static_analyzer.py", "Static Analyzer Tests", False),
        ("src/tests/test_llm_agent.py", "LLM Agent Tests", False),
        ("src/tests/test_manual.py", "Manual Tests", False),
        ("src/tests/test_integration.py", "Integration Tests", False),
    ]
    
    for file_path, description, required in test_files:
        full_path = os.path.join(project_root, file_path)
        exists = check_file(full_path, f"{description} ({file_path})")
        results['files'][file_path] = exists
    
    # ========================================================================
    # CHECK CONFIGURATION FILES
    # ========================================================================
    print_header("5️⃣  CHECKING CONFIGURATION FILES")
    
    config_files = [
        (".env", "Environment variables", True),
        ("requirements.txt", "Dependencies", False),
        (".gitignore", "Git ignore", False),
    ]
    
    for file_path, description, required in config_files:
        full_path = os.path.join(project_root, file_path)
        exists = check_file(full_path, f"{description} ({file_path})")
        results['files'][file_path] = exists
        
        if file_path == ".env" and exists:
            # Check .env content
            with open(full_path, 'r') as f:
                content = f.read()
                if "GROQ_API_KEY" in content:
                    print("   ✅ GROQ_API_KEY found in .env")
                else:
                    print("   ⚠️  GROQ_API_KEY not found in .env")
    
    # ========================================================================
    # TEST IMPORTS
    # ========================================================================
    print_header("6️⃣  TESTING PYTHON IMPORTS")
    
    imports_to_test = [
        ("src.analyzers.static_analyzer", "Static Analyzer"),
        ("src.agents.llm_agent", "LLM Agent"),
        ("src.core.orchestrator", "Orchestrator"),
        ("src.api.main", "FastAPI Main"),
    ]
    
    for module_path, description in imports_to_test:
        results['imports'][module_path] = test_import(module_path, description)
    
    # ========================================================================
    # TEST DEPENDENCIES
    # ========================================================================
    print_header("7️⃣  TESTING DEPENDENCIES")
    
    dependencies = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pylint', 'Pylint'),
        ('bandit', 'Bandit'),
        ('groq', 'Groq'),
        ('dotenv', 'python-dotenv'),
        ('pytest', 'Pytest'),
        ('pydantic', 'Pydantic'),
    ]
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed")
            print(f"   Install: pip install {module if module != 'dotenv' else 'python-dotenv'}")
    
    # ========================================================================
    # GENERATE SUMMARY
    # ========================================================================
    print_header("📊 SUMMARY")
    
    total_dirs = len(results['directories'])
    ok_dirs = sum(results['directories'].values())
    
    total_files = len(results['files'])
    ok_files = sum(results['files'].values())
    
    total_imports = len(results['imports'])
    ok_imports = sum(results['imports'].values())
    
    print(f"\n📁 Directories: {ok_dirs}/{total_dirs} OK")
    print(f"📄 Files: {ok_files}/{total_files} OK")
    print(f"📦 Imports: {ok_imports}/{total_imports} OK")
    
    # ========================================================================
    # PROVIDE ACTIONABLE STEPS
    # ========================================================================
    print_header("🔧 WHAT TO DO NEXT")
    
    missing_critical = []
    
    # Check critical files
    critical_files = [
        "src/core/orchestrator.py",
        "src/analyzers/static_analyzer.py",
        "src/agents/llm_agent.py",
        "src/api/main.py",
    ]
    
    for file_path in critical_files:
        if not results['files'].get(file_path, False):
            missing_critical.append(file_path)
    
    if missing_critical:
        print("\n❌ CRITICAL FILES MISSING:")
        for file_path in missing_critical:
            print(f"   • {file_path}")
        print("\n📋 You need to CREATE these files!")
        print("   Copy the code from the artifacts I provided earlier.")
    else:
        print("\n✅ All critical files present!")
    
    # Check if we can run tests
    can_test = (
        results['files'].get('src/core/orchestrator.py', False) and
        results['files'].get('src/analyzers/static_analyzer.py', False)
    )
    
    if can_test:
        print("\n✅ Ready to test!")
        print("\n🚀 Run these commands:")
        print("   1. Test imports:")
        print("      python -c \"from src.core.orchestrator import CodeAnalysisOrchestrator; print('Works!')\"")
        print("\n   2. Run manual tests (if file exists):")
        print("      python src/tests/test_manual.py")
        print("\n   3. Start API server:")
        print("      uvicorn src.api.main:app --reload")
    else:
        print("\n⚠️  NOT ready to test yet!")
        print("   Create missing files first.")
    
    # ========================================================================
    # CREATE MISSING __init__.py FILES
    # ========================================================================
    print_header("🔨 AUTO-FIX: Creating Missing __init__.py Files")
    
    for init_file in init_files:
        full_path = os.path.join(project_root, init_file)
        if not os.path.exists(full_path):
            # Create directory if needed
            dir_path = os.path.dirname(full_path)
            os.makedirs(dir_path, exist_ok=True)
            
            # Create empty __init__.py
            with open(full_path, 'w') as f:
                f.write("# Auto-generated by verify_project.py\n")
            print(f"✅ Created: {init_file}")
        else:
            print(f"⏭️  Exists: {init_file}")
    
    print("\n" + "="*70)
    print("✅ Verification complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()