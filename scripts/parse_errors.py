#!/usr/bin/env python3
"""
parse_errors.py - Error parsing utilities for Python tracebacks.
Extracts actionable error information from stderr/tracebacks.
"""
import re
import os

# Common error patterns and their auto-fixes
AUTO_FIXES = {
    "ModuleNotFoundError": {
        "pattern": r"ModuleNotFoundError: No module named '(\w+)'",
        "fix": "pip install {module} --break-system-packages"
    },
    "SyntaxError": {
        "pattern": r"File \"([^\"]+)\", line (\d+)",
        "fix": "Check file {file} line {line}"
    },
    "externally-managed-environment": {
        "pattern": "externally-managed-environment",
        "fix": "pip install --break-system-packages"
    },
    "css.config.links": {
        "pattern": "AttributeError.*css.*config.*links",
        "fix": "Use app.index_string instead of app.css.config.links"
    },
    "plotly 8-char hex": {
        "pattern": "Invalid value.*8 characters.*color",
        "fix": "Remove alpha from hex color (use 6-char hex)"
    },
}

class ErrorReport:
    """Structured error report."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.fixes = []
    
    def add_error(self, error_type, message, file=None, line=None, fix=None):
        self.errors.append({
            "type": error_type,
            "message": message,
            "file": file,
            "line": line,
            "fix": fix or self._suggest_fix(error_type)
        })
    
    def add_warning(self, warning):
        self.warnings.append(warning)
    
    def _suggest_fix(self, error_type):
        fix_info = AUTO_FIXES.get(error_type, {})
        return fix_info.get("fix", "Manual inspection required")
    
    def summary(self):
        return {
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        }


def parse_traceback(text):
    """Parse Python traceback and extract errors."""
    report = ErrorReport()
    lines = text.split("\n")
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # ModuleNotFoundError
        if "ModuleNotFoundError" in line:
            match = re.search(r"No module named '(\w+)'", line)
            if match:
                module = match.group(1)
                report.add_error(
                    "ModuleNotFoundError",
                    f"Missing module: {module}",
                    fix=f"pip install {module} --break-system-packages"
                )
        
        # SyntaxError
        elif "SyntaxError" in line:
            match = re.search(r'File "([^"]+)", line (\d+)', line)
            if match:
                report.add_error(
                    "SyntaxError",
                    line,
                    file=match.group(1),
                    line=int(match.group(2))
                )
        
        # Generic Error
        elif line.startswith("Error:") or line.startswith("Exception:"):
            report.add_error("GenericError", line)
        
        # Traceback header - capture next few lines
        elif line == "Traceback (most recent call last):":
            # Get the file/line context
            for j in range(i+1, min(i+5, len(lines))):
                tline = lines[j].strip()
                match = re.search(r'File "([^"]+)", line (\d+)', tline)
                if match:
                    report.add_error(
                        "Traceback",
                        tline,
                        file=match.group(1),
                        line=int(match.group(2))
                    )
                    break
        
        # Dash/CSS errors
        elif "css.config.links" in line:
            report.add_error(
                "DashCSSError",
                line,
                fix="Replace app.css.config.links with app.index_string for Google Fonts"
            )
        
        # Plotly color error
        elif "Invalid value" in line and "color" in line.lower():
            report.add_error(
                "PlotlyColorError",
                line,
                fix="Use 6-char hex color (e.g. '#ff0000') instead of 8-char (e.g. '#ff000044')"
            )
        
        # Warning patterns
        elif "WARNING" in line or "DeprecationWarning" in line:
            report.add_warning(line)
        
        i += 1
    
    return report


if __name__ == "__main__":
    # Test with sample traceback
    sample = """
Traceback (most recent call last):
  File "/path/to/app.py", line 123, in update_graph
    fig.add_trace(go.Scatter(
  File "/path/to/scatter.py", line 456
    line=dict(color='#ffd70044')
ValueError: Invalid 8-char hex color
    """
    report = parse_traceback(sample)
    print("Errors found:", len(report.errors))
    for e in report.errors:
        print(f"  {e['type']}: {e['fix']}")
