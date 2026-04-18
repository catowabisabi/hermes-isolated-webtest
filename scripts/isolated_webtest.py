#!/usr/bin/env python3
"""
isolated_webtest.py - Automated webapp tester for Hermes Agent
Tests webapps/APIs in isolated venv with full error reporting.

Usage:
    python3 isolated_webtest.py <project_path> <main_script> <port> [requirements...]

Example:
    python3 isolated_webtest.py \
        /mnt/c/Users/enoma/Desktop/golden_news \
        dashboard/app.py \
        8050 \
        requests \
        dash \
        plotly

Exit codes: 0 = success, 1 = errors found
"""
import sys
import os
import subprocess
import time
import tempfile
import shutil
import signal

def create_venv(env_name, requirements):
    """Create isolated venv and install packages."""
    env_dir = f"/tmp/hermes_test_{env_name}"
    
    # Remove if exists
    if os.path.exists(env_dir):
        shutil.rmtree(env_dir)
    
    # Create venv
    result = subprocess.run(
        ["python3", "-m", "venv", env_dir],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return None, f"Failed to create venv: {result.stderr}"
    
    # Upgrade pip
    pip_result = subprocess.run(
        [f"{env_dir}/bin/pip", "install", "--upgrade", "pip"],
        capture_output=True,
        text=True,
        timeout=120
    )
    if pip_result.returncode != 0:
        return None, f"Failed to upgrade pip: {pip_result.stderr}"
    
    # Install requirements
    if requirements:
        install_result = subprocess.run(
            [f"{env_dir}/bin/pip", "install", "--break-system-packages", *requirements],
            capture_output=True,
            text=True,
            timeout=300
        )
        if install_result.returncode != 0:
            return None, f"Failed to install packages: {install_result.stderr}"
    
    return env_dir, None

def run_app(env_dir, script_path, work_dir, startup_timeout=8):
    """Run app in background and capture errors."""
    proc = subprocess.Popen(
        [f"{env_dir}/bin/python3", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=work_dir,
        text=True,
        bufsize=1
    )
    
    # Wait for startup
    time.sleep(startup_timeout)
    
    # Check if still running
    if proc.poll() is not None:
        # Process died
        _, stderr = proc.communicate()
        return proc, None, f"Process exited with code {proc.returncode}\n{stderr}"
    
    return proc, None, None

def test_http(url, timeout=10):
    """Test HTTP endpoint."""
    try:
        import requests
        r = requests.get(url, timeout=timeout)
        return True, r.status_code, None
    except Exception as e:
        return False, None, str(e)

def capture_output(proc, timeout=2):
    """Capture all stderr/stdout from process."""
    outputs = {"stdout": [], "stderr": []}
    start = time.time()
    
    while time.time() - start < timeout:
        # Check stdout
        ready = []
        try:
            import select
            ready, _, _ = select.select([proc.stdout, proc.stderr], [], [], 0.5)
        except:
            break
        
        for stream in ready:
            import select
            try:
                ready_s, _, _ = select.select([stream], [], [], 0.1)
                if stream in ready_s:
                    chunk = os.read(stream.fileno(), 4096)
                    if chunk:
                        decoded = chunk.decode('utf-8', errors='replace')
                        if stream == proc.stderr:
                            outputs["stderr"].append(decoded)
                        else:
                            outputs["stdout"].append(decoded)
            except:
                break
        
        if not ready:
            break
    
    return "".join(outputs["stderr"]), "".join(outputs["stdout"])

def parse_errors(stderr, stdout):
    """Parse errors from output."""
    errors = []
    warnings = []
    
    for line in stderr.split("\n"):
        if not line.strip():
            continue
        if "ERROR" in line or "Traceback" in line or "Exception" in line or "Error:" in line:
            errors.append(line.strip())
        elif "WARNING" in line or "DeprecationWarning" in line:
            warnings.append(line.strip())
    
    # Also check stdout for Python errors
    for line in stdout.split("\n"):
        if not line.strip():
            continue
        if "Traceback" in line or "SyntaxError" in line or "ModuleNotFoundError" in line:
            errors.append(line.strip())
    
    return errors, warnings

def cleanup(proc, env_dir):
    """Clean up process and venv."""
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
    
    if env_dir and os.path.exists(env_dir):
        shutil.rmtree(env_dir)

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 isolated_webtest.py <project_path> <main_script> <port> [requirements...]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    main_script = sys.argv[2]
    port = sys.argv[3]
    requirements = sys.argv[4:] if len(sys.argv) > 4 else []
    
    env_name = f"{int(time.time())}"
    full_script_path = os.path.join(project_path, main_script)
    url = f"http://localhost:{port}"
    
    print(f"🔧 Isolated Web Tester")
    print(f"   Project: {project_path}")
    print(f"   Script: {main_script}")
    print(f"   Port: {port}")
    print(f"   Requirements: {', '.join(requirements) if requirements else 'none'}")
    print()
    
    # Create venv
    print(f"📦 Creating isolated venv...")
    env_dir, err = create_venv(env_name, requirements)
    if err:
        print(f"❌ {err}")
        sys.exit(1)
    print(f"   ✅ Venv: {env_dir}")
    
    # Start app
    print(f"🚀 Starting app...")
    proc, _, start_err = run_app(env_dir, full_script_path, project_path)
    if start_err:
        print(f"❌ Startup failed: {start_err}")
        cleanup(proc, env_dir)
        sys.exit(1)
    print(f"   ✅ App started (PID: {proc.pid})")
    
    # HTTP test
    print(f"🌐 Testing HTTP endpoint...")
    http_ok, status, http_err = test_http(url)
    if http_ok:
        print(f"   ✅ HTTP {status}")
    else:
        print(f"   ⚠️  HTTP failed: {http_err}")
    
    # Capture output
    print(f"📋 Capturing output...")
    stderr, stdout = capture_output(proc, timeout=3)
    
    # Parse errors
    errors, warnings = parse_errors(stderr, stdout)
    
    # Cleanup
    print(f"🧹 Cleaning up...")
    cleanup(proc, env_dir)
    
    # Report
    print()
    print("=" * 60)
    
    if errors:
        print(f"❌ {len(errors)} ERROR(S) FOUND:")
        for e in errors:
            print(f"   {e}")
        print()
    
    if warnings:
        print(f"⚠️  {len(warnings)} WARNING(S):")
        for w in warnings[:3]:
            print(f"   {w}")
        print()
    
    if not errors:
        print("✅ ALL TESTS PASSED - No errors detected")
    
    if stderr:
        print("--- Full stderr ---")
        print(stderr[:2000])
    
    print()
    print(f"Env cleaned up: {env_dir}")
    
    sys.exit(0 if not errors else 1)

if __name__ == "__main__":
    main()
