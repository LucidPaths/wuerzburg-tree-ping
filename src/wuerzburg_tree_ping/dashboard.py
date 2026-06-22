from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
import argparse
import json
import os
import sys
import traceback
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wuerzburg_tree_ping import bike, cli, events, parking, pedestrian, toilets, waste

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


CardBuilder = Callable[[], dict[str, Any]]


def utc_now_label() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def item_dict(item: Any) -> dict[str, Any]:
    if is_dataclass(item):
        return asdict(item)
    if isinstance(item, dict):
        return dict(item)
    return {"title": str(item), "body": ""}


def ping_items(items: list[Any]) -> list[dict[str, Any]]:
    return [item_dict(item) for item in items]


def text_card(
    *,
    key: str,
    title: str,
    icon: str,
    folder: str,
    dataset_ids: list[str],
    pitch: str,
    items: list[Any],
    metric_label: str,
    value: int | float | str | None = None,
    status: str = "ok",
) -> dict[str, Any]:
    normalized = ping_items(items)
    if value is None:
        value = len(normalized)
    return {
        "key": key,
        "title": title,
        "icon": icon,
        "folder": folder,
        "datasets": dataset_ids,
        "pitch": pitch,
        "metricLabel": metric_label,
        "value": value,
        "status": status,
        "items": normalized,
    }


def tree_card() -> dict[str, Any]:
    alerts = cli.build_alerts()
    critical = sum(1 for alert in alerts if alert.severity == "critical")
    status = "critical" if critical else "watch" if alerts else "ok"
    return text_card(
        key="trees",
        title="Tree watering ping",
        icon="🌳",
        folder="usecases/tree-watering-ping",
        dataset_ids=[cli.DATASETS["climate_trees"], cli.DATASETS["garden_soil"], cli.DATASETS["water_barrels"]],
        pitch="Watches tree and climate-garden sensors for dry soil or low water storage.",
        items=alerts[:8],
        metric_label="sensor alerts",
        status=status,
    )


def parking_card() -> dict[str, Any]:
    statuses = parking.latest_per_parking(parking.fetch_latest())
    blocked = [s for s in statuses if s.status.lower() in {"belegt", "fast voll", "voll"}]
    free = [s for s in statuses if s.status.lower() == "frei"]
    items = [
        {"title": status.name, "body": status.status, "timestamp": status.values_from}
        for status in statuses[:18]
    ]
    status = "critical" if blocked else "ok"
    card = text_card(
        key="parking",
        title="Parking situation",
        icon="🅿️",
        folder="usecases/parking-ping",
        dataset_ids=[parking.DATASET_ID],
        pitch="Checks garage status so people can avoid full parking before driving into town.",
        items=items,
        metric_label="blocked / full",
        value=len(blocked),
        status=status,
    )
    card["secondary"] = {"label": "free options", "value": len(free)}
    return card


def bike_card() -> dict[str, Any]:
    items = bike.build_items()
    top_count = 0
    if items:
        # body starts with "1,234 counted bicycles..."; keep parsing best-effort for visualization only.
        digits = "".join(ch for ch in items[0].body.split(" counted", 1)[0] if ch.isdigit())
        top_count = int(digits or 0)
    return text_card(
        key="bike",
        title="Bike counter pulse",
        icon="🚲",
        folder="usecases/bike-counter-pulse",
        dataset_ids=[bike.DATASET_ID],
        pitch="Ranks the busiest bike counter stations from the latest available sample.",
        items=items,
        metric_label="top count",
        value=top_count,
        status="ok" if items else "empty",
    )


def pedestrian_card() -> dict[str, Any]:
    items = pedestrian.build_items()
    top_count = 0
    if items:
        digits = "".join(ch for ch in items[0].body.split(" pedestrians", 1)[0] if ch.isdigit())
        top_count = int(digits or 0)
    return text_card(
        key="pedestrian",
        title="Downtown pedestrian pulse",
        icon="🚶",
        folder="usecases/pedestrian-downtown-pulse",
        dataset_ids=[pedestrian.DATASET_ID],
        pitch="Shows where downtown foot traffic is strongest in the latest pedestrian counts.",
        items=items,
        metric_label="top count",
        value=top_count,
        status="ok" if items else "empty",
    )


