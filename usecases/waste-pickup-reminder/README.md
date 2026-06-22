# 🗑️ Waste pickup reminder

    Waste collection reminders by district; staged with --district selection.

    Dataset:

    - `abfallkalender-wuerzburg`

    Run from repo root:

    ```bash
    python usecases/waste-pickup-reminder/waste_pickup_reminder.py
    python usecases/waste-pickup-reminder/waste_pickup_reminder.py --json
    ```

Filter by district:

```bash
python usecases/waste-pickup-reminder/waste_pickup_reminder.py --district Grombühl
```

    Telegram direct mode is staged. Set credentials when available:

    ```bash
    export TELEGRAM_BOT_TOKEN="<bot-token>"
    export TELEGRAM_CHAT_ID="<chat-id>"
    python usecases/waste-pickup-reminder/waste_pickup_reminder.py --send-telegram
    ```

    Hermes cron watchdog script:

    ```bash
    cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/waste-pickup-reminder/waste_pickup_reminder.py
    ```
