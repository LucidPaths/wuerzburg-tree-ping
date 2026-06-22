from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import json
import math
import os
import urllib.parse
import urllib.request

OPEN_DATA_BASE = "https://opendata.wuerzburg.de"


@dataclass(frozen=True)
class PingItem:
    title: str
    body: str
    timestamp: str | None = None
    url: str | None = None


def fetch_records(dataset_id: str, *, limit: int = 20, order_by: str | None = None, where: str | None = None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit}
    if order_by:
        params["order_by"] = order_by
    if where:
        params["where"] = where
    url = f"{OPEN_DATA_BASE}/api/explore/v2.1/catalog/datasets/{dataset_id}/records?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
    req = urllib.request.Request(url, headers={"User-Agent": "opendata-wuerzburg-possibilities/0.2"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    return list(payload.get("results", []))


def utc_now_label() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def render_ping(icon: str, heading: str, items: list[PingItem], *, empty_text: str = "") -> str:
    if not items:
        return empty_text
    lines = [f"{icon} {heading} ({utc_now_label()})"]
    for item in items:
        lines.append("")
        lines.append(f"- {item.title}")
        lines.append(f"  {item.body}")
        if item.timestamp:
            lines.append(f"  Latest: {item.timestamp}")
        if item.url:
            lines.append(f"  Link: {item.url}")
    return "\n".join(lines)


def send_telegram(text: str, token: str | None = None, chat_id: str | None = None) -> None:
    token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required for Telegram delivery")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API rejected message: {payload!r}")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))