def waste_card(district: str | None = None) -> dict[str, Any]:
    items = waste.build_items(district=district)
    district_label = f" for {district}" if district else ""
    return text_card(
        key="waste",
        title="Waste pickup reminder",
        icon="🗑️",
        folder="usecases/waste-pickup-reminder",
        dataset_ids=[waste.DATASET_ID],
        pitch=f"Lists upcoming waste pickups{district_label}; useful as a reminder bot demo.",
        items=items,
        metric_label="upcoming pickups",
        status="ok" if items else "empty",
    )


def toilets_card(lat: float = toilets.DEFAULT_LAT, lon: float = toilets.DEFAULT_LON) -> dict[str, Any]:
    items = toilets.build_items(lat=lat, lon=lon)
    return text_card(
        key="toilets",
        title="Accessible toilets nearby",
        icon="♿",
        folder="usecases/accessible-toilets-helper",
        dataset_ids=[toilets.DATASET_ID],
        pitch=f"Finds nearby barrier-free toilets around {lat:.4f}, {lon:.4f}.",
        items=items,
        metric_label="nearby places",
        status="ok" if items else "empty",
    )


def events_card() -> dict[str, Any]:
    items = events.build_items()
    return text_card(
        key="events",
        title="ZDI event digest",
        icon="📅",
        folder="usecases/zdi-event-digest",
        dataset_ids=[events.DATASET_ID],
        pitch="Turns event-feed records into a short digest for startup/innovation monitoring.",
        items=items,
        metric_label="events shown",
        status="ok" if items else "empty",
    )


def collect_snapshot(*, district: str | None = None, lat: float = toilets.DEFAULT_LAT, lon: float = toilets.DEFAULT_LON) -> dict[str, Any]:
    builders: list[CardBuilder] = [
        tree_card,
        parking_card,
        bike_card,
        pedestrian_card,
        lambda: waste_card(district),
        lambda: toilets_card(lat, lon),
        events_card,
    ]
    cards: list[dict[str, Any]] = []
    for build in builders:
        try:
            cards.append(build())
        except Exception as exc:  # dashboard should show partial data instead of dying mid-demo.
            cards.append({
                "key": getattr(build, "__name__", "unknown"),
                "title": "Dataset fetch failed",
                "icon": "⚠️",
                "folder": "",
                "datasets": [],
                "pitch": "One usecase could not load. Other cards are still usable.",
                "metricLabel": "error",
                "value": "!",
                "status": "error",
                "items": [{"title": type(exc).__name__, "body": str(exc)}],
                "traceback": traceback.format_exc(limit=4),
            })
    return {
        "generatedAt": utc_now_label(),
        "source": "https://opendata.wuerzburg.de/",
        "cards": cards,
    }


MAX_CHAT_CHARS = 12000


def load_env_file(path: Path | None = None) -> None:
    """Load simple KEY=VALUE lines without overriding existing environment variables."""
    env_paths = [path] if path else [ROOT / ".env", Path.home() / "AppData" / "Local" / "hermes" / ".env"]
    for env_path in [p for p in env_paths if p is not None]:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def opendata_context(snapshot: dict[str, Any]) -> str:
    rows: list[str] = [
        f"Generated: {snapshot.get('generatedAt')}",
        f"Source: {snapshot.get('source')}",
    ]
    for card in snapshot.get("cards", []):
        rows.append(f"\n## {card.get('title')} ({card.get('key')})")
        rows.append(f"Purpose: {card.get('pitch')}")
        rows.append(f"Datasets: {', '.join(card.get('datasets') or [])}")
        rows.append(f"Metric: {card.get('value')} {card.get('metricLabel')} | Status: {card.get('status')}")
        if card.get("secondary"):
            rows.append(f"Secondary: {card['secondary'].get('value')} {card['secondary'].get('label')}")
        for item in (card.get("items") or [])[:8]:
            rows.append(
                "- "
                + str(item.get("title", "untitled"))
                + ": "
                + str(item.get("body") or item.get("severity") or "")
                + (f" | timestamp: {item.get('timestamp')}" if item.get("timestamp") else "")
                + (f" | url: {item.get('url')}" if item.get("url") else "")
            )
    text = "\n".join(rows)
    return text[:MAX_CHAT_CHARS]


