# Isolated Web Testing Environment

Automated testing skill for webapps, APIs, and new features using isolated Python venvs. Each test run gets its own clean environment, preventing cross-contamination and resource conflicts.

## Overview

This skill creates isolated venvs for testing. You can:
- Spin up multiple parallel test environments (e.g., Env A for backend, Env B for frontend)
- Test without affecting host system or other projects
- Automatically parse errors and fix common issues
- Report all issues at once after testing completes

## Setup (One-time)

### For the agent (Hermes)

```bash
# Install python3-venv if not available
sudo apt update && sudo apt install python3.12-venv -y

# Create the base testing venv
python3 -m venv ~/.hermes/isolated_test_env

# Activate and install core dependencies
source ~/.hermes/isolated_test_env/bin/activate
pip install --upgrade pip
pip install requests httpx websockets flask-socketio dash plotly anthropic openai feedparser
```

### For new agents cloning the skill

```bash
# Clone the skill
git clone https://github.com/catowabisabi/hermes-isolated-webtest ~/.hermes/skills/isolated-webtest

# Or install via skill_manage
# (Agent will auto-install when loading this skill)
```

## Usage

### Quick Test Workflow

```python
# 1. Load this skill first
# (Agent does this automatically when skill is matched)

# 2. Create isolated test environment
from hermes_tools import terminal
import subprocess

def create_test_env(name, requirements):
    """Create a fresh venv and install packages"""
    env_dir = f"/tmp/hermes_test_{name}"
    
    # Create venv
    subprocess.run(["python3", "-m", "venv", env_dir], check=True)
    
    # Install pip upgrade first
    subprocess.run([f"{env_dir}/bin/pip", "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    subprocess.run([f"{env_dir}/bin/pip", "install", *requirements], check=True)
    
    return env_dir

# 3. Run app in background
import subprocess
import time

def run_app_in_background(env_dir, script_path, port):
    """Start a webapp in background within isolated env"""
    proc = subprocess.Popen(
        [f"{env_dir}/bin/python3", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(script_path)
    )
    time.sleep(3)  # Wait for startup
    return proc

# 4. Test with requests
import requests

def test_endpoint(url, expected_status=200):
    """Test HTTP endpoint"""
    r = requests.get(url, timeout=10)
    return r.status_code == expected_status, r.text

# 5. Capture and parse errors
def get_stderr(proc):
    """Read stderr from background process"""
    import select
    stderr_text = ""
    while True:
        ready, _, _ = select.select([proc.stderr], [], [], 0.1)
        if not ready:
            break
        chunk = os.read(proc.stderr.fileno(), 4096)
        if not chunk:
            break
        stderr_text += chunk.decode()
    return stderr_text
```

### Automated Test Script Template

```python
#!/usr/bin/env python3
"""
isolated_webtest.py - Automated webapp tester
Usage: python3 isolated_webtest.py <project_path> <main_script> <port> [requirements...]
"""
import sys
import os
import subprocess
import time
import requests
import json

def main():
    project_path = sys.argv[1]
    main_script = sys.argv[2]
    port = sys.argv[3]
    requirements = sys.argv[4:] if len(sys.argv) > 4 else []
    
    # Create isolated venv
    env_name = f"test_{int(time.time())}"
    env_dir = f"/tmp/{env_name}"
    
    print(f"🔧 Creating isolated env: {env_name}")
    subprocess.run(["python3", "-m", "venv", env_dir], check=True)
    subprocess.run([f"{env_dir}/bin/pip", "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    if requirements:
        subprocess.run([f"{env_dir}/bin/pip", "install", *requirements], check=True)
    
    # Start app in background
    print(f"🚀 Starting {main_script} on port {port}...")
    full_path = os.path.join(project_path, main_script)
    work_dir = project_path
    
    proc = subprocess.Popen(
        [f"{env_dir}/bin/python3", full_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=work_dir
    )
    
    time.sleep(5)  # Wait for startup
    
    errors = []
    warnings = []
    
    # Test endpoint
    try:
        r = requests.get(f"http://localhost:{port}", timeout=10)
        print(f"✅ HTTP {r.status_code}")
    except Exception as e:
        errors.append(f"HTTP test failed: {e}")
    
    # Capture stderr
    import select
    stderr_lines = []
    while True:
        ready, _, _ = select.select([proc.stderr], [], [], 0.5)
        if not ready:
            break
        chunk = os.read(proc.stderr.fileno(), 4096)
        if not chunk:
            break
        stderr_lines.append(chunk.decode())
    
    stderr_text = "".join(stderr_lines)
    
    # Parse errors
    for line in stderr_lines:
        if "ERROR" in line or "Traceback" in line:
            errors.append(line.strip())
        elif "WARNING" in line:
            warnings.append(line.strip())
    
    # Cleanup
    proc.terminate()
    proc.wait(timeout=5)
    subprocess.run(["rm", "-rf", env_dir])
    
    # Report
    print("\n" + "="*50)
    if errors:
        print(f"❌ {len(errors)} ERROR(S) FOUND:")
        for e in errors:
            print(f"   {e}")
    else:
        print("✅ NO ERRORS")
    
    if warnings:
        print(f"⚠️  {len(warnings)} WARNING(S)")
        for w in warnings[:5]:
            print(f"   {w}")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### CLI Usage

```bash
# Basic test - include numpy explicitly even if using plotly[express]
python3 isolated_webtest.py \
    /path/to/project \
    dashboard/app.py \
    8050 \
    requests \
    dash \
    plotly \
    "plotly[express]" \
    numpy

