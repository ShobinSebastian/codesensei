# test_imports.py
print("Testing imports...")

try:
    import fastapi
    print("✅ FastAPI installed")
except ImportError:
    print("❌ FastAPI not installed")

try:
    import groq
    print("✅ Groq installed")
except ImportError:
    print("❌ Groq not installed")

try:
    import pylint
    print("✅ Pylint installed")
except ImportError:
    print("❌ Pylint not installed")

try:
    import click
    print("✅ Click installed")
except ImportError:
    print("❌ Click not installed")

try:
    import rich
    print("✅ Rich installed")
except ImportError:
    print("❌ Rich not installed")

print("\n✅ All core dependencies installed successfully!")