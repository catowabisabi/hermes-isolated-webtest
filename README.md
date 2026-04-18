# Hermes Isolated Web Testing Skill

Automated testing skill for webapps, APIs, and new features using isolated Python venvs. For Hermes Agent.

## For Agents - Auto Install

```bash
# One-line install for Hermes Agent
python3 -c "
import urllib.request; 
exec(urllib.request.urlopen('https://raw.githubusercontent.com/catowabisabi/hermes-isolated-webtest/main/scripts/install.py').read().decode())
"
```

Or clone manually:
```bash
git clone https://github.com/catowabisabi/hermes-isolated-webtest ~/.hermes/skills/isolated-webtest
```

## What This Does

This skill lets Hermes Agent test webapps/APIs in fully isolated Python venvs. Each test gets its own clean environment, preventing cross-contamination.

**Features:**
- Create isolated venv per test run
- Test webapps without affecting host system
- Parallel test environments (Env A for backend, Env B for frontend)
- Auto-parse errors and suggest fixes
- Full error reporting before making changes
- Automatic cleanup of test environments

## File Structure

```
hermes-isolated-webtest/
├── SKILL.md                    # Main skill documentation
├── scripts/
│   ├── isolated_webtest.py    # Main test runner
│   ├── env_manager.py         # Venv creation/destruction
│   ├── parse_errors.py        # Error parsing utilities
│   └── install.py             # Auto-install script
├── templates/
│   └── test_template.py       # Template for new tests
└── references/
    ├── common_errors.md       # Known errors and fixes
    └── python_packages.md      # Package installation notes
```

## Quick Start

```bash
# Test a Dash app
python3 isolated_webtest.py /path/to/project dashboard/app.py 8050 requests dash plotly

# Test an API
python3 isolated_webtest.py /path/to/api src/api_server.py 5000 flask requests

# Custom requirements
python3 isolated_webtest.py /path/to/project app.py 8080 requests httpx websockets flask
```

## Usage in Hermes

When loading this skill, Hermes will:

1. Create an isolated venv for the test
2. Install required packages
3. Start the webapp in background
4. Run HTTP tests against the endpoint
5. Capture all stderr/stdout
6. Parse errors and suggest auto-fixes
7. Report all issues at once
8. Clean up the venv

This means Hermes can test a webapp fully before reporting back, rather than the slow iterate-and-fix cycle.

## Setup (One-time)

```bash
# Install python3-venv if not available
sudo apt update && sudo apt install python3.12-venv -y

# Create base testing venv
python3 -m venv ~/.hermes/isolated_test_env
source ~/.hermes/isolated_test_env/bin/activate
pip install --upgrade pip
pip install requests httpx websockets flask-socketio dash plotly

# Or run the install script
python3 scripts/install.py
```

## For Developers

### Adding New Error Patterns

Edit `scripts/parse_errors.py` and add to `AUTO_FIXES`:
```python
"MyNewError": {
    "pattern": r"MyNewError: (.*)",
    "fix": "How to fix it"
}
```

### Creating Test Scripts

Copy `templates/test_template.py` and customize the test logic.

## License

MIT
