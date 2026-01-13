#!/usr/bin/env python3
"""
Simple script to run pytest with proper configuration
"""
import subprocess
import sys
import os

def main():
    """Run pytest with the project configuration"""
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Add src to Python path
    env = os.environ.copy()
    pythonpath = env.get('PYTHONPATH', '')
    src_path = os.path.join(project_dir, 'src')
    env['PYTHONPATH'] = f"{src_path}:{pythonpath}" if pythonpath else src_path
    
    # Run pytest with verbose output
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    
    # Add any additional arguments passed to this script
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    print("Running pytest...")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    # Run the command
    result = subprocess.run(cmd, env=env)
    
    # Exit with the same code as pytest
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()