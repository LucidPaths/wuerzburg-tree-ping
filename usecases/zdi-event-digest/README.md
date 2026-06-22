# 📅 ZDI event digest

Startup/tech event feed digest; notes stale-feed fallback when no upcoming events exist.

Dataset:

- `eventfeed`

Run from repo root:

```bash
python usecases/zdi-event-digest/zdi_event_digest.py
python usecases/zdi-event-digest/zdi_event_digest.py --json
```

Telegram direct mode is staged. Set credentials when available:

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_CHAT_ID="<chat-id>"
python usecases/zdi-event-digest/zdi_event_digest.py --send-telegram
```

Hermes cron watchdog script:

```bash
cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/zdi-event-digest/zdi_event_digest.py
```
