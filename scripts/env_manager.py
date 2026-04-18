#!/usr/bin/env python3
"""
env_manager.py - Venv creation/destruction helper for isolated testing.
Provides clean API for creating and managing test environments.
"""
import os
import subprocess
import shutil
import time
from pathlib import Path

class IsolatedEnv:
    """Manages an isolated Python venv for testing."""
    
    def __init__(self, name=None, requirements=None):
        self.name = name or f"test_{int(time.time())}"
        self.requirements = requirements or []
        self.env_dir = f"/tmp/hermes_test_{self.name}"
        self.active = False
    
    def create(self):
        """Create the venv and install requirements."""
        # Clean up if exists
        if os.path.exists(self.env_dir):
            shutil.rmtree(self.env_dir)
        
        # Create venv
        result = subprocess.run(
            ["python3", "-m", "venv", self.env_dir],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create venv: {result.stderr}")
        
        # Upgrade pip
        subprocess.run(
            [self.pip, "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Install requirements
        if self.requirements:
            result = subprocess.run(
                [self.pip, "install", "--break-system-packages", *self.requirements],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                raise RuntimeError(f"Failed to install packages: {result.stderr}")
        
        self.active = True
        return self
    
    @property
    def python(self):
        return f"{self.env_dir}/bin/python3"
    
    @property
    def pip(self):
        return f"{self.env_dir}/bin/pip"
    
    def run(self, script, cwd=None, timeout=None, capture=True):
        """Run a Python script in this venv."""
        if not self.active:
            raise RuntimeError("Venv not active. Call create() first.")
        
        result = subprocess.run(
            [self.python, script],
            capture_output=capture,
            text=True,
            cwd=cwd,
            timeout=timeout
        )
        return result
    
    def install(self, *packages):
        """Install additional packages."""
        if not self.active:
            raise RuntimeError("Venv not active.")
        
        result = subprocess.run(
            [self.pip, "install", "--break-system-packages", *packages],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            raise RuntimeError(f"Install failed: {result.stderr}")
        return self
    
    def cleanup(self):
        """Remove the venv."""
        if os.path.exists(self.env_dir):
            shutil.rmtree(self.env_dir)
        self.active = False
    
    def __enter__(self):
        return self.create()
    
    def __exit__(self, *args):
        self.cleanup()


def create_test_env(name, requirements=None):
    """Convenience function to create a single test env."""
    env = IsolatedEnv(name, requirements)
    env.create()
    return env


if __name__ == "__main__":
    # Demo usage
    print("Creating isolated env...")
    with IsolatedEnv("demo", ["requests", "httpx"]) as env:
        print(f"  Python: {env.python}")
        result = env.run("-c", "import requests; print('requests OK')")
        print(f"  Result: {result.stdout.strip()}")
    print("  Env cleaned up.")
