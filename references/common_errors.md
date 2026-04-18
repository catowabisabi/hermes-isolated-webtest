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

---

## Plotly Express + Numpy Dependency

**Pattern:** `ImportError: Plotly Express requires numpy to be installed`

**Fix:** Always include `numpy` explicitly in requirements, even when using `"plotly[express]"`:
```bash
pip install "plotly[express]" numpy --break-system-packages
```
When using isolated_webtest.py, always add `numpy` as a separate requirement argument.

---

## JSON Unicode Encoding (WebSocket/API responses)

**Pattern:** Non-ASCII characters (Chinese, etc.) appear as `\uXXXX` in browser or garbled

**Fix:** Always use `ensure_ascii=False` in `json.dumps()`:
```python
# Wrong - non-ASCII becomes \uXXXX
json.dumps({"title": "中文標題"})

# Correct - unicode preserved
json.dumps({"title": "中文標題"}, ensure_ascii=False)

# Helper function pattern:
def json_dumps(data):
    return json.dumps(data, ensure_ascii=False, default=str)
```

**When:** This affects any JSON API that serves data to web frontends (WebSocket, REST API, etc.)

---

## D3.js Graph - Node Labels Show Incomplete Info

**Pattern:** D3 force-directed graph shows source names (e.g. "Yahoo", "BBC") as labels, making nodes unidentifiable

**Fix:** Show the article title instead, truncated:
```javascript
// Wrong - source name is not descriptive enough
nodes.append('text').text(d => d.source.slice(0, 10))

// Correct - show article title as label
nodes.append('text')
    .text(d => d.title.length > 35 ? d.title.slice(0, 35) + '...' : d.title)
    .each(function(d) {
        // Wrap long labels into multiple lines
        if (d.label.length > 30) {
            const words = d.label.split(' ');
            // ... line wrapping logic
        }
    });
```

**Lesson:** Source name alone is not informative enough for news graphs. Always use the article title (truncated) as the visible label.

---

## D3 Graph - Too Many Nodes/Edges

**Pattern:** Graph is a "hairball" - too many overlapping nodes and edges to read

**Fix:** Add a node limit slider and require more shared keywords for edges:
```javascript
// Require 3+ shared keywords (not 2+)
if (shared.length >= 3) {
    edges.push({...});
}

// Add slider control
<input type="range" min="5" max="30" value="15" oninput="updateNodeLimit(+this.value)">
```

**Lesson:** Start with fewer nodes (default 15) and let user adjust. Require 3+ shared keywords prevents noise.

