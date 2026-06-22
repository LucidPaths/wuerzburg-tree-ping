from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import json
import os
import sys
import urllib.parse
import urllib.request

OPEN_DATA_BASE = "https://opendata.wuerzburg.de"
DATASET_ID = "parkplatzdaten_wuerzburg"


@dataclass(frozen=True)
class ParkingStatus:
    name: str
    status: str
    values_from: str | None = None


def fetch_latest(limit: int = 80) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"limit": limit, "order_by": "values_from desc"})
    url = f"{OPEN_DATA_BASE}/api/explore/v2.1/catalog/datasets/{DATASET_ID}/records?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "wuerzburg-parking-ping/0.1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    return list(payload.get("results", []))


def latest_per_parking(records: list[dict[str, Any]]) -> list[ParkingStatus]:
    seen: set[int | str] = set()
    latest: list[ParkingStatus] = []
    for record in records:
        parking_id = record.get("id") or record.get("name")
        if parking_id in seen:
            continue
        seen.add(parking_id)
        latest.append(ParkingStatus(
            name=str(record.get("name") or parking_id),
            status=str(record.get("status") or "unknown"),
            values_from=record.get("values_from"),
        ))
    return latest


def summarize(statuses: list[ParkingStatus]) -> str:
    if not statuses:
        return ""
    blocked = [s for s in statuses if s.status.lower() in {"belegt", "fast voll", "voll"}]
    free = [s for s in statuses if s.status.lower() == "frei"]
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"🅿️ Würzburg parking ping ({generated})"]
    if blocked:
        lines.append("Avoid / check before driving:")
        for status in blocked:
            lines.append(f"- {status.name}: {status.status} ({status.values_from or 'no timestamp'})")
    else:
        lines.append("No parking facilities are currently marked occupied in the latest sample.")
    if free:
        lines.append("Likely available options:")
        for status in free[:5]:
            lines.append(f"- {status.name}: {status.status}")
    return "\n".join(lines)


def build_ping() -> str:
    return summarize(latest_per_parking(fetch_latest()))


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


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    statuses = latest_per_parking(fetch_latest())
    if "--json" in argv:
        print(json.dumps([status.__dict__ for status in statuses], ensure_ascii=False, indent=2))
        return 0
    text = summarize(statuses)
    if "--send-telegram" in argv:
        send_telegram(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
