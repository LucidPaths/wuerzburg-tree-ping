# Würzburg Tree Ping

Tiny demo monitor for Würzburg OpenData tree, soil-moisture, and water-level sensors.

It supports two modes:

1. **Plain Python + Telegram bot** — run the script yourself and send directly through Telegram.
2. **Hermes cronjob** — let Hermes schedule the script and deliver non-empty output to Telegram/Discord.

The clean boundary is: **Python does truth; Hermes does scheduling, interpretation, and delivery.**

## Data sources

Verified OpenData portal: <https://opendata.wuerzburg.de/>

API base:

```text
https://opendata.wuerzburg.de/api/explore/v2.1/catalog/datasets
```

Datasets used:

| Dataset ID | Purpose |
| --- | --- |
| `sls-klimabaeume` | Würzburger Klimabäume soil moisture / VWC |
| `tektelic-kiwi-agriculture-sensor_klimagarten-ochsenfurt` | Garden soil moisture at 30 cm / 100 cm |
| `milesight-em500_klimagarten-ochsenfurt` | Water barrel fill level |
| `barani-helix_klimagarten-ochsenfurt` | Weather context, currently documented for extension |

## Quick start

```bash
git clone https://github.com/LucidPaths/wuerzburg-tree-ping.git
cd wuerzburg-tree-ping
python -m venv .venv
. .venv/bin/activate  # Windows git-bash
pip install -e .
wuerzburg-tree-ping
```

No output means no alert. That is intentional: cron can stay quiet when everything is fine.

JSON/debug mode:

```bash
wuerzburg-tree-ping --json
```

## Telegram direct mode

Create a Telegram bot with BotFather, get the chat ID, then:

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_CHAT_ID="<chat-id>"
wuerzburg-tree-ping --send-telegram
```

Secrets stay in environment variables. Do **not** commit them.

## Hermes cron mode

Recommended for a local Hermes demo because Hermes already has gateway delivery.

Create a cron job that runs the script only, and sends stdout when alerts exist:

```bash
hermes cron create 'every 1h'
```

Prompt/script shape:

```text
Run the Würzburg tree ping monitor. Deliver any non-empty output as the alert. Stay silent if stdout is empty.
```

Script:

```bash
cd /path/to/wuerzburg-tree-ping && python -m wuerzburg_tree_ping.cli
```

If creating from inside Hermes with the `cronjob` tool, use `no_agent=True` for a pure watchdog. Empty stdout = silent, non-empty stdout = delivered.

## Example ping

```text
🌳 Würzburg OpenData watering ping (2026-06-22 09:30 UTC)

🔴 Dry soil: Ahorn
Soil moisture at 30 cm is 3.5%, 100 cm: 3.8%, air temp: 29.3°C. Recommend watering review.
Latest reading: 2026-06-22T09:19:54+00:00
```

## Development

```bash
python -m pytest
python -m wuerzburg_tree_ping.cli --json
```

## Notes for the event

Good demo script:

1. Show the public OpenData source.
2. Show the dataset IDs and the live JSON fields.
3. Run the local monitor.
4. Show the Telegram/Hermes ping.
5. Ask Hermes: “why did this trigger?” or “show me the driest locations.”

This keeps the demo grounded: AI explains and prioritizes, but the municipal data decides.
