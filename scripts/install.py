#!/usr/bin/env python3
"""
install.py - Auto-install script for hermes-isolated-webtest skill.

Usage:
    # One-line install (from anywhere):
    python3 -c "
    import urllib.request;
    exec(urllib.request.urlopen('https://raw.githubusercontent.com/catowabisabi/hermes-isolated-webtest/main/scripts/install.py').read().decode())
    "

    # Or clone and run locally:
    git clone https://github.com/catowabisabi/hermes-isolated-webtest /tmp/hermes-webtest
    python3 /tmp/hermes-webtest/scripts/install.py
"""
import os
import sys
import subprocess
import urllib.request

SKILL_DIR = os.path.expanduser("~/.hermes/skills/isolated-webtest")
REPO_URL = "https://github.com/catowabisabi/hermes-isolated-webtest.git"
MAIN_BRANCH = "main"

def run(cmd, check=True, capture=True):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"   {result.stderr}")
        sys.exit(1)
    return result

def check_python_venv():
    """Check if python3-venv is available."""
    result = run("python3 -m venv --help", check=False)
    if result.returncode != 0:
        print("⚠️  python3-venv not found. Install with:")
        print("    sudo apt update && sudo apt install python3.12-venv -y")
        return False
    print("✅ python3-venv available")
    return True

def create_hermes_dir():
    """Create ~/.hermes/skills directory if needed."""
    skills_dir = os.path.dirname(SKILL_DIR)
    if not os.path.exists(sKILLS_DIR):
        os.makedirs(skills_dir, exist_ok=True)
        print(f"✅ Created {skills_dir}")
    else:
        print(f"✅ {skills_dir} exists")

def clone_or_update():
    """Clone or update the skill repo."""
    if os.path.exists(SKILL_DIR):
        print(f"🔄 Updating existing skill at {SKILL_DIR}")
        run(f"cd {SKILL_DIR} && git pull origin {MAIN_BRANCH}")
    else:
        print(f"📦 Cloning {REPO_URL}")
        run(f"git clone {REPO_URL} {SKILL_DIR}")
    print(f"✅ Skill installed at {SKILL_DIR}")

def make_scripts_executable():
    """Make all Python scripts executable."""
    for root, dirs, files in os.walk(SKILL_DIR):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                os.chmod(path, 0o755)
                print(f"   chmod +x {path}")

def install_base_packages():
    """Install base packages in the test venv."""
    base_venv = os.path.expanduser("~/.hermes/isolated_test_env")
    
    if os.path.exists(base_venv):
        print(f"🔄 Base venv exists at {base_venv}")
    else:
        print(f"📦 Creating base testing venv...")
        run(f"python3 -m venv {base_venv}")
    
    print(f"📦 Upgrading pip...")
    run(f"{base_venv}/bin/pip install --upgrade pip")
    
    print(f"📦 Installing core test packages...")
    run(f"{base_venv}/bin/pip install --break-system-packages requests httpx websockets flask-socketio dash plotly")
    print(f"✅ Core packages installed")

def verify():
    """Verify installation."""
    print("\n🔍 Verifying installation...")
    
    # Check files exist
    required = ["SKILL.md", "scripts/isolated_webtest.py", "scripts/env_manager.py", "scripts/parse_errors.py"]
    for f in required:
        path = os.path.join(SKILL_DIR, f)
        if os.path.exists(path):
            print(f"   ✅ {f}")
        else:
            print(f"   ❌ {f} missing")
            return False
    
    # Check base venv
    base_venv = os.path.expanduser("~/.hermes/isolated_test_env")
    if os.path.exists(base_venv):
        print(f"   ✅ Base venv exists")
    else:
        print(f"   ⚠️  Base venv not created (may need manual setup)")
    
    return True

def main():
    print("🔧 Hermes Isolated Web Testing Skill - Installer")
    print("=" * 50)
    
    print("\n📋 Prerequisites:")
    check_python_venv()
    
    print("\n📁 Installing skill:")
    create_hermes_dir()
    clone_or_update()
    make_scripts_executable()
    
    print("\n📦 Installing base packages:")
    install_base_packages()
    
    if verify():
        print("\n" + "=" * 50)
        print("✅ Installation complete!")
        print(f"\nSkill location: {SKILL_DIR}")
        print(f"Base venv: ~/.hermes/isolated_test_env")
        print("\n📖 See SKILL.md for usage instructions")
    else:
        print("\n❌ Installation verification failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
