# Tree watering ping

Usecase: monitor Würzburg tree/garden soil-moisture and water-level sensors.

Run from repo root:

```bash
python usecases/tree-watering-ping/tree_watering_ping.py
python usecases/tree-watering-ping/tree_watering_ping.py --json
```

Telegram direct mode:

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_CHAT_ID="<chat-id>"
python usecases/tree-watering-ping/tree_watering_ping.py --send-telegram
```

Hermes cron watchdog script:

```bash
cd /path/to/wuerzburg-tree-ping && python usecases/tree-watering-ping/tree_watering_ping.py
```

Empty stdout means no alert. Non-empty stdout is the ping.

Datasets:

- `sls-klimabaeume`
- `tektelic-kiwi-agriculture-sensor_klimagarten-ochsenfurt`
- `milesight-em500_klimagarten-ochsenfurt`
