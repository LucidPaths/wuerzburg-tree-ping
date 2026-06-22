# 🚶 Downtown pedestrian pulse

Pedestrian counts for city-center locations; answers “how busy is downtown?”

Dataset:

- `passantenzaehlung_tagesdaten`

Run from repo root:

```bash
python usecases/pedestrian-downtown-pulse/pedestrian_downtown_pulse.py
python usecases/pedestrian-downtown-pulse/pedestrian_downtown_pulse.py --json
```

Telegram direct mode is staged. Set credentials when available:

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_CHAT_ID="<chat-id>"
python usecases/pedestrian-downtown-pulse/pedestrian_downtown_pulse.py --send-telegram
```

Hermes cron watchdog script:

```bash
cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/pedestrian-downtown-pulse/pedestrian_downtown_pulse.py
```
