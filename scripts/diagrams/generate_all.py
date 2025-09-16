#!/usr/bin/env python3
"""Generates all diagrams by importing each module."""
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the repository root (two levels up from scripts/diagrams/)
repo_root = os.path.dirname(os.path.dirname(script_dir))

# Add repo root to Python path
sys.path.insert(0, repo_root)

# Change to the repo root directory so relative paths work
os.chdir(repo_root)

# Now import each diagram module directly
try:
    import scripts.diagrams.network
    print("Generated network diagram")
except Exception as e:
    print(f"Error generating network diagram: {e}")

try:
    import scripts.diagrams.security
    print("Generated security diagram")
except Exception as e:
    print(f"Error generating security diagram: {e}")

try:
    import scripts.diagrams.integration
    print("Generated integration diagram")
except Exception as e:
    print(f"Error generating integration diagram: {e}")

try:
    import scripts.diagrams.data
    print("Generated data diagram")
except Exception as e:
    print(f"Error generating data diagram: {e}")

print("Diagrams generated into docs/diagrams")