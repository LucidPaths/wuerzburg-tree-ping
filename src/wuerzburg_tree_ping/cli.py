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
DATASETS = {
    "climate_trees": "sls-klimabaeume",
    "garden_soil": "tektelic-kiwi-agriculture-sensor_klimagarten-ochsenfurt",
    "water_barrels": "milesight-em500_klimagarten-ochsenfurt",
    "garden_weather": "barani-helix_klimagarten-ochsenfurt",
}


@dataclass(frozen=True)
class Alert:
    severity: str
    title: str
    body: str
    dataset: str
    timestamp: str | None = None

    def as_text(self) -> str:
        icon = {"critical": "🔴", "warning": "🟠", "info": "ℹ️"}.get(self.severity, "•")
        stamp = f"\nLatest reading: {self.timestamp}" if self.timestamp else ""
        return f"{icon} {self.title}\n{self.body}{stamp}"


def fetch_latest(dataset_id: str, limit: int = 50) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"limit": limit, "order_by": "timestamp desc"})
    url = f"{OPEN_DATA_BASE}/api/explore/v2.1/catalog/datasets/{dataset_id}/records?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "wuerzburg-tree-ping/0.1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    return list(payload.get("results", []))


def _latest_per(records: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    latest: list[dict[str, Any]] = []
    for record in records:
        value = str(record.get(key, ""))
        if not value or value in seen:
            continue
        seen.add(value)
        latest.append(record)
    return latest


def evaluate_climate_trees(records: list[dict[str, Any]], critical_vwc: float = 20, warning_vwc: float = 30) -> list[Alert]:
    alerts: list[Alert] = []
    for record in _latest_per(records, "ss_serialnumber"):
        vwc = record.get("vwc")
        if not isinstance(vwc, (int, float)):
            continue
        place = record.get("originatorname") or record.get("ss_serialnumber") or "unknown tree sensor"
        species = record.get("ss_baumart") or "unknown species"
        if vwc < critical_vwc:
            severity = "critical"
        elif vwc < warning_vwc:
            severity = "warning"
        else:
            continue
        alerts.append(Alert(
            severity=severity,
            title=f"Watering risk: {place}",
            body=f"Tree soil moisture is {vwc:.1f}% VWC for {species}. Check or water if no rain is expected.",
            dataset=DATASETS["climate_trees"],
            timestamp=record.get("timestamp"),
        ))
    return alerts


def evaluate_garden_soil(records: list[dict[str, Any]], critical: float = 12, warning: float = 25) -> list[Alert]:
    alerts: list[Alert] = []
    for record in _latest_per(records, "sensor_id"):
        m30 = record.get("soil_moisture_30")
        m100 = record.get("soil_moisture_100")
        if not isinstance(m30, (int, float)):
            continue
        place = record.get("standort") or record.get("sensor_id") or "unknown soil sensor"
        temp = record.get("temperature_celsius")
        severity = "critical" if m30 < critical else "warning" if m30 < warning else None
        if not severity:
            continue
        deep = f", 100 cm: {m100:.1f}%" if isinstance(m100, (int, float)) else ""
        temp_text = f", air temp: {temp:.1f}°C" if isinstance(temp, (int, float)) else ""
        alerts.append(Alert(
            severity=severity,
            title=f"Dry soil: {place}",
            body=f"Soil moisture at 30 cm is {m30:.1f}%{deep}{temp_text}. Recommend watering review.",
            dataset=DATASETS["garden_soil"],
            timestamp=record.get("timestamp"),
        ))
    return alerts


def evaluate_water_barrels(records: list[dict[str, Any]], low_percent: float = 25) -> list[Alert]:
    alerts: list[Alert] = []
    for record in _latest_per(records, "sensor_id"):
        level = record.get("level_percent")
        if not isinstance(level, (int, float)) or level >= low_percent:
            continue
        place = record.get("standort") or record.get("sensor_id") or "unknown barrel"
        alerts.append(Alert(
            severity="warning",
            title=f"Water storage low: {place}",
            body=f"Water barrel is at {level:.0f}%. Refill soon if it is used for irrigation.",
            dataset=DATASETS["water_barrels"],
            timestamp=record.get("timestamp"),
        ))
    return alerts


def build_alerts() -> list[Alert]:
    alerts: list[Alert] = []
    alerts.extend(evaluate_climate_trees(fetch_latest(DATASETS["climate_trees"])))
    alerts.extend(evaluate_garden_soil(fetch_latest(DATASETS["garden_soil"])))
    alerts.extend(evaluate_water_barrels(fetch_latest(DATASETS["water_barrels"])))
    return sorted(alerts, key=lambda a: {"critical": 0, "warning": 1, "info": 2}.get(a.severity, 9))


def render_alerts(alerts: list[Alert], max_alerts: int = 8) -> str:
    if not alerts:
        return ""
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    chunks = [f"🌳 Würzburg OpenData watering ping ({generated})"]
    chunks.extend(alert.as_text() for alert in alerts[:max_alerts])
    if len(alerts) > max_alerts:
        chunks.append(f"…and {len(alerts) - max_alerts} more sensor alert(s).")
    return "\n\n".join(chunks)


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
    send = "--send-telegram" in argv
    json_mode = "--json" in argv
    alerts = build_alerts()
    if json_mode:
        print(json.dumps([alert.__dict__ for alert in alerts], ensure_ascii=False, indent=2))
        return 0
    text = render_alerts(alerts)
    if text:
        if send:
            send_telegram(text)
        else:
            print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
