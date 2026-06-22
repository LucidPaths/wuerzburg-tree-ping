# 🚲 Bike counter pulse

Daily bike counts by station; answers “which routes are busiest?”

Dataset:

- `fahrradzaehlung-tagesdaten-alle-zaehlstationen`

Run from repo root:

```bash
python usecases/bike-counter-pulse/bike_counter_pulse.py
python usecases/bike-counter-pulse/bike_counter_pulse.py --json
```

Telegram direct mode is staged. Set credentials when available:

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_CHAT_ID="<chat-id>"
python usecases/bike-counter-pulse/bike_counter_pulse.py --send-telegram
```

Hermes cron watchdog script:

```bash
cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/bike-counter-pulse/bike_counter_pulse.py
```
