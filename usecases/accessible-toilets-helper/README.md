# ♿ Accessible toilets helper

    Nearest accessible toilets from a supplied or default location.

    Dataset:

    - `barrierefreie-toiletten-im-stadtgebiet-wuerzburg`

    Run from repo root:

    ```bash
    python usecases/accessible-toilets-helper/accessible_toilets_helper.py
    python usecases/accessible-toilets-helper/accessible_toilets_helper.py --json
    ```

Use a specific location:

```bash
python usecases/accessible-toilets-helper/accessible_toilets_helper.py --lat 49.7939 --lon 9.9300
```

    Telegram direct mode is staged. Set credentials when available:

    ```bash
    export TELEGRAM_BOT_TOKEN="<bot-token>"
    export TELEGRAM_CHAT_ID="<chat-id>"
    python usecases/accessible-toilets-helper/accessible_toilets_helper.py --send-telegram
    ```

    Hermes cron watchdog script:

    ```bash
    cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/accessible-toilets-helper/accessible_toilets_helper.py
    ```
