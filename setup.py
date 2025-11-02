# setup.py

"""
CodeSensei Package Setup
=========================
Makes CodeSensei installable as a command-line tool.

Install with: pip install -e .
Then use: codesensei --help

Author: Shobin Sebastian
Date: November 2025
"""

from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read README
try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "CodeSensei - AI-Powered Code Analysis Tool"

setup(
    name="codesensei",
    version="0.3.0",
    description="AI-powered code analysis, explanation, and debugging tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shobin Sebastian",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/codesensei",
    
    # Package configuration
    packages=find_packages(),
    include_package_data=True,
    
    # Dependencies
    install_requires=requirements,
    
    # CLI entry point
    entry_points={
        'console_scripts': [
            'codesensei=src.cli.cli:cli',
        ],
    },
    
    # Metadata
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    
    python_requires='>=3.8',
    
    # Keywords
    keywords='code-analysis debugging ai llm static-analysis',
)