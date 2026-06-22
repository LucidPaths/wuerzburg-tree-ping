# Dashboard / visualizer

A dependency-free localhost dashboard for the Würzburg OpenData demos.

It gives the demo one visual surface instead of seven terminal windows:

- tree watering sensor alerts
- parking status
- bike counter pulse
- pedestrian downtown pulse
- waste pickup reminders
- nearby accessible toilets
- ZDI/event digest

## Run live dashboard

From repo root:

```bash
python dashboard/app.py
```

Open:

```text
http://127.0.0.1:8765/
```

The browser calls:

```text
/api/snapshot
```

That reruns the local Python collectors against `opendata.wuerzburg.de` and redraws the cards.

## OpenData chatbox

The dashboard also exposes a small Ollama-backed chatbox scoped to the current dashboard snapshot.

Set one of these on the machine running the dashboard:

```bash
export OLLAMA_API_KEY="<your-key>"
export OLLAMA_BASE_URL="https://ollama.com/v1"  # Ollama Cloud / OpenAI-compatible endpoint
export OLLAMA_MODEL="gpt-oss:20b"
```

On Windows CMD:

```bat
set OLLAMA_API_KEY=<your-key>
set OLLAMA_BASE_URL=https://ollama.com/v1
set OLLAMA_MODEL=gpt-oss:20b
```

Then run:

```bash
python dashboard/app.py
```

The key stays server-side. The browser only calls local `/api/chat`; it never receives the key.

For presentation mode, the page also has a **Connect your AI** form. Paste the Ollama API key there instead of setting environment variables; the browser sends it to the localhost Python server once, the server keeps it only in process memory, and the key is never written to disk or echoed back.

If `OLLAMA_API_KEY` is absent and no browser key was connected, the dashboard tries local Ollama at `http://127.0.0.1:11434/api/chat`.

If port `8765` is already in use, run the dashboard on another port:

```bash
python dashboard/app.py --port 8870
```

Then open `http://127.0.0.1:8870/`.

Optional controls:

- `district` filters the waste calendar, e.g. `Grombühl`
- `lat` / `lon` changes the accessible-toilet search point

## Generate static fallback

For offline-ish demos or screenshots:

```bash
python dashboard/generate_dashboard.py
```

Open:

```text
dashboard/index.html
```

The static HTML embeds the last collected snapshot. The live localhost mode is better for the actual presentation.
