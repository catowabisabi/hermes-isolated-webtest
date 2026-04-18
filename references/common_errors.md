# Common Errors and Auto-Fixes

## ModuleNotFoundError

**Pattern:** `ModuleNotFoundError: No module named 'xyz'`

**Fix:** 
```bash
pip install xyz --break-system-packages
```

**Or in venv:**
```bash
/path/to/venv/bin/pip install xyz
```

---

## externally-managed-environment

**Pattern:** `This environment is externally managed`

**Fix:** Add `--break-system-packages` flag:
```bash
pip install xyz --break-system-packages
```

---

## Dash css.config.links AttributeError

**Pattern:** `AttributeError: 'ResourceConfig' object has no attribute 'links'`

**Fix:** Replace:
```python
app.css.config.links.append({"rel": "stylesheet", "href": "..."})
```

With:
```python
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%css%}
    <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
'''
```

---

## Plotly 8-char Hex Color

**Pattern:** `Invalid value of type 'builtins.str' received for 'color' property... Received value: '#ffd70044'`

**Fix:** Use 6-char hex only:
```python
color="#ffd700"  # NOT "#ffd70044"
```

Or use rgba:
```python
color="rgba(255, 215, 0, 0.5)"
```

---

## SQLite Connection Issues

**Pattern:** `sqlite3.OperationalError: database is locked`

**Fix:** Ensure you close connections properly:
```python
db.close()  # Always close after use
```

---

## Port Already In Use

**Pattern:** `OSError: [Errno 98] Address already in use`

**Fix:**
```bash
# Find process on port
lsof -i :8050

# Kill it
kill -9 <PID>
```

---

## Cursor Description None

**Pattern:** `cursor.description` returns all `None`

**Fix:** Use `cursor.description` from the actual query cursor, not a separate `SELECT *`:
```python
# Wrong:
cols = [desc[0] for desc in db.execute("SELECT * FROM table").description]

# Correct:
cursor = db.execute("SELECT col1, col2 FROM table")
cols = [d[0] for d in cursor.description]
```

---

## WebSocket Connection Refused

**Pattern:** `ConnectionRefusedError: [Errno 111] Connection refused`

**Fix:** 
1. Ensure WebSocket server is running
2. Check the port matches
3. Check firewall settings
4. For Dash, use `http://localhost:` not `ws://localhost:` for initial load

---

## Python 3.14+ Compatibility

**Pattern:** Various import/attribute errors on Python 3.14+

**Fix:** Python 3.14 has stricter defaults. Some older packages may need:
```bash
pip install --upgrade --force-reinstall <package>
```

Or use Python 3.12 if available.