def build_chat_messages(question: str, snapshot: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are the OpenData Würzburg dashboard assistant. Answer only from the dashboard context below. "
                "Be concise, practical, and honest. If the context does not contain the answer, say that the dashboard does not show it. "
                "Do not invent live values, locations, timestamps, routes, or policy claims. Mention that values come from opendata.wuerzburg.de when useful."
            ),
        },
        {"role": "user", "content": f"Dashboard context:\n{opendata_context(snapshot)}\n\nQuestion: {question}"},
    ]


def ollama_chat_request(question: str, snapshot: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Return the chat endpoint and payload for native Ollama or OpenAI-compatible Ollama Cloud."""
    explicit_api_url = (os.getenv("OLLAMA_API_URL") or "").rstrip("/")
    base_url = (os.getenv("OLLAMA_BASE_URL") or "").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
    messages = build_chat_messages(question, snapshot)

    if explicit_api_url:
        api_url = explicit_api_url
    elif base_url.endswith("/v1") or "/v1/" in base_url:
        api_url = f"{base_url}/chat/completions"
    elif base_url:
        api_url = base_url if base_url.endswith("/api/chat") else f"{base_url}/api/chat"
    elif os.getenv("OLLAMA_API_KEY"):
        api_url = "https://ollama.com/api/chat"
    else:
        api_url = "http://127.0.0.1:11434/api/chat"

    if "/chat/completions" in api_url:
        return api_url, {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": 0.2,
        }
    return api_url, {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.2},
    }


def chat_answer_from_response(result: dict[str, Any]) -> str:
    answer = (result.get("message") or {}).get("content") or result.get("response")
    if not answer and result.get("choices"):
        answer = ((result["choices"][0] or {}).get("message") or {}).get("content")
    if not answer:
        raise RuntimeError(f"Ollama API response did not contain an answer: {result!r}")
    return str(answer).strip()


def chat_with_ollama(question: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    load_env_file()
    api_key = os.getenv("OLLAMA_API_KEY")
    api_url, payload = ollama_chat_request(question, snapshot)
    model = str(payload.get("model") or os.getenv("OLLAMA_MODEL", "gpt-oss:20b"))
    headers = {"Content-Type": "application/json", "User-Agent": "opendata-wuerzburg-dashboard/0.3"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:800]
        raise RuntimeError(f"Ollama API returned HTTP {exc.code}: {body}") from exc
    return {"answer": chat_answer_from_response(result), "model": model, "contextGeneratedAt": snapshot.get("generatedAt")}


DASHBOARD_HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OpenData Würzburg Possibilities — Local Dashboard</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #071016;
      --panel: #101b24;
      --panel2: #132331;
      --muted: #8ea4b8;
      --text: #edf7ff;
      --line: #274052;
      --ok: #3ddc97;
      --watch: #ffbd4a;
      --critical: #ff5d73;
      --blue: #72a7ff;
      --violet: #c084fc;
      --shadow: 0 20px 60px #0008;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 18% 8%, #1c5f74aa 0 20rem, transparent 42rem),
        radial-gradient(circle at 86% 12%, #462379aa 0 18rem, transparent 40rem),
        linear-gradient(180deg, #071016 0%, #09141d 50%, #05090d 100%);
      color: var(--text);
    }
    header {
      padding: 32px clamp(18px, 4vw, 56px) 18px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 20px;
      align-items: end;
    }
    .eyebrow { color: #8ee7ff; font-size: 13px; letter-spacing: .16em; text-transform: uppercase; font-weight: 700; }
    h1 { font-size: clamp(32px, 6vw, 72px); line-height: .92; margin: 8px 0 14px; max-width: 900px; }
    .subtitle { color: #c8d8e7; max-width: 820px; font-size: clamp(16px, 2vw, 20px); line-height: 1.45; margin: 0; }
    .statusBox {
      border: 1px solid var(--line); background: #0b1520cc; border-radius: 22px; padding: 16px 18px; min-width: 245px; box-shadow: var(--shadow);
    }
    .statusBox b { display: block; font-size: 24px; }
    .statusBox span { color: var(--muted); font-size: 13px; }
    .controls {
      margin: 0 clamp(18px, 4vw, 56px) 22px;
      padding: 14px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      border: 1px solid var(--line);
      background: #091620c9;
      border-radius: 20px;
    }
    input, button {
      border: 1px solid #31536a;
      background: #0d1c28;
      color: var(--text);
      border-radius: 12px;
      padding: 10px 12px;
      font: inherit;
    }
    button { cursor: pointer; background: linear-gradient(135deg, #0f766e, #2563eb); border: 0; font-weight: 750; }
    button:hover { filter: brightness(1.15); }
    main {
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 16px;
      padding: 0 clamp(18px, 4vw, 56px) 46px;
    }
    .card {
      grid-column: span 4;
      min-height: 420px;
      position: relative;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 26px;
      background: linear-gradient(180deg, #132433e8, #0c1721f2);
      box-shadow: var(--shadow);
      padding: 20px;
    }
    .card:nth-child(1), .card:nth-child(2) { grid-column: span 6; }
    .card::before {
      content: "";
      position: absolute; inset: -40% -20% auto auto; width: 230px; height: 230px; border-radius: 50%;
      background: radial-gradient(circle, #4cc9f055, transparent 68%); pointer-events: none;
    }
    .top { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; position: relative; }
    .icon { font-size: 34px; width: 58px; height: 58px; display: grid; place-items: center; border-radius: 18px; background: #071018; border: 1px solid #2d485c; }
    h2 { margin: 0; font-size: 22px; }
    .folder { color: var(--blue); font-size: 12px; margin-top: 5px; word-break: break-word; }
    .metric { text-align: right; }
    .metric strong { display: block; font-size: 34px; line-height: .95; }
    .metric span { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
    .pitch { color: #bdd0df; line-height: 1.45; margin: 18px 0; min-height: 44px; position: relative; }
    .datasets { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
    .pill { border: 1px solid #33576f; background: #07131d; color: #9dd6ff; border-radius: 999px; padding: 5px 8px; font-size: 11px; }
    .items { display: grid; gap: 10px; max-height: 215px; overflow: auto; padding-right: 4px; }
    .item { border: 1px solid #233d50; background: #08131c; border-radius: 15px; padding: 11px 12px; }
    .itemTitle { font-weight: 800; margin-bottom: 5px; }
    .itemBody { color: #c6d7e5; font-size: 13px; line-height: 1.35; }
    .timestamp { color: #8499aa; font-size: 12px; margin-top: 5px; }
    .barTrack { height: 8px; background: #071018; border-radius: 999px; overflow: hidden; margin-top: 14px; border: 1px solid #20384a; }
    .bar { height: 100%; width: 0; background: linear-gradient(90deg, var(--ok), var(--blue), var(--violet)); border-radius: inherit; transition: width .5s ease; }
    .status { display: inline-flex; align-items: center; gap: 6px; margin-top: 14px; color: var(--muted); font-size: 13px; }
    .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--ok); box-shadow: 0 0 16px currentColor; }
    .status.critical .dot, .status.error .dot { background: var(--critical); }
    .status.watch .dot { background: var(--watch); }
    .chatPanel {
      margin: 0 clamp(18px, 4vw, 56px) 28px;
      border: 1px solid #31536a;
      background: linear-gradient(180deg, #101f2dcc, #08121bdd);
      border-radius: 26px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .chatHead { display: flex; justify-content: space-between; gap: 16px; padding: 18px 20px; border-bottom: 1px solid #223d50; }
    .chatHead h2 { margin: 0 0 6px; }
    .chatHead p { margin: 0; color: #bdd0df; }
    .chatBadge { color: #8ee7ff; font-size: 12px; text-transform: uppercase; letter-spacing: .1em; white-space: nowrap; }
    .chatLog { display: grid; gap: 10px; max-height: 310px; overflow: auto; padding: 16px 20px; }
    .msg { border: 1px solid #263f52; border-radius: 16px; padding: 12px 14px; line-height: 1.45; white-space: pre-wrap; }
    .msg.user { justify-self: end; max-width: 82%; background: #123655; }
    .msg.assistant { justify-self: start; max-width: 88%; background: #08131c; }
    .msg.error { background: #31121b; border-color: #783248; color: #ffd5dd; }
    .chatForm { display: flex; gap: 10px; padding: 14px 20px 20px; }
    .chatForm input { flex: 1; }
    .errorText { color: #ffb4c0; white-space: pre-wrap; }
    footer { padding: 0 clamp(18px, 4vw, 56px) 35px; color: var(--muted); }
    @media (max-width: 1100px) { .card, .card:nth-child(1), .card:nth-child(2) { grid-column: span 6; } }
    @media (max-width: 760px) { header { grid-template-columns: 1fr; } .card, .card:nth-child(1), .card:nth-child(2) { grid-column: 1 / -1; } }
  </style>
</head>
<body>
  <header>
    <div>
      <div class="eyebrow">localhost demo · Würzburg OpenData</div>
      <h1>OpenData Würzburg Possibilities</h1>
      <p class="subtitle">One live dashboard for the tiny pings: city data is the truth source, Python checks it, Hermes/AI explains or ships the result.</p>
    </div>
    <div class="statusBox">
      <b id="cardCount">—</b>
      <span id="generatedAt">Loading live municipal data…</span>
    </div>
  </header>
  <section class="controls">
    <label>Waste district <input id="district" placeholder="e.g. Grombühl" /></label>
    <label>Latitude <input id="lat" value="49.7939" size="9" /></label>
    <label>Longitude <input id="lon" value="9.9300" size="9" /></label>
    <button id="refresh">Refresh data</button>
  </section>
  <main id="cards"></main>
  <section class="chatPanel">
    <div class="chatHead">
      <div>
        <h2>Ask the OpenData assistant</h2>
        <p>Scoped to the live dashboard snapshot. If the data is not on the page, it should say so.</p>
      </div>
      <div class="chatBadge">Ollama · server-side key</div>
    </div>
    <div id="chatLog" class="chatLog">
      <div class="msg assistant">Ask things like: “Which parking looks risky?”, “Which trees need attention?”, or “Summarize this for a visitor.”</div>
    </div>
    <form id="chatForm" class="chatForm">
      <input id="chatInput" placeholder="Ask about the current OpenData snapshot…" autocomplete="off" />
      <button type="submit">Ask</button>
    </form>
  </section>
  <footer>
    Source: <a href="https://opendata.wuerzburg.de/" style="color:#8ee7ff">opendata.wuerzburg.de</a>. Refresh reruns the local Python collectors; no fake sample data.
  </footer>
<script>
const cardsEl = document.getElementById('cards');
const generatedAt = document.getElementById('generatedAt');
const cardCount = document.getElementById('cardCount');
const chatLog = document.getElementById('chatLog');
const chatInput = document.getElementById('chatInput');
let currentSnapshot = null;
const escapeHtml = (s) => String(s ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const pct = (v) => {
  const n = Number(String(v).replace(/[^0-9.-]/g,''));
  if (!Number.isFinite(n)) return 15;
  return Math.max(8, Math.min(100, Math.log10(Math.max(1, n)) * 24));
};
function renderCard(card) {
  const items = (card.items || []).slice(0, 6).map(item => `
    <div class="item">
      <div class="itemTitle">${escapeHtml(item.title || 'untitled')}</div>
      <div class="itemBody">${escapeHtml(item.body || item.severity || '')}</div>
      ${item.timestamp ? `<div class="timestamp">${escapeHtml(item.timestamp)}</div>` : ''}
      ${item.url ? `<div class="timestamp">${escapeHtml(item.url)}</div>` : ''}
    </div>`).join('') || '<div class="item"><div class="itemBody">No current output from this dataset.</div></div>';
  const pills = (card.datasets || []).map(d => `<span class="pill">${escapeHtml(d)}</span>`).join('');
  const status = escapeHtml(card.status || 'ok');
  return `<article class="card">
    <div class="top">
      <div style="display:flex; gap:14px; min-width:0">
        <div class="icon">${escapeHtml(card.icon || '•')}</div>
        <div><h2>${escapeHtml(card.title)}</h2><div class="folder">${escapeHtml(card.folder || '')}</div></div>
      </div>
      <div class="metric"><strong>${escapeHtml(card.value ?? '—')}</strong><span>${escapeHtml(card.metricLabel || '')}</span></div>
    </div>
    <p class="pitch">${escapeHtml(card.pitch || '')}</p>
    <div class="datasets">${pills}</div>
    <div class="items">${items}</div>
    <div class="barTrack"><div class="bar" style="width:${pct(card.value)}%"></div></div>
    <div class="status ${status}"><span class="dot"></span>${status}${card.secondary ? ` · ${escapeHtml(card.secondary.value)} ${escapeHtml(card.secondary.label)}` : ''}</div>
  </article>`;
}
async function loadData() {
  cardsEl.innerHTML = '<article class="card"><h2>Loading…</h2><p class="pitch">Fetching live OpenData records through local Python.</p></article>';
  const params = new URLSearchParams();
  const district = document.getElementById('district').value.trim();
  const lat = document.getElementById('lat').value.trim();
  const lon = document.getElementById('lon').value.trim();
  if (district) params.set('district', district);
  if (lat) params.set('lat', lat);
  if (lon) params.set('lon', lon);
  const res = await fetch('/api/snapshot?' + params.toString());
  const data = await res.json();
  currentSnapshot = data;
  generatedAt.textContent = 'Generated ' + data.generatedAt;
  cardCount.textContent = `${data.cards.length} live cards`;
  cardsEl.innerHTML = data.cards.map(renderCard).join('');
}
function appendMessage(role, text) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
  return div;
}
async function askChat(question) {
  appendMessage('user', question);
  const pending = appendMessage('assistant', 'Thinking against the current OpenData snapshot…');
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question, snapshot: currentSnapshot})
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Chat request failed');
  pending.textContent = data.answer + `\n\n— ${data.model}, context ${data.contextGeneratedAt}`;
}
document.getElementById('chatForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = chatInput.value.trim();
  if (!question) return;
  chatInput.value = '';
  try {
    if (!currentSnapshot) await loadData();
    await askChat(question);
  } catch (err) {
    appendMessage('error', err.message || String(err));
  }
});
document.getElementById('refresh').addEventListener('click', loadData);
loadData().catch(err => {
  cardsEl.innerHTML = `<article class="card"><h2>Dashboard error</h2><pre class="errorText">${escapeHtml(err.stack || err)}</pre></article>`;
});
</script>
</body>
</html>
'''


def build_static_html(snapshot: dict[str, Any] | None = None) -> str:
    if snapshot is None:
        return DASHBOARD_HTML
    data_literal = json.dumps(snapshot, ensure_ascii=False)
    return DASHBOARD_HTML.replace(
        "loadData().catch(err => {",
        f"window.__STATIC_SNAPSHOT__ = {data_literal};\n"
        "const originalFetch = window.fetch;\n"
        "window.fetch = async (url) => String(url).startsWith('/api/snapshot') ? new Response(JSON.stringify(window.__STATIC_SNAPSHOT__), {headers:{'content-type':'application/json'}}) : originalFetch(url);\n"
        "loadData().catch(err => {",
    )


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib hook name
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send(200, DASHBOARD_HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if parsed.path == "/api/snapshot":
            params = urllib.parse.parse_qs(parsed.query)
            district = params.get("district", [None])[0] or None
            try:
                lat = float(params.get("lat", [toilets.DEFAULT_LAT])[0])
                lon = float(params.get("lon", [toilets.DEFAULT_LON])[0])
            except (TypeError, ValueError):
                self._send(400, b'{"error":"lat/lon must be numeric"}', "application/json; charset=utf-8")
                return
            payload = collect_snapshot(district=district, lat=lat, lon=lon)
            self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802 - stdlib hook name
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/chat":
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(min(length, 65536))
            request = json.loads(body.decode("utf-8"))
            question = str(request.get("question") or "").strip()
            if not question:
                self._send(400, b'{"error":"question is required"}', "application/json; charset=utf-8")
                return
            snapshot = request.get("snapshot") if isinstance(request.get("snapshot"), dict) else collect_snapshot()
            payload = chat_with_ollama(question[:1000], snapshot)
            self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
        except Exception as exc:
            payload = {"error": str(exc)}
            self._send(500, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    url = f"http://{host}:{port}/"
    print(f"OpenData Würzburg dashboard running at {url}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the OpenData Würzburg localhost dashboard.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    run_server(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
