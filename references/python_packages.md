# Python Package Notes

## Dash / Plotly Installation

```bash
pip install dash plotly "dash[extra-components]"
pip install "plotly[express]"  # Requires numpy
```

**Note:** Python 3.14+ may have numpy compatibility issues with older plotly versions. If you see `numpy` import errors, try:
```bash
pip install numpy --upgrade
pip install plotly --upgrade
```

---

## WebSocket Packages

```bash
pip install websockets asyncio
```

For Flask-SocketIO:
```bash
pip install flask-socketio
```

---

## API Testing Packages

```bash
pip install requests httpx  # httpx supports async
pip install aiohttp          # For async HTTP tests
```

---

## Feedparser (RSS)

```bash
pip install feedparser
```

On externally-managed environments:
```bash
pip install feedparser --break-system-packages
```

---

## Anthropic / OpenAI SDKs

```bash
pip install anthropic openai
```

Note: MiniMax uses Anthropic SDK format:
```python
import anthropic
client = anthropic.Anthropic(
    base_url='https://api.minimax.io/anthropic',
    api_key='sk-cp-ml_...'
)
```

---

## Database

SQLite is built-in. No installation needed.

For PostgreSQL:
```bash
pip install psycopg2-binary
```

---

## Recommended Test Packages

```bash
pip install pytest pytest-asyncio
pip install playwright  # For browser automation
playwright install chromium
```