# Test with full requirements (include numpy!)
python3 isolated_webtest.py \
    /mnt/c/Users/enoma/Desktop/golden_news \
    dashboard/app.py \
    8050 \
    requests \
    httpx \
    dash \
    plotly \
    "plotly[express]" \
    flask-socketio \
    websockets \
    flask \
    feedparser \
    anthropic \
    openai \
    python-dateutil \
    numpy
```

**IMPORTANT:** Always include `numpy` explicitly even when using `"plotly[express]"` as a requirement string. Plotly Express sometimes doesn't pull numpy in automatically on first install, causing `ImportError: Plotly Express requires numpy to be installed`.

## Testing Multiple Environments in Parallel

```python
import subprocess
import time
import requests

def test_backend_and_frontend():
    """Test backend API and frontend simultaneously"""
    
    # Env A - Backend API
    env_a = "/tmp/test_backend"
    subprocess.run(["python3", "-m", "venv", env_a])
    subprocess.run([f"{env_a}/bin/pip", "install", "flask", "requests"])
    
    # Env B - Frontend  
    env_b = "/tmp/test_frontend"
    subprocess.run(["python3", "-m", "venv", env_b])
    subprocess.run([f"{env_b}/bin/pip", "install", "dash", "plotly"])
    
    # Start both in background
    # ... spawn processes ...
    
    # Test cross-env communication
    # Env B's frontend calls Env A's backend API
    
    # Cleanup both
    subprocess.run(["rm", "-rf", env_a, env_b])
```

## Auto-Fix Common Errors

The test script includes auto-detection and fixes for:

| Error | Auto-fix |
|-------|----------|
| `ModuleNotFoundError` | Install missing package |
| `externally-managed-environment` | Use `--break-system-packages` flag |
| `Permission denied` | Set `PYTHONUSERBASE` to `/tmp/...` |
| Port already in use | Kill existing process on port |
| `SyntaxError` | Parse traceback, identify file and line |
| Dash `css.config.links` error | Patch to use `index_string` instead |

## Critical Workflow Rule

**ALWAYS test in isolated env BEFORE asking user to pull.** The correct flow is:

1. **Create isolated venv** (using `isolated_webtest.py`)
2. **Run all tests** until no errors
3. **Fix any issues found** in the isolated env
4. **Commit ONCE** when everything passes
5. **Then notify user** to pull

**NEVER**: change → ask user to pull → wait for error → repeat

This prevents wasting the user's time on preventable errors.

## Error Handling

When tests fail:
- Parse all errors from stderr
- Attempt auto-fix for known patterns
- Re-test in isolated env
- Only commit when tests pass completely

## File Structure

```
~/.hermes/skills/isolated-webtest/
├── SKILL.md                    # This file
├── scripts/
│   ├── isolated_webtest.py    # Main test runner
│   ├── env_manager.py         # Venv creation/destruction helpers
│   └── parse_errors.py        # Error parsing utilities
├── templates/
│   └── test_template.py       # Template for new test scripts
└── references/
    ├── common_errors.md       # Known errors and fixes
    └── python_packages.md      # Package installation notes
```

## Dependencies to Install in Base Env

```bash
pip install requests httpx websockets flask flask-socketio dash plotly anthropic openai feedparser python-dateutil
```

## Notes

- Venvs are always created in `/tmp/` to avoid disk pollution
- Always set `check=True` on subprocess calls to catch venv creation failures
- Use `select.select()` for non-blocking stderr reads
- Set reasonable timeouts (5-10s) for HTTP tests
- Always call `proc.terminate()` and `proc.wait()` to avoid zombie processes
- After testing, delete the venv with `rm -rf` to reclaim disk space
