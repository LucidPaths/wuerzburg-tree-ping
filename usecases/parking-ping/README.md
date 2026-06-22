# Parking ping

Usecase: monitor Würzburg parking facility status and produce a quick routing ping.

This is an easy second demo because the OpenData portal exposes near-real-time parking status with human-readable fields:

- `name`
- `status` (`frei`, `belegt`, etc.)
- `values_from`

Run from repo root:

```bash
python usecases/parking-ping/parking_ping.py
python usecases/parking-ping/parking_ping.py --json
```

Telegram direct mode:

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_CHAT_ID="<chat-id>"
python usecases/parking-ping/parking_ping.py --send-telegram
```

Hermes cron watchdog script:

```bash
cd /path/to/wuerzburg-tree-ping && python usecases/parking-ping/parking_ping.py
```

Dataset:

- `parkplatzdaten_wuerzburg`

Demo framing:

> “AI watches public parking telemetry and pings which garages to avoid, with alternatives.”
