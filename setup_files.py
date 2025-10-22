# setup_files.py
"""
Setup Script - Creates missing directories and files
Run this to set up your project structure
"""

import os

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Created: {path}")
    else:
        print(f"⏭️  Exists: {path}")

def create_file(path, content=""):
    """Create file with content."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)
        print(f"✅ Created: {path}")
    else:
        print(f"⏭️  Exists: {path}")

def main():
    print("🔧 Setting up CodeSensei project structure...\n")
    
    # Create directories
    print("📁 Creating directories...")
    create_directory("src")
    create_directory("src/analyzers")
    create_directory("src/agents")
    create_directory("src/core")
    create_directory("src/api")
    create_directory("src/tests")
    
    # Create __init__.py files
    print("\n📄 Creating __init__.py files...")
    create_file("src/__init__.py")
    create_file("src/analyzers/__init__.py")
    create_file("src/agents/__init__.py")
    create_file("src/core/__init__.py")
    create_file("src/api/__init__.py")
    create_file("src/tests/__init__.py")
    
    # Show next steps
    print("\n" + "="*60)
    print("✅ Directory structure created!")
    print("="*60)
    
    print("\n📋 Next steps:")
    print("1. Copy orchestrator.py code to: src/core/orchestrator.py")
    print("2. Copy test_manual.py code to: src/tests/test_manual.py")
    print("3. Copy test_integration.py code to: src/tests/test_integration.py")
    print("4. Run: python quick_start.py")
    
    print("\n📁 Current structure:")
    print("CodeSensei/")
    print("├── src/")
    print("│   ├── __init__.py ✅")
    print("│   ├── analyzers/")
    print("│   │   ├── __init__.py ✅")
    print("│   │   └── static_analyzer.py")
    print("│   ├── agents/")
    print("│   │   ├── __init__.py ✅")
    print("│   │   └── llm_agent.py")
    print("│   ├── core/")
    print("│   │   ├── __init__.py ✅")
    print("│   │   └── orchestrator.py ⬅️ CREATE THIS")
    print("│   ├── api/")
    print("│   │   ├── __init__.py ✅")
    print("│   │   └── main.py")
    print("│   └── tests/")
    print("│       ├── __init__.py ✅")
    print("│       ├── test_manual.py ⬅️ CREATE THIS")
    print("│       └── test_integration.py ⬅️ CREATE THIS")
    print("└── quick_start.py ⬅️ CREATE THIS")
    
    print("\n🎯 Files you need to create manually:")
    print("   Copy from the artifacts I provided above!")

if __name__ == "__main__":
    main()