#!/usr/bin/env python3
"""
test_template.py - Template for creating new webapp tests.
Copy this and customize for your project.
"""
import sys
import os
import subprocess
import time
import shutil
from pathlib import Path

# === CONFIGURATION ===
PROJECT_PATH = ""  # e.g., "/path/to/project"
MAIN_SCRIPT = ""   # e.g., "dashboard/app.py"
PORT = 8050
REQUIREMENTS = ["requests", "dash", "plotly"]  # Packages needed
STARTUP_WAIT = 5  # seconds to wait for app to start
# ===

def create_venv(name):
    env_dir = f"/tmp/test_{name}_{int(time.time())}"
    subprocess.run(["python3", "-m", "venv", env_dir], check=True)
    subprocess.run([f"{env_dir}/bin/pip", "install", "--upgrade", "pip"], check=True)
    if REQUIREMENTS:
        subprocess.run(
            [f"{env_dir}/bin/pip", "install", "--break-system-packages", *REQUIREMENTS],
            check=True
        )
    return env_dir

def run_and_test(env_dir, script_path, work_dir):
    proc = subprocess.Popen(
        [f"{env_dir}/bin/python3", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=work_dir
    )
    
    # Wait for startup
    time.sleep(STARTUP_WAIT)
    
    if proc.poll() is not None:
        _, stderr = proc.communicate()
        return False, f"Process died: {stderr.decode()}"
    
    # === ADD YOUR TESTS HERE ===
    import requests
    try:
        r = requests.get(f"http://localhost:{PORT}", timeout=10)
        if r.status_code != 200:
            return False, f"Bad status: {r.status_code}"
    except Exception as e:
        return False, f"HTTP test failed: {e}"
    # ===
    
    return True, None

def main():
    project = Path(PROJECT_PATH)
    script = project / MAIN_SCRIPT
    
    print(f"Testing {project}...")
    
    # Create env
    env_dir = create_venv(project.name)
    print(f"Venv: {env_dir}")
    
    # Run tests
    success, error = run_and_test(env_dir, str(script), str(project))
    
    # Cleanup
    proc.terminate()
    proc.wait()
    shutil.rmtree(env_dir)
    
    if success:
        print("✅ All tests passed")
        return 0
    else:
        print(f"❌ Test failed: {error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
