# quick_start.py

"""
Quick Start Script
==================
One command to test everything!

Usage:
    python quick_start.py

This will:
1. Check dependencies
2. Verify API key
3. Test static analyzer
4. Test LLM agent (if available)
5. Test orchestrator
6. Start API server (optional)

Author: Shobin Sebastian
Date: November 2025
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def print_header(text):
    """Print fancy header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def check_dependencies():
    """Check if all required packages are installed."""
    print_header("1️⃣  CHECKING DEPENDENCIES")
    
    required = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pylint': 'Pylint',
        'bandit': 'Bandit',
        'groq': 'Groq',
        'dotenv': 'python-dotenv',
        'pytest': 'Pytest'
    }
    
    missing = []
    
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✅ {name} installed")
        except ImportError:
            print(f"  ❌ {name} missing")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print("  pip install fastapi uvicorn pylint bandit groq python-dotenv pytest")
        return False
    
    print("\n✅ All dependencies installed!")
    return True


def check_env():
    """Check environment variables."""
    print_header("2️⃣  CHECKING ENVIRONMENT")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check .env file exists
    if not os.path.exists('.env'):
        print("  ⚠️  .env file not found")
        print("\nCreate .env file with:")
        print("  GROQ_API_KEY=your_key_here")
        print("  ENVIRONMENT=development")
        return False
    
    print("  ✅ .env file exists")
    
    # Check API key
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print(f"  ✅ GROQ_API_KEY loaded ({len(api_key)} chars)")
    else:
        print("  ⚠️  GROQ_API_KEY not set")
        print("  LLM features will be disabled")
        return False
    
    return True


def test_static_analyzer():
    """Test static analyzer."""
    print_header("3️⃣  TESTING STATIC ANALYZER")
    
    try:
        from src.analyzers.static_analyzer import StaticAnalyzer
        
        analyzer = StaticAnalyzer()
        print("  ✅ Static analyzer initialized")
        
        # Test with simple code
        test_code = """
def test():
    x = 10 / 0
"""
        result = analyzer.analyze(test_code)
        
        print(f"  ✅ Analysis completed")
        print(f"     Found {len(result['issues'])} issues")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Static analyzer failed: {e}")
        return False


def test_llm_agent():
    """Test LLM agent."""
    print_header("4️⃣  TESTING LLM AGENT")
    
    try:
        from src.agents.llm_agent import LLMAgent
        
        agent = LLMAgent()
        print("  ✅ LLM agent initialized")
        
        # Test with simple code
        test_code = """
def divide(a, b):
    return a / b
"""
        issues = agent.analyze(test_code)
        
        print(f"  ✅ LLM analysis completed")
        print(f"     Found {len(issues)} issues")
        
        return True
        
    except ValueError as e:
        print(f"  ⚠️  LLM agent unavailable: {e}")
        print("     This is okay for testing static analysis only")
        return False
    except Exception as e:
        print(f"  ❌ LLM agent failed: {e}")
        return False


def test_orchestrator():
    """Test orchestrator."""
    print_header("5️⃣  TESTING ORCHESTRATOR")
    
    try:
        from src.core.orchestrator import CodeAnalysisOrchestrator
        
        orchestrator = CodeAnalysisOrchestrator()
        print("  ✅ Orchestrator initialized")
        
        # Test with code that has issues
        test_code = """
def calculate(a, b):
    result = a / b  # No zero check
    return result

x = calculate(10, 0)
"""
        
        print("  🔍 Running analysis...")
        result = orchestrator.analyze(test_code, use_llm=False)
        
        print(f"  ✅ Analysis completed")
        print(f"     Total issues: {result['summary']['total']}")
        print(f"     Critical: {result['summary']['by_severity']['critical']}")
        print(f"     Medium: {result['summary']['by_severity']['medium']}")
        print(f"     Low: {result['summary']['by_severity']['low']}")
        print(f"     Time: {result['metadata']['execution_time']}s")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Orchestrator failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api():
    """Test API endpoints."""
    print_header("6️⃣  TESTING API")
    
    try:
        from src.api.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("  ✅ Health endpoint working")
        else:
            print(f"  ❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test analyze endpoint
        response = client.post(
            "/analyze/static",
            json={"code": "print(1/0)"}
        )
        if response.status_code == 200:
            print("  ✅ Analyze endpoint working")
            data = response.json()
            print(f"     Found {len(data.get('issues', []))} issues")
        else:
            print(f"  ❌ Analyze endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def offer_to_start_server():
    """Ask if user wants to start the server."""
    print_header("7️⃣  START API SERVER?")
    
    print("\nDo you want to start the API server?")
    print("  - Visit http://localhost:8000/docs for Swagger UI")
    print("  - Press Ctrl+C to stop the server")
    print()
    
    choice = input("Start server? (y/n): ").lower().strip()
    
    if choice == 'y':
        print("\n🚀 Starting server...")
        print("   Visit: http://localhost:8000")
        print("   Docs:  http://localhost:8000/docs")
        print("\n   Press Ctrl+C to stop\n")
        
        try:
            import uvicorn
            uvicorn.run(
                "src.api.main:app",
                host="0.0.0.0",
                port=8000,
                reload=True
            )
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")
    else:
        print("\n✅ Skipping server start")


def print_summary(results):
    """Print test summary."""
    print_header("📊 TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n  Tests Passed: {passed}/{total}")
    print()
    
    for test, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use!")
    elif passed > 0:
        print("\n⚠️  Some tests failed, but basic functionality works")
    else:
        print("\n❌ Multiple failures detected. Check error messages above.")
    
    print()


def main():
    """Run all checks and tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "CODESENSEI QUICK START" + " "*25 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {}
    
    # Run checks
    results['Dependencies'] = check_dependencies()
    if not results['Dependencies']:
        print("\n❌ Cannot continue without dependencies")
        return
    
    results['Environment'] = check_env()
    results['Static Analyzer'] = test_static_analyzer()
    results['LLM Agent'] = test_llm_agent()
    results['Orchestrator'] = test_orchestrator()
    results['API'] = test_api()
    
    # Print summary
    print_summary(results)
    
    # Offer to start server if basic tests pass
    if results['Static Analyzer'] and results['Orchestrator']:
        offer_to_start_server()
    else:
        print("\n⚠️  Fix errors before starting server")
    
    print("\n📚 Next Steps:")
    print("  1. Run manual tests: python src/tests/test_manual.py")
    print("  2. Run pytest: pytest src/tests/test_integration.py -v")
    print("  3. Start server: uvicorn src.api.main:app --reload")
    print("  4. Read: DAY_3_4_INSTRUCTIONS.md")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()