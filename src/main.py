#!/usr/bin/env python3
"""
AI Platform Assessment - Main Runner
Demonstrates all four core tasks plus dashboard
"""

import os
import sys
import subprocess
from pathlib import Path

def run_task(task_name: str, script_name: str, description: str):
    """Run a specific task"""
    print(f"\n{'='*60}")
    print(f"TASK: {task_name}")
    print(f"{description}")
    print(f"{'='*60}")
    
    choice = input(f"Run {task_name}? (y/n): ").lower()
    if choice == 'y':
        try:
            subprocess.run([sys.executable, script_name], check=True)
        except KeyboardInterrupt:
            print(f"\n{task_name} interrupted by user")
        except subprocess.CalledProcessError as e:
            print(f"{task_name} failed with error: {e}")
        except FileNotFoundError:
            print(f"Script {script_name} not found")

def main():
    print("AI Platform Assessment")
    print("=" * 60)
    print("This assessment includes 4 core tasks + stretch goal:")
    print("1. Conversational Core (Streaming & Cost Telemetry)")
    print("2. High-Performance Retrieval-Augmented QA")
    print("3. Autonomous Planning Agent with Tool Calling")
    print("4. Self-Healing Code Assistant")
    print("5. Evaluation Dashboard (Stretch Goal)")
    print("=" * 60)
    
    # Check if all files exist
    required_files = [
        "chat.py",
        "rag_system.py", 
        "planning_agent.py",
        "code_assistant.py",
        "dashboard.py"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        print(f"Missing files: {missing_files}")
        return
    
    print("All required files found")
    
    # Task 3.1: Conversational Core
    run_task(
        "3.1 - Conversational Core",
        "chat.py",
        "Chat with streaming responses, message persistence, and cost telemetry"
    )
    
    # Task 3.2: RAG System
    run_task(
        "3.2 - RAG System", 
        "rag_system.py",
        "Document ingestion, vector search, and QA with retrieval evaluation"
    )
    
    # Task 3.3: Planning Agent
    run_task(
        "3.3 - Planning Agent",
        "planning_agent.py", 
        "Autonomous trip planning with tool calling and constraint satisfaction"
    )
    
    # Task 3.4: Code Assistant
    run_task(
        "3.4 - Code Assistant",
        "code_assistant.py",
        "Self-healing code generation with compilation testing and retry logic"
    )
    
    # Stretch Goal: Dashboard
    print(f"\n{'='*60}")
    print("STRETCH GOAL: Evaluation Dashboard")
    print("Streamlit dashboard with metrics visualization")
    print("='*60")
    
    choice = input("Launch dashboard? (y/n): ").lower()
    if choice == 'y':
        print("Starting Streamlit dashboard...")
        print("Dashboard will be available at: http://localhost:8501")
        print("Press Ctrl+C to stop")
        
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"], check=True)
        except KeyboardInterrupt:
            print("\nDashboard stopped")
        except subprocess.CalledProcessError as e:
            print(f"Dashboard failed: {e}")
    
    print("\nAssessment complete!")
    print("\nTo run with Docker:")
    print("  docker-compose up --build")
    print("\nIndividual components can be run directly:")
    for script in required_files:
        print(f"  python {script}")

if __name__ == "__main__":
    main()