"""
Entry point script to run the property dashboard
"""
import os
import sys
import subprocess

def run_dashboard():
    """Run the Streamlit dashboard"""
    # Get the path to the main app file
    project_root = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(project_root, "app", "streamlit_dashboard.py")
    
    # Ensure the correct Python executable is used
    python_executable = sys.executable
    
    print(f"Starting dashboard using Python: {python_executable}")
    print(f"Dashboard path: {app_path}")
    
    # Run Streamlit
    cmd = [python_executable, "-m", "streamlit", "run", app_path]
    subprocess.run(cmd)

if __name__ == "__main__":
    run_dashboard()
