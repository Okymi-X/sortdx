#!/usr/bin/env python3
"""
Setup script for sortx development.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up sortx development environment")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    print(f"📁 Working directory: {project_dir}")
    
    # Install in editable mode
    if not run_command(
        f'pip install -e ".[dev]"', 
        "Installing sortx in development mode"
    ):
        print("❌ Failed to install package")
        return 1
    
    # Run basic tests to verify installation
    if not run_command("python -c \"import sortx; print('✅ sortx import successful')\"", "Testing basic import"):
        print("❌ Failed basic import test")
        return 1
    
    # Run the development test script
    if not run_command("python dev_test.py", "Running development tests"):
        print("❌ Development tests failed")
        return 1
    
    # Run pytest if available
    try:
        import pytest
        if not run_command("pytest tests/ -v", "Running pytest"):
            print("⚠️ Some tests failed, but continuing...")
    except ImportError:
        print("⚠️ pytest not available, skipping unit tests")
    
    # Test CLI
    if not run_command("python -m sortx --help", "Testing CLI help"):
        print("❌ CLI test failed")
        return 1
    
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("="*50)
    print("\n📋 Next steps:")
    print("1. Run 'python -m sortx --help' to see CLI options")
    print("2. Run 'python -m sortx examples' to see usage examples")
    print("3. Try sorting sample data: 'python -m sortx tests/data/sample.csv -o output.csv -k price:num'")
    print("4. Run 'pytest' for full test suite")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
